from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from nutrition.models import UserProfile, Food, Meal, MealItem

E2E_USERNAME = "e2e_testuser"
E2E_PASSWORD = "e2e_testpass_123"

class Command(BaseCommand):
    help = "Seed deterministic test data for e2e tests."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true")

    def handle(self, *args, **options):
        User = get_user_model()
        if options["reset"]:
            User.objects.filter(username=E2E_USERNAME).delete()
        user, created = User.objects.get_or_create(username=E2E_USERNAME, defaults={"email": "e2e@test.local"})
        if created or options["reset"]:
            user.set_password(E2E_PASSWORD); user.save()
        UserProfile.objects.get_or_create(user=user, defaults={
            "age": 25, "gender": "male", "height": Decimal("175.00"),
            "weight": Decimal("75.00"), "activity_level": "moderate"})
        foods_data = [
            {"name":"E2E Banana","category":"FR","calories":Decimal("89"),"protein":Decimal("1.1"),"carbohydrates":Decimal("23"),"fats":Decimal("0.3")},
            {"name":"E2E Chicken Breast","category":"MT","calories":Decimal("165"),"protein":Decimal("31"),"carbohydrates":Decimal("0"),"fats":Decimal("3.6")},
        ]
        foods = [Food.objects.get_or_create(name=fd["name"], user=user, defaults=fd)[0] for fd in foods_data]
        meal, mc = Meal.objects.get_or_create(name="E2E Test Meal", user=user)
        if mc and foods:
            MealItem.objects.create(meal=meal, food=foods[0], quantity=Decimal("1"))
        self.stdout.write(self.style.SUCCESS(f"Done. User: {E2E_USERNAME} / {E2E_PASSWORD}"))
