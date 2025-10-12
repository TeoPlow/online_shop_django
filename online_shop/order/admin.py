from django.contrib import admin
from .models import BasketItem, Order, DeliverySettings


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    """Админка для корзины"""

    list_display = ("id", "user", "product", "count", "added_at")
    list_filter = ("user", "product")
    search_fields = ("user__username", "product__title")
    readonly_fields = ("id", "user", "product", "count", "added_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админка для заказов"""

    list_display = (
        "id",
        "user",
        "fullName",
        "status",
        "createdAt",
        "totalCost",
    )
    list_filter = ("status", "createdAt", "user")
    search_fields = ("fullName", "email", "phone", "city", "address")
    filter_horizontal = ("products",)
    readonly_fields = (
        "id",
        "user",
        "fullName",
        "status",
        "createdAt",
        "totalCost",
    )


class DeliverySettingsAdmin(admin.ModelAdmin):
    """Админка для настроек доставки"""

    def has_add_permission(self, request):
        return not DeliverySettings.objects.exists()


admin.site.register(DeliverySettings, DeliverySettingsAdmin)
