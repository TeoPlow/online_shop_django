from rest_framework import serializers
from user.serializers import ImageSerializer
from .models import (
    Category,
    Tag,
    Product,
    SaleItem,
)


class SubCategorySerializer(serializers.ModelSerializer):
    """Сериализатор подкатегории"""

    image = ImageSerializer()

    class Meta:
        model = Category
        fields = ["id", "title", "image"]


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории"""

    image = ImageSerializer()
    subcategories = SubCategorySerializer(
        many=True, source="subcategories.all"
    )

    class Meta:
        model = Category
        fields = ["id", "title", "image", "subcategories"]


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега"""

    class Meta:
        model = Tag
        fields = ["id", "name"]


class ReviewSerializer(serializers.Serializer):
    """Сериализатор отзыва"""

    author = serializers.CharField()
    email = serializers.EmailField()
    text = serializers.CharField()
    rate = serializers.IntegerField()


class SpecificationSerializer(serializers.Serializer):
    """Сериализатор характеристики"""

    name = serializers.CharField()
    value = serializers.CharField()


class ProductShortSerializer(serializers.ModelSerializer):
    """Сериализатор продукта"""

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
    """Полный сериализатор продукта"""

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
    """Сериализатор акции"""

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
