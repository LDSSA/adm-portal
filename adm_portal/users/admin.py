from django.contrib import admin

from .models import User, UserConfirmEmail, UserResetPassword


class AdminUser(admin.ModelAdmin):
    list_display = ("email", "uuid")
    search_fields = ("email", "uuid")


class AdminUserConfirmEmail(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__email", "user__uuid")


class AdminUserResetPassword(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__email", "user__uuid")


admin.site.register(User, AdminUser)
admin.site.register(UserConfirmEmail, AdminUserConfirmEmail)
admin.site.register(UserResetPassword)
