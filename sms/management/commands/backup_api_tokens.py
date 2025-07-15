from django.core.management.base import BaseCommand
from sms.models import UserProfile
import json
import os

class Command(BaseCommand):
    help = 'Backup API token hashes and any available raw tokens to a JSON file'

    def handle(self, *args, **kwargs):
        tokens_data = []
        for profile in UserProfile.objects.all():
            raw_token = profile.get_raw_token() if hasattr(profile, 'get_raw_token') else None
            tokens_data.append({
                'user_id': profile.user_id,
                'username': profile.user.username,
                'api_token': raw_token or 'N/A',  # raw token if available, else 'N/A'
                'api_token_hash': profile.api_token_hash,
            })

        backup_path = os.path.join(os.getcwd(), 'api_tokens_backup.json')
        with open(backup_path, 'w') as f:
            json.dump(tokens_data, f, indent=2)
        self.stdout.write(self.style.SUCCESS(f'Backup saved to {backup_path}'))
