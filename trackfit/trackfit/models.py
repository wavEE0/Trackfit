from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    def __str__(self):
        return self.email
    class Meta:
        app_label = 'trackfit'

class UserOAuthInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='oauth_info')
    oauth_provider = models.CharField(max_length=20)
    access_token = models.TextField() 
    refresh_token = models.CharField(max_length=1024, null=True, blank=True)
    expiry_date = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.oauth_provider}"

    def is_expired(self):
        return timezone.now() >= self.expiry_date

    def can_refresh(self):
        return bool(self.refresh_token)

    def update_tokens(self, access_token, refresh_token, expires_in):
        self.access_token = access_token
        self.refresh_token = refresh_token if refresh_token is not None else self.refresh_token
        self.expiry_date = timezone.now() + timedelta(seconds=expires_in)
        self.save()

    def save(self, *args, **kwargs):
        print("Access token:", self.access_token)
        print("Refresh token:", self.refresh_token)
        print("Expiry date:", self.expiry_date)
        if not self.expiry_date:
            self.expiry_date = timezone.now() + timedelta(minutes=60)
        super(UserOAuthInfo, self).save(*args, **kwargs)

    class Meta:
        app_label = 'trackfit'

