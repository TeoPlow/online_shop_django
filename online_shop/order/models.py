from django.db import models
from user.models import User
from product.models import Product


class BasketItem(models.Model):
    """Модель предмета в корзине"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="basket_items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.product} ({self.count})"


class Order(models.Model):
    """Модель заказа"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders"
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    fullName = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    deliveryType = models.CharField(max_length=50)
    paymentType = models.CharField(max_length=50)
    totalCost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default="accepted")
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    products = models.ManyToManyField("OrderItem", related_name="orders")

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["createdAt"]),
        ]

    def __str__(self):
        return f"Order #{self.id} ({self.fullName})"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    count = models.PositiveIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.order} - {self.product} ({self.count})"


class DeliverySettings(models.Model):
    """Модель настроек доставки"""

    express_cost = models.DecimalField(
        "Express delivery", max_digits=10, decimal_places=2, default=500
    )
    regular_cost = models.DecimalField(
        "Regular delivery", max_digits=10, decimal_places=2, default=200
    )
    free_from = models.DecimalField(
        "Free delivery from", max_digits=10, decimal_places=2, default=2000
    )

    def __str__(self):
        return "Delivery settings"

    class Meta:
        verbose_name = "Delivery settings"
        verbose_name_plural = "Delivery's settings"
