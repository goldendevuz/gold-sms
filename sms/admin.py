from django.contrib import admin
from django.contrib.auth import get_user_model

from sms.models import SendHistory, SMSTariff

User = get_user_model()


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 10

    class Meta:
        abstract = True


@admin.action(description='SMS balansni oshirish')
def add_sms_balance(modeladmin, request, queryset):
    for user in queryset:
        user.sms_balance += 50  # Misol uchun 50 ta qo‘shamiz
        user.save()


@admin.register(User)
class UserAdmin(BaseAdmin):
    list_display = [f.name for f in User._meta.fields if
                    f.name not in ('password', 'groups', 'user_permissions', 'is_staff', 'is_superuser')]
    actions = [add_sms_balance]


@admin.register(SendHistory)
class SendHistoryAdmin(BaseAdmin):
    list_display = [f.name for f in SendHistory._meta.fields] + ['text_length', 'user_balance']

    def user_balance(self, obj):
        return obj.user.sms_balance

    user_balance.short_description = "User Balansi"

    def text_length(self, obj):
        return len(obj.text) if obj.text else 0

    text_length.short_description = 'Text Length'


@admin.register(SMSTariff)
class SMSTariffAdmin(BaseAdmin):
    list_display = [f.name for f in SMSTariff._meta.fields]
    ordering = ('price_per_sms',)

    # def price_per_sms(self, obj):
    #     return obj.price_per_sms()
    # price_per_sms.short_description = '1 SMS narxi (so‘m)'
