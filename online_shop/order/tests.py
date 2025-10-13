import logging
from rest_framework.test import APITestCase
from user.models import User, Image
from product.models import Category, Product
from .models import Order, OrderItem


log = logging.getLogger(__name__)


class BasketViewTest(APITestCase):
    def setUp(self):
        """
        Предустановка пользователя и продуктов для тестирования.
        """
        self.user = User.objects.create_user(
            email="test@mail.com",
            username="testuser",
            password="testpass",
            fullName="Test User",
        )
        self.image = Image.objects.create(
            src="images/test.png", alt="картинка"
        )
        self.category = Category.objects.create(
            title="Мониторы", image=self.image
        )
        self.product = Product.objects.create(
            category=self.category,
            title="Тестовый монитор",
            standart_price=123.45,
            count=10,
            description="Короткое описание",
            fullDescription="Полное описание",
            freeDelivery=True,
            rating=4.5,
        )
        self.product.images.add(self.image)
        self.client.force_authenticate(user=self.user)

    def test_get_empty_basket(self):
        """
        Тестирование получения пустой корзины.
        """
        response = self.client.get("/api/basket")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_add_item_to_basket(self):
        """
        Тестирование добавления товара в корзину.
        """
        response = self.client.post(
            "/api/basket", {"id": self.product.id, "count": 2}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["count"], 2)
        self.assertEqual(response.data[0]["title"], self.product.title)

    def test_update_item_count(self):
        """
        Тестирование обновления количества товара в корзине.
        """
        response = self.client.post(
            "/api/basket", {"id": self.product.id, "count": 5}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["count"], 5)

    def test_delete_item_from_basket(self):
        """
        Тестирование удаления товара из корзины.
        """
        self.client.post(
            "/api/basket", {"id": self.product.id, "count": 2}, format="json"
        )
        response = self.client.delete(
            "/api/basket", {"id": self.product.id, "count": 2}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_partial_delete_item(self):
        """
        Тестирование частичного удаления товара из корзины.
        """
        self.client.post(
            "/api/basket", {"id": self.product.id, "count": 5}, format="json"
        )
        response = self.client.delete(
            "/api/basket", {"id": self.product.id, "count": 3}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["count"], 2)


class OrdersViewTest(APITestCase):
    def setUp(self):
        """
        Предустановка пользователя и продуктов для тестирования.
        """
        self.user = User.objects.create_user(
            email="test@mail.com",
            username="testuser",
            password="testpass",
            fullName="Test User",
        )
        self.image = Image.objects.create(
            src="images/test.png", alt="картинка"
        )
        self.category = Category.objects.create(
            title="Мониторы", image=self.image
        )
        self.product1 = Product.objects.create(
            category=self.category,
            title="Монитор",
            standart_price=100.00,
            count=5,
            description="Короткое описание",
            fullDescription="Полное описание",
            freeDelivery=True,
            rating=4.5,
        )
        self.product2 = Product.objects.create(
            category=self.category,
            title="Клавиатура",
            standart_price=50.00,
            count=10,
            description="Короткое описание",
            fullDescription="Полное описание",
            freeDelivery=False,
            rating=4.0,
        )
        self.product1.images.add(self.image)
        self.product2.images.add(self.image)
        self.client.force_authenticate(user=self.user)

    def test_get_empty_orders(self):
        """
        Тестирование получения пустого списка заказов.
        """
        response = self.client.get("/api/orders")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_create_order(self):
        """
        Тестирование создания заказа.
        """
        self.client.post(
            "/api/basket", {"id": self.product1.id, "count": 2}, format="json"
        )
        self.client.post(
            "/api/basket", {"id": self.product2.id, "count": 1}, format="json"
        )

        response = self.client.post("/api/orders", {}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("orderId", response.data)
        order_id = response.data["orderId"]

        order = Order.objects.get(id=order_id)
        self.assertEqual(order.user, self.user)
        self.assertEqual(
            order.totalCost,
            self.product1.price * 2 + self.product2.price * 1,
        )
        self.assertEqual(order.products.count(), 2)

    def test_get_orders_after_create(self):
        """
        Тестирование получения заказов после создания.
        """
        self.client.post(
            "/api/basket", {"id": self.product1.id, "count": 2}, format="json"
        )
        self.client.post("/api/orders", {}, format="json")
        response = self.client.get("/api/orders")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        order = response.data[0]
        self.assertEqual(order["fullName"], self.user.fullName)
        self.assertEqual(order["email"], self.user.email)
        self.assertEqual(order["products"][0]["title"], self.product1.title)


class OrderDetailViewTest(APITestCase):
    def setUp(self):
        """
        Предустановка пользователя и продуктов для тестирования.
        """
        self.user = User.objects.create_user(
            email="test@mail.com",
            username="testuser",
            password="testpass",
            fullName="Test User",
        )
        self.image = Image.objects.create(
            src="images/test.png", alt="картинка"
        )
        self.category = Category.objects.create(
            title="Мониторы", image=self.image
        )
        self.product = Product.objects.create(
            category=self.category,
            title="Монитор",
            standart_price=123.45,
            count=5,
            description="Короткое описание",
            fullDescription="Полное описание",
            freeDelivery=True,
            rating=4,
        )
        self.client.force_authenticate(user=self.user)

        self.product.images.add(self.image)
        self.order = Order.objects.create(
            user=self.user,
            fullName=self.user.fullName,
            email=self.user.email,
            phone="1234567890",
            deliveryType="express",
            paymentType="online",
            totalCost=self.product.price * 2,
            status="accepted",
            city="Москва",
            address="Пушкина, колотушкина, 8",
        )
        self.basket_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            count=2,
        )
        self.order.products.add(self.basket_item)

    def test_get_order_detail(self):
        """
        Тестирование получения деталей заказа.
        """
        response = self.client.get(f"/api/order/{self.order.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.order.id)
        self.assertEqual(response.data["fullName"], self.user.fullName)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(
            response.data["deliveryType"], self.order.deliveryType
        )
        self.assertEqual(
            response.data["products"][0]["title"], self.product.title
        )

    def test_get_order_not_found(self):
        """
        Тестирование получения заказа, которого не существует.
        """
        response = self.client.get("/api/order/9999999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)

    def test_confirm_order_not_found(self):
        """
        Тестирование подтверждения несуществующего заказа.
        """
        response = self.client.post("/api/order/9999999")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)


# Отключено, так как подключён внешний платёжный шлюз

# class PaymentViewTest(APITestCase):
#     payment_data = {
#         "number": "12345678",
#         "name": "Test User",
#         "month": "02",
#         "year": "2025",
#         "code": "123",
#     }

#     def setUp(self):
#         """
#         Предустановка пользователя и продуктов для тестирования.
#         """
#         self.user = User.objects.create_user(
#             email="test@mail.com",
#             username="testuser",
#             password="testpass",
#             fullName="Test User",
#         )
#         self.image = Image.objects.create(
#             src="images/test.png", alt="Test Image"
#         )
#         self.category = Category.objects.create(
#             title="Мониторы", image=self.image
#         )
#         self.product = Product.objects.create(
#             category=self.category,
#             title="Монитор",
#             standart_price=100.00,
#             count=5,
#             description="desc",
#             fullDescription="full",
#             freeDelivery=True,
#             rating=4.5,
#         )
#         self.client.force_authenticate(user=self.user)

#         self.product.images.add(self.image)
#         self.basket_item = BasketItem.objects.create(
#             user=self.user, product=self.product, count=2
#         )
#         self.order = Order.objects.create(
#             user=self.user,
#             fullName=self.user.fullName,
#             email=self.user.email,
#             phone="1234567890",
#             deliveryType="free",
#             paymentType="online",
#             totalCost=self.product.price * 2,
#             status="accepted",
#             city="Moscow",
#             address="Red Square 1",
#         )
#         self.order.products.add(self.basket_item)

#     def test_payment_success(self):
#         """
#         Тестирование успешного платежа.
#         """
#         response = self.client.post(
#             f"/api/payment/{self.order.id}", self.payment_data, format="json"
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertIn("message", response.data)
#         self.order.refresh_from_db()
#         self.assertEqual(self.order.status, "paid")

#     def test_payment_order_not_found(self):
#         """
#         Тестирование получения заказа, которого не существует.
#         """
#         response = self.client.post(
#             "/api/payment/9999999", self.payment_data, format="json"
#         )
#         self.assertEqual(response.status_code, 404)
#         self.assertIn("error", response.data)
