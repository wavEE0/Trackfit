import json
from authlib.integrations.django_client import OAuth
from django.contrib.auth import login as auth_login
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from .models import User, UserOAuthInfo
from nutrition.models import Meal, Food, DailyIntake, UserProfile, BodyGoal
from nutrition.nutri_guide  import NutriGuide
from django.utils import timezone
from datetime import timedelta

# Code below sourced from Auth0 API and altered
oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

def login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )

def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    userinfo = token.get('userinfo')

    if userinfo:
        email = userinfo['email']
        user, created = User.objects.get_or_create(email=email, defaults={'username': email})

        auth_login(request, user)
        
        # OAuth tokens saved
        access_token = token.get('access_token')
        expires_in = token.get('expires_in')
        expiry_date = timezone.now() + timedelta(seconds=expires_in) if expires_in else None
        refresh_token = token.get('refresh_token')
        if refresh_token is None:
            refresh_token = ""

        UserOAuthInfo.objects.update_or_create(
            user=user,
            defaults={
            'oauth_provider': 'auth0',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expiry_date': expiry_date,
            }
        )

        request.session["user"] = token

        return redirect(request.build_absolute_uri(reverse("dashboard")))

    return redirect('error_page')

def logout(request):
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

def index(request):
    user_session = request.session.get("user")
    return render(
        request,
        "index.html",
        context={
            "session": user_session,
            "pretty": json.dumps(user_session, indent=4),
        },
    )

def dashboard(request):
    user = request.user  # Assuming authentication is handled and user is logged in
    today = timezone.now().date()

    # Nutrition Tracking view reused to access data
    # Fetch user-specific data
    daily_intake = DailyIntake.objects.filter(user=user, date=today).first()
    custom_meals = Meal.objects.filter(user=user)
    custom_foods = Food.objects.filter(user=user)

    # Prepare enriched meals list if daily intake is present
    enriched_meals = []
    if daily_intake:
        meals_with_quantity = daily_intake.intakemeal_set.all().select_related('meal')
        for intake_meal in meals_with_quantity:
            meal = intake_meal.meal
            meal.quantity = intake_meal.quantity  # Attach quantity for display
            enriched_meals.append(meal)

    # Generic meals and foods (if needed, filter these according to your business logic)
    all_meals = Meal.objects.all()
    all_foods = Food.objects.all()


    # Fetch the user's profile and body goal
    user_profile = UserProfile.objects.filter(user=user).first()
    body_goal = BodyGoal.objects.filter(user=user).first()

    if user_profile:
        # Create an instance of NutriGuide with the user's profile
        nutri_guide = NutriGuide(user_profile)

        # Get BMR and Maintenance Calories
        bmr = nutri_guide.get_bmr()
        maintenance_calories = nutri_guide.get_maintenance()

        # Get recommended calories based on the body goal
        recommended_calories = nutri_guide.get_rcm_cal() if body_goal else maintenance_calories
    else:
        bmr = maintenance_calories = recommended_calories = None

    # Prepare the context with all necessary data
    context = {
        "session": request.session.get("user"),  # Include any session data if needed
        "today_intake": daily_intake,
        "intake_meals": enriched_meals,
        "custom_meals": custom_meals,
        "custom_foods": custom_foods,
        "all_meals": all_meals,
        "all_foods": all_foods,
        "user_profile": user_profile,
        "body_goal": body_goal,
        "bmr": bmr,
        "maintenance_calories": maintenance_calories,
        "recommended_calories": recommended_calories,
        "pretty": json.dumps(request.session.get("user"), indent=4) if request.session.get("user") else "No session data",
    }

    return render(request, "dashboard.html", context)
