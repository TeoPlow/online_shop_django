import logging
import random
import requests
from product.models import Product
from online_shop.settings import PAYMENT_URL
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
    HTTP_201_CREATED,
)
from .models import (
    BasketItem,
    Order,
    DeliverySettings,
)
from .serializers import (
    OrderProductSerializer,
    OrderSerializer,
)


log = logging.getLogger(__name__)


class BasketView(APIView):
    """Вьюха для корзины пользователя"""

    def get(self, request):
        """Получение корзины пользователя"""
        user = request.user
        # Корзину может получить только авторизованный пользователь
        if not user.is_authenticated:
            log.warning("Anonymous user tried to access basket")
            return Response(
                {"message": "User is anonymous, no basket available"},
                HTTP_404_NOT_FOUND,
            )
        items = BasketItem.objects.filter(user=user)
        serializer = OrderProductSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Добавление товара в корзину"""
        user = request.user
        product_id = request.data.get("id")
        count = int(request.data.get("count", 1))

        # Проверяю, что товар существует
        product = Product.objects.filter(id=product_id).first()
        if not product:
            log.warning(
                "User %d tried to add non-existent product %d to basket",
                user.id, product_id
                )
            return Response(
                {"message": "Product not found"}, HTTP_404_NOT_FOUND
            )
        # Создаю новую или обновляю старую позицию в корзине
        item, _ = BasketItem.objects.get_or_create(user=user, product=product)
        item.count += count

        # Проверяю, что на складе достаточно товара
        if product.count < item.count:
            log.warning(
                "User %d tried to add %d of product %d, but only %d in stock",
                user.id, count, product_id, product.count
            )
            return Response(
                {"error": "Not enough products in stock"}, HTTP_400_BAD_REQUEST
            )
        item.save()

        # Возвращаю обновлённую корзину
        items = BasketItem.objects.filter(user=user)
        serializer = OrderProductSerializer(items, many=True)
        return Response(serializer.data)

    def delete(self, request):
        """Удаление товара из корзины"""
        user = request.user
        product_id = request.data.get("id")
        count = int(request.data.get("count", 1))

        item = BasketItem.objects.filter(
            user=user, product_id=product_id
        ).first()

        # Проверяю, что товар существует
        if not item:
            log.warning(
                "User %d tried to delete product %d not in basket",
                user.id, product_id
            )
            return Response(
                {"message": "Product not found in basket"},
                HTTP_404_NOT_FOUND,
            )

        # Удаляю товар или уменьшаю его количество
        if item:
            if count >= item.count:
                item.delete()
            else:
                item.count -= count
                item.save()

        # Возвращаю обновлённую корзину
        items = BasketItem.objects.filter(user=user)
        serializer = OrderProductSerializer(items, many=True)
        return Response(serializer.data)


class OrdersView(APIView):
    """Вьюха для заказов пользователя"""

    def get(self, request):
        """Получение всех заказов по пользователю"""
        user = request.user
        orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Создание заказа на основе корзины"""
        user = request.user
        log.info(
            f"User {user.id} is creating an order. Basket: {request.data}"
        )

        fullName = getattr(user, "fullName", "")
        email = getattr(user, "email", "")
        phone = getattr(user, "phone", "")
        totalCost = 0
        totalCostWithDelivery = 0
        settings, _ = DeliverySettings.objects.get_or_create(id=1)

        # Получаю данные из запроса
        # (но во фронте запросы кривые, поэтому try except)
        try:
            deliveryType = request.data.get("deliveryType", "")
            paymentType = request.data.get("paymentType", "")
            status = request.data.get("status", "")
            city = request.data.get("city", "")
            address = request.data.get("address", "")
        except Exception:
            deliveryType = ""
            paymentType = ""
            status = ""
            city = ""
            address = ""

        # Считаю стоимость товаров в корзине
        basket_items = list(BasketItem.objects.filter(user=user))

        for item in basket_items:
            product = item.product
            count = item.count
            if product:
                totalCost += product.price * count

        delivery_cost = (
            settings.express_cost
            if deliveryType == "express"
            else settings.regular_cost
        )
        if totalCost >= settings.free_from:
            delivery_cost = 0
        totalCostWithDelivery = totalCost + delivery_cost

        # Создаю заказ
        order = Order.objects.create(
            user=user,
            fullName=fullName,
            email=email,
            phone=phone,
            deliveryType=deliveryType,
            paymentType=paymentType,
            totalCost=totalCostWithDelivery,
            status=status,
            city=city,
            address=address,
        )
        order.products.set(basket_items)
        order.save()
        log.info(
            "Order %d created for user %d with total %d",
            order.id, user.id, totalCostWithDelivery
        )
        return Response({"orderId": order.id}, HTTP_200_OK)


