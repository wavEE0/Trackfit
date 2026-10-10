# Initial migration for the nutrition app.
# Written by hand -- makemigrations was never run for this app.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [("trackfit", "0001_initial")]
    operations = [
        migrations.CreateModel(name="Food", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=100)),
            ("category", models.CharField(choices=[("FR","Fruits"),("VG","Vegetables"),("GR","Grains"),("MT","Meats"),("DA","Dairy"),("FT","Fats and Oils"),("SW","Sweets"),("BV","Beverages"),("OT","Others")], max_length=2)),
            ("calories",      models.DecimalField(decimal_places=2, max_digits=6)),
            ("protein",       models.DecimalField(decimal_places=2, max_digits=5)),
            ("carbohydrates", models.DecimalField(decimal_places=2, max_digits=5)),
            ("sugar",  models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
            ("fats",   models.DecimalField(decimal_places=2, max_digits=5)),
            ("fiber",  models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
            ("sodium", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
            ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="foods", to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name="Meal", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=100)),
            ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="meals", to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name="MealItem", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("quantity", models.DecimalField(decimal_places=2, max_digits=5)),
            ("food", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="nutrition.food")),
            ("meal", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="nutrition.meal")),
        ]),
        migrations.AddField(model_name="meal", name="foods", field=models.ManyToManyField(through="nutrition.mealitem", to="nutrition.food")),
        migrations.CreateModel(name="DailyIntake", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("date", models.DateField()),
            ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dailyIntake", to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name="IntakeMeal", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("quantity", models.PositiveIntegerField(default=1)),
            ("daily_intake", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="nutrition.dailyintake")),
            ("meal", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="nutrition.meal")),
        ]),
        migrations.AddField(model_name="dailyintake", name="meals", field=models.ManyToManyField(through="nutrition.intakemeal", to="nutrition.meal")),
        migrations.CreateModel(name="UserProfile", fields=[
            ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ("age", models.IntegerField()),
            ("gender", models.CharField(max_length=30)),
            ("height", models.DecimalField(decimal_places=2, max_digits=5)),
            ("weight", models.DecimalField(decimal_places=2, max_digits=5)),
            ("activity_level", models.CharField(max_length=50)),
        ]),
        migrations.CreateModel(name="BodyGoal", fields=[
            ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ("category", models.CharField(blank=True, choices=[("WL","Weight Loss"),("MB","Muscle Building"),("FL","Fat Loss"),("EI","Endurance Improvement"),("FB","Flexibility and Balance"),("SB","Strength Building"),("CU","Custom")], max_length=2, null=True)),
            ("level", models.CharField(blank=True, choices=[("Mild","Mild"),("Average","Average"),("Extreme","Extreme"),("Custom","Custom")], default="Mild", max_length=7, null=True)),
            ("target_weight",              models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
            ("goal_date",                  models.DateField(blank=True, null=True)),
            ("target_body_fat_percentage", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
            ("target_muscle_mass",         models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
            ("target_bmi",                 models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
        ]),
    ]
