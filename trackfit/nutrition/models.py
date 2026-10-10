from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.db.models import F


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=30)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    activity_level = models.CharField(max_length=50)

    def __str__(self): return self.user.username

    def get_bmi(self):
        h = self.height / 100
        return float(self.weight) / (h ** 2)

    def get_bfp(self):
        bmi = self.get_bmi()
        if self.gender.lower() == 'male':   return (1.20*bmi)+(0.23*self.age)-16.2
        if self.gender.lower() == 'female': return (1.20*bmi)+(0.23*self.age)-5.4
        raise ValueError("Gender must be 'male' or 'female'.")


class BodyGoal(models.Model):
    WEIGHT_LOSS='WL'; MUSCLE_BUILDING='MB'; FAT_LOSS='FL'
    ENDURANCE_IMPROVEMENT='EI'; FLEXIBILITY_BALANCE='FB'; STRENGTH_BUILDING='SB'; CUSTOM='CU'
    CATEGORY_CHOICES = [('WL','Weight Loss'),('MB','Muscle Building'),('FL','Fat Loss'),
        ('EI','Endurance Improvement'),('FB','Flexibility and Balance'),
        ('SB','Strength Building'),('CU','Custom')]
    MILD='Mild'; AVERAGE='Average'; EXTREME='Extreme'; CUSTOM_LEVEL='Custom'
    LEVEL_CHOICES = [('Mild','Mild'),('Average','Average'),('Extreme','Extreme'),('Custom','Custom')]

    user     = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, null=True)
    level    = models.CharField(max_length=7, choices=LEVEL_CHOICES, default=MILD, null=True)
    target_weight               = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    goal_date                   = models.DateField(null=True, blank=True)
    target_body_fat_percentage  = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    target_muscle_mass          = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    target_bmi                  = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def is_advanced_goal(self): return self.category == self.CUSTOM

    def get_targets_display(self):
        def fmt(v):
            s = f"{v:f}"
            return s.rstrip("0").rstrip(".") if "." in s else s
        parts = []
        if self.target_weight              is not None: parts.append(f"Weight: {fmt(self.target_weight)} kg")
        if self.target_body_fat_percentage is not None: parts.append(f"Body Fat: {fmt(self.target_body_fat_percentage)}%")
        if self.target_muscle_mass         is not None: parts.append(f"Muscle Mass: {fmt(self.target_muscle_mass)} kg")
        if self.target_bmi                 is not None: parts.append(f"BMI: {fmt(self.target_bmi)}")
        return ", ".join(parts)

    def __str__(self):
        if self.is_advanced_goal():
            return f"{self.user.username}'s Advanced Body Goal: {self.get_targets_display()}"
        return f"{self.user.username}'s Body Goal: {self.get_category_display() if self.category else 'None'} ({self.get_level_display()})"


class Food(models.Model):
    CATEGORY_CHOICES = [("FR","Fruits"),("VG","Vegetables"),("GR","Grains"),("MT","Meats"),
        ("DA","Dairy"),("FT","Fats and Oils"),("SW","Sweets"),("BV","Beverages"),("OT","Others")]
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="foods", null=True, blank=True)
    category     = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    calories     = models.DecimalField(max_digits=6, decimal_places=2)
    protein      = models.DecimalField(max_digits=5, decimal_places=2)
    carbohydrates= models.DecimalField(max_digits=5, decimal_places=2)
    sugar        = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fats         = models.DecimalField(max_digits=5, decimal_places=2)
    fiber        = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sodium       = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    def __str__(self): return f"{self.name} ({self.get_category_display()})"


class Meal(models.Model):
    name  = models.CharField(max_length=100)
    foods = models.ManyToManyField(Food, through="MealItem")
    user  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="meals", null=True, blank=True)

    def add_food(self, food, quantity):
        mi, c = self.mealitem_set.get_or_create(food=food, defaults={"quantity": quantity})
        if not c: mi.quantity += quantity; mi.save()

    def __str__(self): return self.name
    def calories(self): return sum(i.food.calories*i.quantity for i in self.mealitem_set.all())
    def total_calories(self): return self.calories()
    def protein(self):       return sum(i.food.protein*i.quantity for i in self.mealitem_set.all())
    def carbohydrates(self): return sum(i.food.carbohydrates*i.quantity for i in self.mealitem_set.all())
    def fats(self):          return sum(i.food.fats*i.quantity for i in self.mealitem_set.all())
    def ingredients_list(self): return [{"name":i.food.name,"quantity":i.quantity} for i in self.mealitem_set.all()]


class MealItem(models.Model):
    meal     = models.ForeignKey(Meal, on_delete=models.CASCADE)
    food     = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    def __str__(self): return f"{self.food.name} x {self.quantity}"


class IntakeMeal(models.Model):
    daily_intake = models.ForeignKey("DailyIntake", on_delete=models.CASCADE)
    meal         = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity     = models.PositiveIntegerField(default=1)


class DailyIntake(models.Model):
    date  = models.DateField()
    user  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dailyIntake")
    meals = models.ManyToManyField(Meal, through="IntakeMeal")

    def add_meal(self, meal, quantity=1):
        im, c = IntakeMeal.objects.get_or_create(daily_intake=self, meal=meal, defaults={"quantity": quantity})
        if not c: im.quantity += quantity; im.save()

    def remove_meal(self, meal, quantity=1):
        try:
            im = self.intakemeal_set.get(meal=meal)
            im.quantity = F("quantity") - quantity; im.save(); im.refresh_from_db()
            if im.quantity <= 0: im.delete()
        except IntakeMeal.DoesNotExist: pass

    def get_meal_quantity(self, meal_id):
        im = self.intakemeal_set.filter(meal_id=meal_id).first()
        return im.quantity if im else 0

    def protein(self):       return sum(m.protein()       for m in self.meals.all())
    def carbohydrates(self): return sum(m.carbohydrates() for m in self.meals.all())
    def fats(self):          return sum(m.fats()          for m in self.meals.all())
    def calories(self):      return sum(m.calories()      for m in self.meals.all())
    def __str__(self):       return f"{self.user}'s intake on {self.date}"
