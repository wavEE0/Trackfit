from django import forms
from .models import UserProfile, BodyGoal
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class UserProfileForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary'),
        ('light', 'Light'),
        ('moderate', 'Moderate'),
        ('active', 'Active'),
        ('athlete', 'Athlete'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES)
    activity_level = forms.ChoiceField(choices=ACTIVITY_LEVEL_CHOICES)

    class Meta:
        model = UserProfile
        fields = ['age', 'gender', 'height', 'weight', 'activity_level']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit'))

class BodyGoalForm(forms.ModelForm):
    class Meta:
        model = BodyGoal
        fields = ['category', 'level', 'target_weight', 'goal_date']




