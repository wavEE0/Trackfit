from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import transaction
from .models import UserProfile, DailyIntake, BodyGoal, Meal, Food
from nutrition.nutri_guide import NutriGuide

def recommendation(request):
    context = {
        "session": request.session.get("user")
    }
    
    # Ensure the user_profile, bodygoal, and associated data is always added to the context if they exist
    user_profile = UserProfile.objects.filter(user=request.user).first()
    if user_profile:
        context['user_profile_filled'] = True
        context['user_profile'] = user_profile
        nutri_guide = NutriGuide(user_profile)
        context['bmr'] = nutri_guide.get_bmr()
        context['maintenance_calories'] = nutri_guide.get_maintenance()
        
        body_goal = BodyGoal.objects.filter(user=user_profile.user).first()
        if body_goal:
            context['body_goal_filled'] = True
            context['body_goal'] = body_goal
            context['recommended_calories'] = nutri_guide.get_rcm_cal()
        else: 
            context['body_goal_filled'] = False
    else:
        context['user_profile_filled'] = False
        context['body_goal_filled'] = False
        
    # Handling all forms done together due to closely-coupled data
    if request.method == 'POST':
        action = request.POST.get('action')

        # User Profile form submission
        if action == 'save_user_profile':
            # Create new instance
            if not user_profile:
                user_profile = UserProfile(user=request.user)
            # Update and save UserProfile data
            user_profile.age = int(request.POST.get('age'))
            user_profile.gender = request.POST.get('gender')
            user_profile.height = float(request.POST.get('height'))
            user_profile.weight = float(request.POST.get('weight'))
            user_profile.activity_level = request.POST.get('activity_level')
            user_profile.save()

            # User Profile and calculations data added to context
            context['user_profile_filled'] = True
            context['user_profile'] = user_profile

            nutri_guide = NutriGuide(user_profile)
            context['bmr'] = nutri_guide.get_bmr()
            context['maintenance_calories'] = nutri_guide.get_maintenance()

        elif action == 'reset_user_profile':
            if user_profile:
                user_profile.delete()
            context["user_profile_filled"] = False
            
            # BodyGoal resets with User Profile
            if body_goal:
                body_goal.delete()
            context['body_goal_filled'] = False

        # Body Goals form submission
        elif action == 'save_body_goal':
            # Get body goal inputs
            category = request.POST.get('category')
            level = request.POST.get('level', None)
            target_weight = request.POST.get('target_weight', None)
            goal_date = request.POST.get('goal_date', None)
            
            body_goal, created = BodyGoal.objects.update_or_create(
                user=request.user,
                # Properties updates based on category CUSTOM or else
                defaults={
                    'category': category,
                    'level': None if category == 'CU' else level,
                    'target_weight': target_weight if category == 'CU' else None,
                    'goal_date': goal_date if category == 'CU' else None
                }
            )
            context['body_goal_filled'] = True
            context['body_goal'] = body_goal

            # Calculate recommendation with User Profile data (shared user_id with BodyGoal)
            if user_profile:
                nutri_guide = NutriGuide(user_profile)
                context['recommended_calories'] = nutri_guide.get_rcm_cal()
        
        elif action == 'reset_body_goal':
            if body_goal:
                body_goal.delete()
            context['body_goal_filled'] = False

    return render(request, 'recommendation.html', context)


def tracking(request):
    user = request.user
    today = timezone.now().date()

    # User specific
    custom_meals = Meal.objects.filter(user=user)
    custom_foods = Food.objects.filter(user=user)
    daily_intake = DailyIntake.objects.filter(user=user, date=today).first()
    enriched_meals = []

    if daily_intake:
        meals_with_quantity = daily_intake.intakemeal_set.all().select_related('meal')

        # Attach quantity to each meal object
        for intake_meal in meals_with_quantity:
            meal = intake_meal.meal
            meal.quantity = intake_meal.quantity
            enriched_meals.append(meal)

    # Generic
    all_meals = Meal.objects.filter()
    all_foods = Food.objects.filter()

    context = {
        "session": request.session.get("user"),
        'today_intake': daily_intake,
        'intake_meals': enriched_meals,
        'custom_meals': custom_meals,
        'custom_foods': custom_foods,
        'all_meals': all_meals,
        'all_foods': all_foods,
        'date': today
    }
    return render(request, 'tracking.html', context)

@require_POST
def add_daily_intake(request):
    user = request.user
    today = timezone.now().date()
    meal_ids = request.POST.getlist('selected_meals')
    
    daily_intake, created = DailyIntake.objects.get_or_create(user=user, date=today)
    selected_meals = Meal.objects.filter(id__in=meal_ids)
    for meal in selected_meals:
        daily_intake.add_meal(meal)
    
    return redirect('tracking')

@require_POST
def remove_daily_intake(request):
    user = request.user
    meal_id = request.POST.get('item_id')

    # If not using a specific date, just use the latest intake for the user.
    daily_intake = DailyIntake.objects.filter(user=user).latest('date')
    meal = get_object_or_404(Meal, id=meal_id)
    
    daily_intake.remove_meal(meal)

    return redirect('tracking')

@require_POST
def add_custom_meal(request):
    user = request.user
    meal_name = request.POST.get('meal_name')
    selected_food_ids = request.POST.getlist('selected_foods')

    with transaction.atomic():
        new_meal = Meal.objects.create(name=meal_name, user=user)

        for food_id in selected_food_ids:
            print(food_id)
            quantity_key = f'quantity_{food_id}'
            if quantity_key in request.POST:
                quantity = request.POST.get(quantity_key)
                print(quantity)
                try:
                    food = Food.objects.get(id=food_id)
                    new_meal.add_food(food, float(quantity))
                except Food.DoesNotExist:
                    continue

    return redirect('tracking')

@require_POST
def remove_custom_meal(request):
    meal_id = request.POST.get('item_id')
    # Check meal belongs to requesting user before deleting
    meal = get_object_or_404(Meal, id=meal_id, user=request.user)
    
    meal.delete()

    return redirect('tracking')

@require_POST
def add_custom_food(request):
    if request.method == "POST":
        # Retrieve form data
        name = request.POST.get("food_name")
        category = request.POST.get("food_category")
        calories = request.POST.get("food_calories")
        protein = request.POST.get("food_protein")
        carbohydrates = request.POST.get("food_carbohydrates")
        sugar = request.POST.get("food_sugar")
        fats = request.POST.get("food_fats")
        fiber = request.POST.get("food_fiber")
        sodium = request.POST.get("food_sodium")

        # Create a new Food instance and save to the database
        food = Food(
            name=name,
            user=request.user,
            category=category,
            calories=calories,
            protein=protein,
            carbohydrates=carbohydrates,
            sugar=sugar if sugar else None,  # Handle optional fields
            fats=fats,
            fiber=fiber if fiber else None,
            sodium=sodium if sodium else None,
        )
        food.save()
        
    return redirect('tracking')

@require_POST
def remove_custom_food(request):
    food_id = request.POST.get('item_id')
    # Check meal belongs to requesting user before deleting
    food = get_object_or_404(Food, id=food_id, user=request.user)
    
    food.delete()

    return redirect('tracking')