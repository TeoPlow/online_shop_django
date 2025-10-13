from django.contrib import admin
from .models import BasketItem, Order, DeliverySettings, OrderItem


@admin.register(BasketItem)
class BasketItemAdmin(admin.ModelAdmin):
    """Админка для корзины"""

    list_display = ("id", "user", "product", "count", "added_at")
    list_filter = ("user", "product")
    search_fields = ("user__username", "product__title")
    readonly_fields = ("id", "user", "product", "count", "added_at")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Админка для предметов заказа"""

    list_display = ("id", "order", "product", "count")
    list_filter = ("order", "product")
    search_fields = ("order__fullName", "product__title")
    readonly_fields = ("id", "order", "product", "count")


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
    readonly_fields = (
        "id",
        "user",
        "fullName",
        "status",
        "createdAt",
        "totalCost",
    )


class DeliverySettingsAdmin(admin.ModelAdmin):
    """Админка для настроек доставки (один объект)"""

    def has_add_permission(self, request):
        return not DeliverySettings.objects.exists()


admin.site.register(DeliverySettings, DeliverySettingsAdmin)
