from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
)
from product.models import Product

from .models import (
    BasketItem,
    Order,
    DeliverySettings,
    )
from .serializers import (
    OrderProductSerializer,
    OrderSerializer,
)
import logging
import random

log = logging.getLogger(__name__)


class BasketView(APIView):
    def get(self, request):
        try:
            user = request.user
            items = BasketItem.objects.filter(user=user, orders__isnull=True)
            serializer = OrderProductSerializer(items, many=True)
            return Response(serializer.data)
        except TypeError:
            return Response({'message': 'User don`t have a basket, is anonymous'}, HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        product_id = request.data.get('id')
        count = int(request.data.get('count', 1))
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({'message': 'Product not found'}, HTTP_404_NOT_FOUND)
        item, created = BasketItem.objects.get_or_create(user=user, product=product)
        item.count += count
        if product.count < item.count:
            return Response({'error': 'Not enough products in stock'}, HTTP_400_BAD_REQUEST)
        item.save()
        items = BasketItem.objects.filter(user=user)
        serializer = OrderProductSerializer(items, many=True)
        return Response(serializer.data)

    def delete(self, request):
        user = request.user
        product_id = request.data.get('id')
        count = int(request.data.get('count', 1))
        item = BasketItem.objects.filter(user=user, product_id=product_id).first()
        if item:
            if count >= item.count:
                item.delete()
            else:
                item.count -= count
                item.save()
        items = BasketItem.objects.filter(user=user)
        serializer = OrderProductSerializer(items, many=True)
        return Response(serializer.data)


class OrdersView(APIView):
    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.user
        basket = request.data
        fullName = getattr(user, 'fullName', '')
        email = getattr(user, 'email', '')
        phone = getattr(user, 'phone', '')
        totalCostWithDelivery = 0
        settings, _ = DeliverySettings.objects.get_or_create(id=1)

        try:
            deliveryType = request.data.get('deliveryType')
            paymentType = request.data.get('paymentType')
            status = request.data.get('status')
            city = request.data.get('city')
            address = request.data.get('address')
        except:
            deliveryType = ''
            paymentType = ''
            status = ''
            city = ''
            address = ''

        totalCost = 0
        basket_items = []
        for item in basket:
            product_id = item.get('id')
            count = item.get('count', 1)
            product = Product.objects.filter(id=product_id).first()
            if product:
                totalCost += product.price * count
                basket_item = BasketItem.objects.create(user=user, product=product, count=count)
                basket_items.append(basket_item)

                delivery_cost = settings.express_cost if deliveryType == 'express' else settings.regular_cost
                if totalCost >= settings.free_from:
                    delivery_cost = 0
                totalCostWithDelivery = totalCost + delivery_cost

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
        basket_items_to_delete = BasketItem.objects.filter(
            user=user
        ).exclude(orders__isnull=False)
        basket_items_to_delete.delete()
        order.save()
        return Response({'orderId': order.id}, HTTP_200_OK)


class OrderDetailView(APIView):
    def get(self, request, id):
        order = Order.objects.filter(id=id, user=request.user).first()
        if not order:
            return Response({'error': 'Order not found'}, HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def post(self, request, id):
        order = Order.objects.filter(id=id, user=request.user).first()
        if not order:
            return Response({'error': 'Order not found'}, HTTP_404_NOT_FOUND)

        # Проверяем наличие товаров в магазине
        for basket_item in order.products.all():
            product = basket_item.product
            if product.count < basket_item.count:
                order.status = 'canceled'
                order.save()
                return Response(
                    {'error': f'Not enough stock for product "{product.title}"'},
                    HTTP_400_BAD_REQUEST
                )

        # Обновляем данные по заказу
        order.deliveryType = request.data.get('deliveryType', order.deliveryType)
        order.paymentType = request.data.get('paymentType', order.paymentType)
        order.city = request.data.get('city', order.city)
        order.address = request.data.get('address', order.address)

        order.status = 'confirmed'

        # После подтверждения заказа убираю товары сос клада
        for basket_item in order.products.all():
            product = basket_item.product
            product.count = max(product.count - basket_item.count, 0)
            product.save()
        order.save()

        return Response({'orderId': id}, HTTP_200_OK)


class PaymentView(APIView):
    def post(self, request, id):
        order = Order.objects.filter(id=id, user=request.user).first()
        if not order:
            return Response({'error': 'Order not found'}, HTTP_404_NOT_FOUND)

        number = str(request.data.get('number', ''))
        # Валидация: чётный, не длиннее 8 цифр
        if not number.isdigit() or len(number) > 8 or int(number) % 2 != 0:
            order.save()
            return Response({'error': 'Invalid number: must be even and up to 8 digits.'}, HTTP_400_BAD_REQUEST)

        # "Процесс" оплаты (эмулируем очередь и сервис)
        if number[-1] == '0' or int(number) % 2 != 0:
            # Ошибка оплаты (случайная)
            errors = [
                'Payment declined by bank.',
                'Insufficient funds.',
                'Card expired.',
                'Technical error. Try again later.'
            ]
            order.save()
            return Response({'error': random.choice(errors)}, HTTP_400_BAD_REQUEST)
        else:
            # Оплата подтверждена
            order.status = 'paid'
            order.save()
            return Response({'message': 'Waiting for payment confirmation from payment system.'}, HTTP_200_OK)
