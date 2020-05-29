from django.contrib import admin

from .models import Profile


class AdminProfile(admin.ModelAdmin):
    list_display = ("user", "full_name", "gender", "ticket_type")
    search_fields = ("user__email", "user__uuid", "full_name", "gender", "ticket_type")


admin.site.register(Profile, AdminProfile)
