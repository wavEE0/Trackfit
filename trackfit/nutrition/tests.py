from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta
from .models import UserProfile, BodyGoal, Food, Meal, MealItem, DailyIntake
from nutrition.nutri_guide import NutriGuide


class UserProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("john", "john@example.com", "johnpassword")
        self.user_profile = UserProfile.objects.create(user=self.user, age=25, gender="male", height=180, weight=80, activity_level="active")

    def test_bmi(self):
        self.assertAlmostEqual(self.user_profile.get_bmi(), float(self.user_profile.weight)/((float(self.user_profile.height)/100)**2), places=2)

    def test_bfp_male(self):
        self.assertAlmostEqual(self.user_profile.get_bfp(), (1.20*self.user_profile.get_bmi())+(0.23*self.user_profile.age)-16.2, places=2)

    def test_bfp_female(self):
        self.user_profile.gender = "female"; self.user_profile.save()
        self.assertAlmostEqual(self.user_profile.get_bfp(), (1.20*self.user_profile.get_bmi())+(0.23*self.user_profile.age)-5.4, places=2)


class BodyGoalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "password")

    def test_get_targets_display_with_all_targets(self):
        bg = BodyGoal.objects.create(user=self.user, category=BodyGoal.CUSTOM,
            target_weight=75, target_body_fat_percentage=15, target_muscle_mass=10, target_bmi=22)
        self.assertEqual(bg.get_targets_display(), "Weight: 75 kg, Body Fat: 15%, Muscle Mass: 10 kg, BMI: 22")

    def test_get_targets_display_with_partial_targets(self):
        bg = BodyGoal.objects.create(user=self.user, category=BodyGoal.CUSTOM, target_weight=80, target_body_fat_percentage=20)
        self.assertEqual(bg.get_targets_display(), "Weight: 80 kg, Body Fat: 20%")


class NutriGuideTests(TestCase):
    def setUp(self):
        self.user_male = User.objects.create_user("ethan", "ethan@email.com", "ethan123")
        self.user_profile_male = UserProfile.objects.create(user=self.user_male, age=25, gender="male", height=180, weight=75, activity_level="sedentary")
        self.user_female = User.objects.create_user("sara", "sara@zmail.com", "sara123")
        self.user_profile_female = UserProfile.objects.create(user=self.user_female, age=25, gender="female", height=165, weight=60, activity_level="active")

    def test_bmr_calculator_male(self):
        ng = NutriGuide(self.user_profile_male)
        self.assertAlmostEqual(ng.get_bmr(), (9.99*self.user_profile_male.weight)+(6.25*self.user_profile_male.height)-(4.92*self.user_profile_male.age)+5, places=2)

    def test_bmr_calculator_female(self):
        ng = NutriGuide(self.user_profile_female)
        self.assertAlmostEqual(ng.get_bmr(), (9.99*self.user_profile_female.weight)+(6.25*self.user_profile_female.height)-(4.92*self.user_profile_female.age)-161, places=2)

    def test_maintenance_calories_male_sedentary(self):
        ng = NutriGuide(self.user_profile_male)
        self.assertAlmostEqual(ng.get_maintenance(), ng.get_bmr()*1.2, places=2)

    def test_maintenance_calories_female_active(self):
        ng = NutriGuide(self.user_profile_female)
        self.assertAlmostEqual(ng.get_maintenance(), ng.get_bmr()*1.725, places=2)

    def test_rcm_cal_no_goals(self):
        ng = NutriGuide(self.user_profile_male)
        self.assertAlmostEqual(ng.get_rcm_cal(), ng.get_maintenance(), places=2)

    def test_rcm_cal_wl_mild(self):
        ng = NutriGuide(self.user_profile_male)
        BodyGoal.objects.create(user=self.user_male, category=BodyGoal.WEIGHT_LOSS, level=BodyGoal.MILD,
            goal_date=date.today()+timedelta(weeks=4), target_weight=75)
        self.assertAlmostEqual(ng.get_rcm_cal(), ng.get_maintenance()*0.85, places=2)

    def test_rcm_cal_mb_extreme(self):
        ng = NutriGuide(self.user_profile_female)
        BodyGoal.objects.create(user=self.user_female, category=BodyGoal.MUSCLE_BUILDING, level=BodyGoal.EXTREME,
            goal_date=date.today()+timedelta(weeks=4), target_weight=85)
        self.assertAlmostEqual(ng.get_rcm_cal(), ng.get_maintenance()*1.15, places=2)

    def test_calc_adv_cal_target_weight(self):
        # Fixed: original test referenced undefined self.user and self.nutri_guide,
        # and called calc_adv_cal() which does not exist.
        ng = NutriGuide(self.user_profile_male)
        target_weight = Decimal("70")
        BodyGoal.objects.create(user=self.user_male, category=BodyGoal.CUSTOM,
            target_weight=target_weight, goal_date=date.today()+timedelta(days=30))
        maintenance  = ng.get_maintenance()
        weight_diff  = float(target_weight) - float(self.user_profile_male.weight)
        adjustment   = max(min((weight_diff * 500) / 7, 1000), -1000)
        self.assertAlmostEqual(float(ng.get_rcm_cal()), round(float(maintenance)+adjustment, 0), places=0)


class FoodTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.food = Food.objects.create(user=self.user, name="Apple", category="FR",
            calories=Decimal("52.00"), protein=Decimal("0.26"),
            carbohydrates=Decimal("13.81"), sugar=Decimal("10.39"),
            fats=Decimal("0.17"), fiber=Decimal("2.4"), sodium=Decimal("1"))

    def test_food_creation(self):
        self.assertEqual(self.food.name, "Apple")
        self.assertEqual(self.food.user.username, "testuser")


class MealTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.meal = Meal.objects.create(name="Breakfast", user=self.user)
        apple = Food.objects.create(user=self.user, name="Apple", category="FR",
            calories=Decimal("52.00"), protein=Decimal("0.26"),
            carbohydrates=Decimal("13.81"), fats=Decimal("0.17"))
        MealItem.objects.create(meal=self.meal, food=apple, quantity=Decimal("2"))

    def test_meal_total_calories(self):
        self.assertEqual(self.meal.total_calories(), Decimal("104.00"))


class DailyIntakeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.meal = Meal.objects.create(name="Breakfast", user=self.user)
        self.daily_intake = DailyIntake.objects.create(date=date.today(), user=self.user)
        self.daily_intake.meals.add(self.meal)

    def test_daily_intake_association(self):
        self.assertIn(self.meal, self.daily_intake.meals.all())
