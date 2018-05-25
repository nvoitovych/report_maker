from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from social_django.admin import Association, Nonce, UserSocialAuth

from account.models import Account


class AccountInline(admin.StackedInline):
    model = Account
    can_delete = False
    verbose_name_plural = 'Детальна інформація'


class UserAdmin(BaseUserAdmin):
    inlines = (AccountInline, )
    readonly_fields = (
        'last_login',
        'date_joined',
        'is_superuser',
    )
    exclude = (
        'groups',
    )
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'last_login',
    )

    fieldsets = (
        ('Основна інформація', {'fields': ('username', 'password')}),
        ('Особиста інформація', {
            'fields': (
                'first_name',
                'last_name',
                'email',
            )
        }),
        ('Інше', {
            'fields': (
                'is_active',
                'is_superuser',
                'last_login',
                'date_joined',
            )
        }),
    )

    @staticmethod
    def block_user(modeladmin, request, queryset):
        for account in queryset:
            account.is_active = False
            account.save()

    @staticmethod
    def unblock_user(modeladmin, request, queryset):
        for account in queryset:
            account.is_active = True
            account.save()


class AccountAdmin(admin.ModelAdmin):
    readonly_fields = (
        'user',
    )
    fields = (
        'user',
        'mobile_phone_number',
        'is_online',
    )
    list_display = (
        'user',
        'mobile_phone_number',
        'is_online',
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def has_change_permission(self, request, obj=None):
        has_class_permission = super(AccountAdmin, self).has_change_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.user.id:
            return False
        return True


admin.site.add_action(UserAdmin.block_user, name='Заблокувати')
admin.site.add_action(UserAdmin.unblock_user, name='Розблокувати')
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
# Remove Association, Nonce and UserSocialAuth(from social_django) from AdminPanel
admin.site.unregister(Association)
admin.site.unregister(Nonce)
admin.site.unregister(UserSocialAuth)


