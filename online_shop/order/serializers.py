from rest_framework import serializers
from .models import (
    BasketItem,
    Order,
)
from product.serializers import ProductShortSerializer, SaleItemSerializer

class OrderProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    count = serializers.IntegerField()

    class Meta:
        model = BasketItem
        fields = [
            'id', 'category', 'title', 'price', 'count', 'date', 'description',
            'freeDelivery', 'images', 'tags', 'reviews', 'rating'
        ]

    def get_price(self, obj):
        return obj.product.price

    def to_representation(self, obj):
        product_data = ProductShortSerializer(obj.product).data
        product_data['price'] = obj.product.price
        product_data['count'] = obj.count
        return product_data


class OrderSerializer(serializers.ModelSerializer):
    products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'createdAt', 'fullName', 'email', 'phone', 'deliveryType',
            'paymentType', 'totalCost', 'status', 'city', 'address', 'products'
        ]