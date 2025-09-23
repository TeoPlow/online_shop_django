from rest_framework import serializers
from .models import (
    Category,
    Tag,
    Product,
    SaleItem,
)
from user.serializers import ImageSerializer


class SubCategorySerializer(serializers.ModelSerializer):
    image = ImageSerializer()

    class Meta:
        model = Category
        fields = ["id", "title", "image"]


class CategorySerializer(serializers.ModelSerializer):
    image = ImageSerializer()
    subcategories = SubCategorySerializer(
        many=True, source="subcategories.all"
    )

    class Meta:
        model = Category
        fields = ["id", "title", "image", "subcategories"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ReviewSerializer(serializers.Serializer):
    author = serializers.CharField()
    email = serializers.EmailField()
    text = serializers.CharField()
    rate = serializers.IntegerField()


class SpecificationSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.CharField()


class ProductShortSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "title",
            "price",
            "count",
            "date",
            "description",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "rating",
        ]


class ProductFullSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    tags = TagSerializer(many=True)
    reviews = ReviewSerializer(many=True, required=False)
    specifications = SpecificationSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            "id",
            "category",
            "title",
            "price",
            "count",
            "date",
            "description",
            "fullDescription",
            "freeDelivery",
            "images",
            "tags",
            "reviews",
            "specifications",
            "rating",
        ]


class SaleItemSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    id = serializers.IntegerField(source="product.id")

    class Meta:
        model = SaleItem
        fields = [
            "id",
            "title",
            "price",
            "salePrice",
            "dateFrom",
            "dateTo",
            "images",
        ]
