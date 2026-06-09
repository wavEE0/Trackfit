from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.db.models import F

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    age = models.IntegerField()  # Allow null and blank values
    gender = models.CharField(max_length=30)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    activity_level = models.CharField(max_length=50)

    def __str__(self):
        return self.user.username
    
    # Method to calculate BMI
    def get_bmi(self):
        height_in_meters = self.height / 100
        bmi = float(self.weight) / (height_in_meters ** 2)
        return bmi

    # Method to calculate body fat percentage using the BMI method
    def get_bfp(self):
        bmi = self.get_bmi()
        if self.gender.lower() == 'male':
            body_fat_percentage = (1.20 * bmi) + (0.23 * self.age) - 16.2
        elif self.gender.lower() == 'female':
            body_fat_percentage = (1.20 * bmi) + (0.23 * self.age) - 5.4
        else:
            raise ValueError("Gender not recognized. Please use 'male' or 'female'.")
        return body_fat_percentage

class BodyGoal(models.Model):
    # Constants for categories of goals
    WEIGHT_LOSS = 'WL'
    MUSCLE_BUILDING = 'MB'
    FAT_LOSS = 'FL'
    ENDURANCE_IMPROVEMENT = 'EI'
    FLEXIBILITY_BALANCE = 'FB'
    STRENGTH_BUILDING = 'SB'
    CUSTOM = 'CU'
    CATEGORY_CHOICES = [
        (WEIGHT_LOSS, 'Weight Loss'),
        (MUSCLE_BUILDING, 'Muscle Building'),
        (FAT_LOSS, 'Fat Loss'),
        (ENDURANCE_IMPROVEMENT, 'Endurance Improvement'),
        (FLEXIBILITY_BALANCE, 'Flexibility and Balance'),
        (STRENGTH_BUILDING, 'Strength Building'),
        (CUSTOM, 'Custom'),  # When targets are filled out manually
    ]

    # Constants for levels of chosen category
    MILD = 'Mild'
    AVERAGE = 'Average'
    EXTREME = 'Extreme'
    CUSTOM_LEVEL = 'Custom'
    LEVEL_CHOICES = [
        (MILD, 'Mild'),
        (AVERAGE, 'Average'),
        (EXTREME, 'Extreme'),
        (CUSTOM_LEVEL, 'Custom'),  # When targets are filled out manually
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, null=True)
    level = models.CharField(max_length=7, choices=LEVEL_CHOICES, default=MILD, null=True)
    
    # Advnaced options for specific goals
    target_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    goal_date = models.DateField(null=True, blank=True)

    def is_advanced_goal(self):
        return self.category == self.CUSTOM

    def __str__(self):
        if self.is_advanced_goal():
            # Display for advanced/specific goals
            return f"{self.user.username}'s Advanced Body Goal: {self.get_targets_display()}"
        else:
            # Display for basic category goals
            category_display = self.get_category_display() if self.category else 'None'
            level_display = self.get_level_display()
            return f"{self.user.username}'s Body Goal: {category_display} ({level_display})"

class Food(models.Model):
    CATEGORY_CHOICES = [
        ('FR', 'Fruits'),
        ('VG', 'Vegetables'),
        ('GR', 'Grains'),
        ('MT', 'Meats'),
        ('DA', 'Dairy'),
        ('FT', 'Fats and Oils'),
        ('SW', 'Sweets'),
        ('BV', 'Beverages'),
        ('OT', 'Others'),
    ]

    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='foods', null=True, blank=True)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    calories = models.DecimalField(max_digits=6, decimal_places=2)
    protein = models.DecimalField(max_digits=5, decimal_places=2)
    carbohydrates = models.DecimalField(max_digits=5, decimal_places=2)
    sugar = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fats = models.DecimalField(max_digits=5, decimal_places=2)
    fiber = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sodium = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Meal(models.Model):
    name = models.CharField(max_length=100)
    foods = models.ManyToManyField(Food, through='MealItem')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='meals', null=True, blank=True)

    def add_food(self, food, quantity):
        meal_item, created = self.mealitem_set.get_or_create(food=food, defaults={'quantity': quantity})
        if not created:
            meal_item.quantity += quantity
            meal_item.save()

    def __str__(self):
        return self.name
    
    def id(self):
        return self.id

    def calories(self):
        return sum([item.food.calories * item.quantity for item in self.mealitem_set.all()])
    
    def protein(self):
        total_protein = sum([meal_food.food.protein * meal_food.quantity for meal_food in self.mealitem_set.all()])
        return total_protein

    def carbohydrates(self):
        total_carbs = sum([meal_food.food.carbohydrates * meal_food.quantity for meal_food in self.mealitem_set.all()])
        return total_carbs

    def fats(self):
        total_fats = sum([meal_food.food.fats * meal_food.quantity for meal_food in self.mealitem_set.all()])
        return total_fats
    
    def ingredients_list(self):
        return [{'name': item.food.name, 'quantity': item.quantity} for item in self.mealitem_set.all()]


class MealItem(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.food.name} x {self.quantity}"

    
class IntakeMeal(models.Model):
    daily_intake = models.ForeignKey('DailyIntake', on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class DailyIntake(models.Model):
    date = models.DateField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dailyIntake')
    meals = models.ManyToManyField(Meal, through='IntakeMeal')

    def add_meal(self, meal, quantity=1):
        # Check if the meal already exists in this intake
        intake_meal, created = IntakeMeal.objects.get_or_create(
            daily_intake=self,
            meal=meal,
            defaults={'quantity': quantity}
        )
        # If exists, increment the quantity
        if not created:
            intake_meal.quantity += quantity
            intake_meal.save()

    def remove_meal(self, meal, quantity=1):
        """
        Removes a specified quantity of a meal from the daily intake.
        If the resulting quantity is zero or less, the meal is removed from the intake.
        """
        try:
            intake_meal = self.intakemeal_set.get(meal=meal)
            intake_meal.quantity = F('quantity') - quantity  # F() to avoid race conditions
            intake_meal.save()

            # Refresh DB to check updated quantity
            intake_meal.refresh_from_db()

            if intake_meal.quantity <= 0:
                intake_meal.delete()  # Removes the meal
        except IntakeMeal.DoesNotExist:
            pass

    def get_meal_quantity(self, meal_id):
        intake_meal = self.intakemeal_set.filter(meal_id=meal_id).first()
        return intake_meal.quantity if intake_meal else 0

    def protein(self):
        return sum(meal.protein() for meal in self.meals.all())

    def carbohydrates(self):
        return sum(meal.carbohydrates() for meal in self.meals.all())

    def fats(self):
        return sum(meal.fats() for meal in self.meals.all())

    def calories(self):
        return sum(meal.calories() for meal in self.meals.all())

    def __str__(self):
        return f"{self.user}'s intake on {self.date}"

