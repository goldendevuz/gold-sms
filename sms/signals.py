import json
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from core import settings
from sms.models import SendHistory, UserProfile

User = get_user_model()

@receiver(post_save, sender=SendHistory)
def update_user_balance(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        if hasattr(user, 'profile'):
            profile = user.profile
            if profile.sms_balance > 0:
                profile.sms_balance -= 1
                profile.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=UserProfile)
def save_api_token_backup(sender, instance, created, **kwargs):
    if created:
        data = {
            "user_id": str(instance.user_id),
            "username": instance.user.username,
            "api_token": instance.get_raw_token() or "N/A",
            "api_token_hash": instance.api_token_hash,
        }
        # Define a directory to save tokens backups
        backup_dir = os.path.join(settings.BASE_DIR, 'api_token_backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Use user_id and username to create a unique filename
        filename = f"user_{instance.user_id}_{instance.user.username}_token.json"
        filepath = os.path.join(backup_dir, filename)

        # Save JSON file
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
