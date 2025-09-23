from django.urls import path
from .views import (
    BasketView,
    OrdersView,
    OrderDetailView,
    PaymentView,
)

urlpatterns = [
    path("basket", BasketView.as_view()),
    path("orders", OrdersView.as_view()),
    path("order/<int:id>", OrderDetailView.as_view()), # В swagger неверный url - /orders/{id}
    path("payment/<int:id>", PaymentView.as_view()),
]
