from django.db import models
from user.models import Image
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Модель категории продукта"""

    title = models.CharField(max_length=255)
    image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="category_images",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subcategories",
    )

    class Meta:
        indexes = [
            models.Index(fields=["parent"]),
        ]

    def clean(self):
        if self.parent and self.parent.parent:
            raise ValidationError("Subcategory cannot have a subcategory.")

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Модель тега продукта"""

    name = models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class Review(models.Model):
    """Модель отзыва о продукте"""

    author = models.CharField(max_length=255)
    email = models.EmailField()
    text = models.TextField()
    rate = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["rate"]),
        ]

    def __str__(self):
        return f"{self.author} ({self.rate})"


class Specification(models.Model):
    """Модель характеристики продукта"""

    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}: {self.value}"


class Product(models.Model):
    """Модель продукта"""

    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="products"
    )
    title = models.CharField(max_length=255)
    standart_price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    fullDescription = models.TextField(blank=True)
    freeDelivery = models.BooleanField(default=False)
    images = models.ManyToManyField(Image, related_name="product_images")
    tags = models.ManyToManyField(Tag, related_name="products", blank=True)
    reviews = models.ManyToManyField(
        "Review", related_name="products", blank=True
    )
    specifications = models.ManyToManyField(
        "Specification", related_name="products", blank=True
    )
    rating = models.IntegerField(default=0)
    sort_index = models.IntegerField(default=0)
    limitedEdition = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["title"]),
            models.Index(fields=["sort_index"]),
        ]

    # Для работы скидок
    @property
    def price(self):
        sale = self.sales.first()
        if sale:
            return sale.salePrice
        return self.standart_price

    def __str__(self):
        return self.title


class SaleItem(models.Model):
    """Модель акции на продукт"""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="sales"
    )
    salePrice = models.DecimalField(max_digits=10, decimal_places=2)
    dateFrom = models.CharField(max_length=10)
    dateTo = models.CharField(max_length=10)

    class Meta:
        indexes = [
            models.Index(fields=["product"]),
        ]

    @property
    def title(self):
        return self.product.title

    @property
    def price(self):
        return self.product.standart_price

    @property
    def images(self):
        return self.product.images.all()

    def __str__(self):
        return self.product.title
