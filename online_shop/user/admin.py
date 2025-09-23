from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Image,
    User,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {"fields": ("fullName", "phone", "avatar")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {"fields": ("fullName", "phone", "avatar")}),
    )
    list_display = (
        "username",
        "email",
        "fullName",
        "is_staff",
        "is_superuser",
    )
    search_fields = ("email", "fullName", "phone")


admin.site.register(Image)