class OrderDetailView(APIView):
    """Вьюха деталей заказа"""

    def get(self, request, id):
        """Получение деталей заказа по id"""
        order = Order.objects.filter(id=id, user=request.user).first()
        if not order:
            return Response({"error": "Order not found"}, HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def post(self, request, id):
        """Обновление заказа и проведение оплаты"""
        order = Order.objects.filter(id=id, user=request.user).first()
        if not order:
            return Response({"error": "Order not found"}, HTTP_404_NOT_FOUND)

        # Проверяю наличие товаров в магазине
        for basket_item in order.products.all():
            product = basket_item.product
            if product.count < basket_item.count:
                order.status = "canceled"
                order.save()
                log.warning(
                    "Order %d canceled: not enough stock for product %d",
                    order.id, product.id
                )
                return Response(
                    {
                        "error": f'Not enough stock for product "{product.id}"'
                    },
                    HTTP_400_BAD_REQUEST,
                )

        # Обновляю данные по заказу
        order.deliveryType = request.data.get(
            "deliveryType", order.deliveryType
        )
        order.fullName = request.data.get("fullName", order.fullName)
        order.phone = request.data.get("phone", order.phone)
        order.paymentType = request.data.get("paymentType", order.paymentType)
        order.city = request.data.get("city", order.city)
        order.address = request.data.get("address", order.address)

        # Провожу оплату
        try:
            amount = {"value": str(order.totalCost), "currency": "RUB"}
            user_id = str(request.user.id)
            order_id = order.id
            response = requests.post(
                PAYMENT_URL,
                json={
                    "amount": amount,
                    "user_id": user_id,
                    "order_id": order_id,
                },
            )
            # Перенаправляю пользователя на оплату
            if response.status_code not in [200, 201, 202, 204]:
                raise requests.RequestException(f"Error: {response.text}")

            payment_url = response.json().get("confirmation_url")
            if not payment_url:
                raise requests.RequestException(
                    "No confirmation_url in response"
                )
            order.status = "confirmed"
            log.info(f"Order {order.id} payment confirmed for user {user_id}")

        except requests.RequestException as e:
            order.status = "canceled"
            log.error(f"Payment service error for order {order.id}: {e}")
            return Response(
                {"error": "Payment service is unavailable"},
                HTTP_400_BAD_REQUEST,
            )

        # После подтверждения заказа убираю товары со склада
        if order.status == "confirmed":
            log.info(
                f"Order {order.id} confirmed. Deducting products from stock."
            )
            for basket_item in order.products.all():
                product = basket_item.product
                product.count = max(product.count - basket_item.count, 0)
                product.save()
                log.info(
                    "Product %d stock updated: %d left after order %d",
                    product.id, product.count, order.id
                )
                basket_item.delete()
        order.save()

        # Очищаю корзину
        BasketItem.objects.filter(user=request.user).delete()

        return Response({"confirmation_url": payment_url}, HTTP_201_CREATED)


# Не используется, так как подключён платёжный сервис
class PaymentView(APIView):
    """Вьюха для эмуляции платёжной системы"""

    def post(self, request, id):
        """Обработка платежа по заказу"""
        order = Order.objects.filter(id=id, user=request.user).first()
        if not order:
            return Response({"error": "Order not found"}, HTTP_404_NOT_FOUND)

        number = str(request.data.get("number", ""))
        if not number.isdigit() or len(number) > 8 or int(number) % 2 != 0:
            order.save()
            return Response(
                {"error": "Invalid number: must be even and up to 8 digits."},
                HTTP_400_BAD_REQUEST,
            )

        if number[-1] == "0" or int(number) % 2 != 0:
            errors = [
                "Payment declined by bank.",
                "Insufficient funds.",
                "Card expired.",
                "Technical error. Try again later.",
            ]
            order.save()
            return Response(
                {"error": random.choice(errors)}, HTTP_400_BAD_REQUEST
            )
        else:
            order.status = "paid"
            order.save()
            return Response(
                {
                    "message": "Waiting for confirmation from payment system."
                },
                HTTP_200_OK,
            )
