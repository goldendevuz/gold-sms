from django.db.models.signals import post_save
from django.dispatch import receiver

from sms.models import SendHistory


@receiver(post_save, sender=SendHistory)
def update_user_balance(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        # Bu yerda userdan 1 sms kamaytiramiz (yoki kerakli logika)
        if hasattr(user, 'sms_balance'):
            user.sms_balance -= 1
            user.save()
