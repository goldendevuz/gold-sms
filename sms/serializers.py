from rest_framework import serializers
from django.core.validators import MinLengthValidator, RegexValidator

# Assuming validate_no_phishing_links and phone_regex are defined in sms.models
from sms.models import phone_regex, validate_no_phishing_links


class SendSmsSerializer(serializers.Serializer):
    number = serializers.CharField(
        validators=[phone_regex]
    )
    text = serializers.CharField(
        max_length=155,
        style={'base_template': 'textarea.html', 'rows': 4, 'attrs': {'maxlength': 155}},
        trim_whitespace=False,
        validators=[
            MinLengthValidator(4),
            # RegexValidator(r'^[\x00-\x7F]*$', 'Only ASCII characters are allowed'),
            validate_no_phishing_links  # Add custom phishing validator
        ]
    )