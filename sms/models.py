
import re
from urllib.parse import urlparse

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.core.exceptions import ValidationError


class User(AbstractUser):
    sms_balance = models.PositiveIntegerField(default=1)


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
        max_length=155,
        validators=[
            MinLengthValidator(4),
            RegexValidator(r'^[\x00-\x7F]*$', 'Only ASCII characters are allowed'),
            validate_no_phishing_links  # Add custom phishing validator
        ]
    )


class SMSTariff(TimeStampedModel):
    name = models.CharField(max_length=50)
    sms_count = models.PositiveIntegerField()
    price = models.PositiveIntegerField(help_text="Narx (so‘mda)")
    price_per_sms = models.FloatField()

    def __str__(self):
        return f"{self.name} - {self.sms_count} ta - {self.price} so‘m ({self.price_per_sms} so‘m/SMS)"
