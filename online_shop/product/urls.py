from django.urls import path
from .views import (
    CategoryListView,
    CatalogView,
    ProductsPopularView,
    ProductsLimitedView,
    SalesView,
    BannersView,
    ProductDetailView,
    ProductReviewView,
    TagListView,
)


urlpatterns = [
    path("categories", CategoryListView.as_view()),
    path("catalog", CatalogView.as_view()),
    path("products/popular", ProductsPopularView.as_view()),
    path("products/limited", ProductsLimitedView.as_view()),
    path("sales", SalesView.as_view()),
    path("banners", BannersView.as_view()),
    path("product/<int:id>", ProductDetailView.as_view()),
    path("product/<int:id>/reviews", ProductReviewView.as_view()),
    path("tags", TagListView.as_view()),
]
