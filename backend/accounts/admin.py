from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "avatar_url", "has_medium_token")
    search_fields = ("user__username", "user__email")

    @admin.display(boolean=True, description="Medium token")
    def has_medium_token(self, obj):
        return bool(obj.medium_token)
