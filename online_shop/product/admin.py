from django.contrib import admin
from .models import (
    Product,
    Category,
    Tag,
    SaleItem,
    Specification,
)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "price",
        "count",
        "freeDelivery",
        "limitedEdition",
        "sort_index",
    )
    list_filter = ("category", "freeDelivery", "tags")
    search_fields = ("title", "description")
    filter_horizontal = ("images", "tags")
    readonly_fields = ("rating", "reviews")


class SaleItemAdmin(admin.ModelAdmin):
    list_display = ("product", "salePrice", "dateFrom", "dateTo")
    fields = ("product", "salePrice", "dateFrom", "dateTo")


admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(SaleItem, SaleItemAdmin)
admin.site.register(Specification)
