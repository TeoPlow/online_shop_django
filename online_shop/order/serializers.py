from rest_framework import serializers
from product.serializers import ProductShortSerializer
from .models import Order, OrderItem, BasketItem


class OrderProductSerializer(serializers.ModelSerializer):
    """Сериализатор для продуктов в заказе"""

    price = serializers.DecimalField(
        source="product.price", max_digits=10, decimal_places=2
    )
    count = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = ["product", "count", "price"]

    def to_representation(self, obj):
        product_data = ProductShortSerializer(obj.product).data
        product_data["price"] = obj.product.price
        product_data["count"] = obj.count
        return product_data


class BasketItemSerializer(serializers.ModelSerializer):
    """Сериализатор для предмета в корзине"""

    price = serializers.DecimalField(
        source="product.price", max_digits=10, decimal_places=2
    )
    count = serializers.IntegerField()

    class Meta:
        model = BasketItem
        fields = ["product", "count", "price"]

    def to_representation(self, obj):
        product_data = ProductShortSerializer(obj.product).data
        product_data["price"] = obj.product.price
        product_data["count"] = obj.count
        return product_data


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для заказа"""

    products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        ]
