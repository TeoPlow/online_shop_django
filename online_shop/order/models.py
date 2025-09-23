from django.db import models
from user.models import User
from product.models import Product


class BasketItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='basket_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product} ({self.count})"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    createdAt = models.DateTimeField(auto_now_add=True)
    fullName = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    deliveryType = models.CharField(max_length=50)
    paymentType = models.CharField(max_length=50)
    totalCost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='accepted')
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    products = models.ManyToManyField(BasketItem, related_name='orders')

    def __str__(self):
        return f"Order #{self.id} ({self.fullName})"


class DeliverySettings(models.Model):
    express_cost = models.DecimalField("Express delivery", max_digits=10, decimal_places=2, default=500)
    regular_cost = models.DecimalField("Regular delivery", max_digits=10, decimal_places=2, default=200)
    free_from = models.DecimalField("Free delivery from", max_digits=10, decimal_places=2, default=2000)

    def __str__(self):
        return "Delivery settings"

    class Meta:
        verbose_name = "Delivery settings"
        verbose_name_plural = "Delivery settings"
