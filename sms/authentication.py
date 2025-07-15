import hashlib
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
from sms.models import UserProfile  # adjust to your app name

User = get_user_model()


class SuperUserOrAPIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise exceptions.AuthenticationFailed('Invalid Authorization header format.')

        unhashed_token = parts[1]

        # Hash the incoming token to compare
        hashed_token = hashlib.sha256(unhashed_token.encode()).hexdigest()

        try:
            profile = UserProfile.objects.get(api_token_hash=hashed_token)
            user = profile.user
        except UserProfile.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API token.')

        return (user, None)
