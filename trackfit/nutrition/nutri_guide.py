from datetime import date
from .models import UserProfile, BodyGoal
from decimal import Decimal

class NutriGuide:
    def __init__(self, user_profile):
        self.user_profile = user_profile
    
    def get_bmr(self):
        weight = self.user_profile.weight
        height = self.user_profile.height
        age = self.user_profile.age
        gender = self.user_profile.gender

        if gender.lower() == 'male':
            bmr = Decimal('9.99') * Decimal(weight) + Decimal('6.25') * Decimal(height) - Decimal('4.92') * Decimal(age) + Decimal('5')
        elif gender.lower() == 'female':
            bmr = Decimal('9.99') * Decimal(weight) + Decimal('6.25') * Decimal(height) - Decimal('4.92') * Decimal(age) - Decimal('161')
        else:
            raise ValueError("Gender not recognized. Valid: 'male' or 'female'.")

        return round(bmr, 0)

    def get_maintenance(self):
        bmr = self.get_bmr()
        activity_level = self.user_profile.activity_level
        activity_factors = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'athlete': 1.9
        }

        if activity_level.lower() in activity_factors:
            return round(Decimal(bmr) * Decimal(activity_factors[activity_level.lower()]), 0)
        else:
            raise ValueError("Activity level not recognized. Valid: 'sedentary', 'light', 'moderate', 'active', 'athlete'")

    def get_rcm_cal(self):
        CALORIES_PER_KG = 7700  # Approx calories per kg of body weight
        WEEKS_PER_MONTH = 4.34524  # Average weeks per month
        maintenance_calories = self.get_maintenance()
        body_goal = BodyGoal.objects.filter(user=self.user_profile.user).first()

        if not body_goal:
            return maintenance_calories

        if body_goal.category:
            # Categorical target
            if not body_goal.category is None:
                return self.calc_cat_goals(body_goal, maintenance_calories)
        else:
            # Specific target
            return self.calculate_specific_target_calories(body_goal, maintenance_calories)

        return maintenance_calories
    

    def calc_cat_goals(self, body_goal, maintenance_calories):
        if body_goal.category == BodyGoal.CUSTOM:
            # Handle custom body goals with specific bodyGoal method
            maintenance_calories = self.get_maintenance()
            adjustment = 0

            print(body_goal.target_weight)
            # Calorie adjustment for target weight
            if body_goal.target_weight:
                print("£££££££££")
                weight_difference = body_goal.target_weight - self.user_profile.weight
                # Roughly 500 calories per day for each 0.5 kg of weight change per week
                calorie_adjustment_weight = (weight_difference * 500) / 7
                adjustment += calorie_adjustment_weight

            # Adjustment capped at reasonable limits
            adjustment = max(min(adjustment, 1000), -1000)

            return round (maintenance_calories + adjustment, 0)
        else:
            adjustment_factor = 1.0  # Default no change

            if body_goal.category == BodyGoal.WEIGHT_LOSS:
                if body_goal.level == BodyGoal.MILD:
                    adjustment_factor = 0.85
                elif body_goal.level == BodyGoal.AVERAGE:
                    adjustment_factor = 0.80
                elif body_goal.level == BodyGoal.EXTREME:
                    adjustment_factor = 0.75

            elif body_goal.category == BodyGoal.MUSCLE_BUILDING:
                if body_goal.level == BodyGoal.MILD:
                    adjustment_factor = 1.05
                elif body_goal.level == BodyGoal.AVERAGE:
                    adjustment_factor = 1.10
                elif body_goal.level == BodyGoal.EXTREME:
                    adjustment_factor = 1.15

            elif body_goal.category == BodyGoal.FAT_LOSS:
                if body_goal.level == BodyGoal.MILD:
                    adjustment_factor = 0.90
                elif body_goal.level == BodyGoal.AVERAGE:
                    adjustment_factor = 0.85
                elif body_goal.level == BodyGoal.EXTREME:
                    adjustment_factor = 0.80

            elif body_goal.category == BodyGoal.STRENGTH_BUILDING:
                if body_goal.level == BodyGoal.MILD:
                    adjustment_factor = 1.05
                elif body_goal.level == BodyGoal.AVERAGE:
                    adjustment_factor = 1.10
                elif body_goal.level == BodyGoal.EXTREME:
                    adjustment_factor = 1.15

            elif body_goal.category == BodyGoal.ENDURANCE_IMPROVEMENT:
                adjustment_factor = 1.02

            elif body_goal.category == BodyGoal.CUSTOM:
                adjustment_factor = 1.02

            # Flexibility and balance goals don't significantly affect calorie needs

            return round (maintenance_calories * Decimal(adjustment_factor), 2)