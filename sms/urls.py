from django.urls import path

from .views import SmsAPIView

urlpatterns = [
    path('sms/', SmsAPIView.as_view(), name='sms'),
]
