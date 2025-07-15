import uuid
import hashlib
import re
import secrets
from urllib.parse import urlparse

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.core.exceptions import ValidationError

class BaseModel(TimeStampedModel):
    id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, primary_key=True)

    class Meta:
        abstract = True


class User(BaseModel, AbstractUser):
    def __str__(self):
        return self.username


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    sms_balance = models.PositiveIntegerField(default=1)
    api_token_hash = models.CharField(max_length=64, unique=True)
    _raw_api_token = None

    def __str__(self):
        return f"{self.user.username} Profile"

    def save(self, *args, **kwargs):
        if not self.api_token_hash:
            raw_token = self.generate_api_token()
            self._raw_api_token = raw_token
            self.api_token_hash = self.hash_token(raw_token)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_api_token():
        return secrets.token_urlsafe(42)[:50]

    @staticmethod
    def hash_token(token):
        return hashlib.sha256(token.encode()).hexdigest()

    def get_raw_token(self):
        return getattr(self, "_raw_api_token", None)


phone_regex = RegexValidator(
    regex=r'^(99|98|97|95|94|93|91|90|88|87|77|70|50|33|20)\d{7}$',
    message="Telefon raqam quyidagi formatda bo'lishi kerak: 'XXXXXXXXX' (masalan, 901234567)."
)

def validate_no_phishing_links(value):
    url_pattern = r'(https?://[^\s]+)'
    links = re.findall(url_pattern, value)
    suspicious_keywords = ['login', 'secure', 'signin', 'verify', 'account', 'password']
    suspicious_domains = ['example.com', 'phishingsite.com']

    for link in links:
        for keyword in suspicious_keywords:
            if keyword in link:
                raise ValidationError(f"Phishing link detected: {link}")
        parsed_url = urlparse(link)
        if parsed_url.netloc in suspicious_domains:
            raise ValidationError(f"Suspicious domain detected: {parsed_url.netloc}")


class SendHistory(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.CharField(validators=[phone_regex])
    text = models.TextField(
        max_length=155,
        validators=[
            MinLengthValidator(4),
            RegexValidator(r'^[\x00-\x7F]*$', 'Only ASCII characters are allowed'),
            validate_no_phishing_links
        ]
    )

    def __str__(self):
        return f"{self.user.username} → {self.number}: {self.text[:30]}..."


class SMSTariff(BaseModel):
    name = models.CharField(max_length=50)
    sms_count = models.PositiveIntegerField()
    price = models.PositiveIntegerField(help_text="Narx (so'mda)")
    price_per_sms = models.FloatField(blank=True, editable=False)

    def save(self, *args, **kwargs):
        if self.sms_count > 0:
            self.price_per_sms = round(self.price / self.sms_count, 2)
        else:
            self.price_per_sms = 0.0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.sms_count} ta - {self.price} so'm ({self.price_per_sms} so'm/SMS)"
