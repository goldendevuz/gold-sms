from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from sms.models import SendHistory, SMSTariff, UserProfile

User = get_user_model()


class BaseAdmin(admin.ModelAdmin):
    list_per_page = 10

    class Meta:
        abstract = True


from django.contrib import messages

@admin.action(description='SMS balansni oshirish')
def add_sms_balance(modeladmin, request, queryset):
    no_profile_users = []
    for user in queryset:
        if hasattr(user, 'profile'):
            profile = user.profile
            profile.sms_balance += 50
            profile.save()
        else:
            no_profile_users.append(user.username)

    if no_profile_users:
        messages.warning(request, f"Following users have no profile and were skipped: {', '.join(no_profile_users)}")

class UserAdmin(UserAdmin):
    list_display = [f.name for f in User._meta.fields if
                    f.name not in ('password', 'groups', 'user_permissions', 'is_staff', 'is_superuser')]
    actions = [add_sms_balance]

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


@admin.register(SendHistory)
class SendHistoryAdmin(BaseAdmin):
    list_display = [f.name for f in SendHistory._meta.fields] + ['text_length', 'user_balance']

    def user_balance(self, obj):
        try:
            return obj.user.profile.sms_balance
        except UserProfile.DoesNotExist:
            return '-'


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


@admin.register(UserProfile)
class UserProfileAdmin(BaseAdmin):
    list_display = [f.name for f in UserProfile._meta.fields]

admin.site.register(User, UserAdmin)