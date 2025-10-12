from rest_framework import serializers
from product.serializers import ProductShortSerializer
from .models import Order


class OrderProductSerializer(serializers.ModelSerializer):
    """Сериализатор для продуктов в заказе"""

    price = serializers.SerializerMethodField()
    count = serializers.IntegerField()

    def get_price(self, obj):
        """Получение цены продукта"""
        return obj.product.price

    def to_representation(self, obj):
        """Преобразование объекта в словарь"""
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
