
import hashlib
import re
import secrets
from urllib.parse import urlparse

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.core.exceptions import ValidationError


class User(AbstractUser):
    pass

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    sms_balance = models.PositiveIntegerField(default=1)
    api_token_hash = models.CharField(max_length=64, unique=True)  # Store only hashed token

    # Temporarily store raw token before saving, not saved in DB
    _raw_api_token = None

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        if not self.api_token_hash:
            raw_token = self.generate_api_token()
            self._raw_api_token = raw_token  # Keep unhashed token for immediate use (e.g. display or backup)
            self.api_token_hash = self.hash_token(raw_token)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_api_token():
        # Generate a secure 50-character token (URL safe)
        return secrets.token_urlsafe(42)[:50]

    @staticmethod
    def hash_token(token):
        # Hash token using SHA256 hex digest
        return hashlib.sha256(token.encode()).hexdigest()

    def get_raw_token(self):
        # Return unhashed raw token only if freshly generated
        return getattr(self, "_raw_api_token", None)


phone_regex = RegexValidator(
    regex=r'^(99|98|97|95|94|93|91|90|88|87|77|70|50|33|20)\d{7}$',
    message="Telefon raqam quyidagi formatda bo'lishi kerak: 'XXXXXXXXX' (masalan, 901234567)."
)

def validate_no_phishing_links(value):
    # Regex pattern to match valid links (HTTP, HTTPS) but exclude potential phishing domains
    url_pattern = r'(https?://[^\s]+)'
    
    # Look for all links in the input text
    links = re.findall(url_pattern, value)
    
    # Define suspicious keywords or domains you want to block
    suspicious_keywords = ['login', 'secure', 'signin', 'verify', 'account', 'password']
    
    for link in links:
        # Check if any suspicious keywords are in the URL
        for keyword in suspicious_keywords:
            if keyword in link:
                raise ValidationError(f"Phishing link detected: {link}")
        
        # Optionally, you can validate the domain (e.g., blocking specific domains)
        parsed_url = urlparse(link)
        suspicious_domains = ['example.com', 'phishingsite.com']
        if parsed_url.netloc in suspicious_domains:
            raise ValidationError(f"Suspicious domain detected: {parsed_url.netloc}")

# Create your models here.
class SendHistory(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.CharField(
        validators=[phone_regex]
    )
    text = models.TextField(
        max_length=160,
        validators=[
            MinLengthValidator(4),
            RegexValidator(r'^[\x00-\x7F]*$', 'Only ASCII characters are allowed'),
            validate_no_phishing_links  # Add custom phishing validator
        ]
    )


class SMSTariff(TimeStampedModel):
    name = models.CharField(max_length=50)
    sms_count = models.PositiveIntegerField()
    price = models.PositiveIntegerField(help_text="Narx (so'mda)")
    price_per_sms = models.FloatField(blank=True, editable=False)

    def save(self, *args, **kwargs):
        # Prevent division by zero
        if self.sms_count > 0:
            self.price_per_sms = round(self.price / self.sms_count, 2)
        else:
            self.price_per_sms = 0.0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.sms_count} ta - {self.price} so'm ({self.price_per_sms} so'm/SMS)"

