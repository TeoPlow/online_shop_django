from django.test import TestCase
from rest_framework.test import APIClient
from user.models import Image
from product.models import (
    Category,
    Product,
    Tag,
    Review,
    SaleItem,
    Specification,
)


class ProductTestBase(TestCase):
    """
    Создание набора продуктов, их категории, тэги,
    спецификации, отзывы к ним, скидки и изображения для тестирования.
    """

    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.image = Image.objects.create(src="images/test.png", alt="картинка")
        cls.category = Category.objects.create(
            title="Электроника", image=cls.image
        )
        cls.tag1 = Tag.objects.create(name="Игровой")
        cls.tag2 = Tag.objects.create(name="Офисный")
        cls.spec = Specification.objects.create(name="Размер", value='27"')
        cls.review1 = Review.objects.create(
            author="User1", email="user1@mail.com", text="норм", rate=5
        )
        cls.review2 = Review.objects.create(
            author="User2", email="user2@mail.com", text="сойдёт", rate=4
        )
        cls.product1 = Product.objects.create(
            category=cls.category,
            title="Тестовый монитор 1",
            standart_price=123.45,
            count=10,
            description="Короткое описание",
            fullDescription="Полное описание техники - монитор",
            freeDelivery=True,
            rating=4,
            sort_index=1,
        )
        cls.product2 = Product.objects.create(
            category=cls.category,
            title="Тестовая клава 1",
            standart_price=100,
            count=2,
            description="Короткое описание",
            fullDescription="Полное описание техники - клава",
            freeDelivery=False,
            rating=4,
            limitedEdition=True,
            sort_index=1,
        )
        cls.sale1 = SaleItem.objects.create(
            product=cls.product1,
            salePrice=100.00,
            dateFrom="05-08",
            dateTo="05-20",
        )
        cls.product1.tags.add(cls.tag1)
        cls.product1.reviews.add(cls.review1, cls.review2)
        cls.product1.images.add(cls.image)
        cls.product1.specifications.add(cls.spec)

        cls.product2.tags.add(cls.tag2)
        cls.product2.images.add(cls.image)


class CategoryListViewTest(TestCase):
    def setUp(self):
        """
        Предустановка данных для тестирования списка категорий.
        """
        self.client = APIClient()
        self.image = Image.objects.create(
            src="images/test.png", alt="Test Image"
        )
        self.parent_category = Category.objects.create(
            title="Parent", image=self.image
        )
        self.sub_image = Image.objects.create(
            src="images/sub.png", alt="Sub Image"
        )
        self.sub_category = Category.objects.create(
            title="Sub", image=self.sub_image, parent=self.parent_category
        )

    def test_get_categories(self):
        """
        Тестирование получения категорий.
        """
        response = self.client.get("/api/categories")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)

        category = response.data[0]
        self.assertIn("id", category)
        self.assertIn("title", category)
        self.assertIn("image", category)
        self.assertIn("subcategories", category)

        if category["subcategories"]:
            subcat = category["subcategories"][0]
            self.assertIn("id", subcat)
            self.assertIn("title", subcat)
            self.assertIn("image", subcat)


class CatalogViewTest(ProductTestBase):
    def test_catalog_no_filters(self):
        """
        Тестирование каталога без фильтров.
        """
        response = self.client.get("/api/catalog")
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.data)
        self.assertEqual(len(response.data["items"]), 2)

    def test_catalog_filter_by_name(self):
        """
        Тестирование каталога с фильтром по названию.
        """
        response = self.client.get("/api/catalog?filter[name]=монитор")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(
            response.data["items"][0]["title"], "Тестовый монитор 1"
        )

    def test_catalog_filter_by_category(self):
        """
        Тестирование каталога с фильтром по категории.
        """
        response = self.client.get(f"/api/catalog?category={self.category.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["items"]), 2)

    def test_catalog_filter_by_tag(self):
        """
        Тестирование каталога с фильтром по тегу.
        """
        response = self.client.get(f"/api/catalog?tags[]={self.tag2.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(
            response.data["items"][0]["title"], "Тестовая клава 1"
        )

    def test_catalog_pagination(self):
        """
        Тестирование пагинации каталога.
        """
        response = self.client.get("/api/catalog?limit=1&currentPage=2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["currentPage"], 2)


class ProductsPopularViewTest(ProductTestBase):
    def test_popular_products(self):
        """
        Тестирование получения популярных продуктов.
        """
        response = self.client.get("/api/products/popular")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) == 2)


class ProductsLimitedViewTest(ProductTestBase):
    def test_limited_products(self):
        """
        Тестирование получения ограниченных по кол-ву продуктов.
        """
        response = self.client.get("/api/products/limited")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Тестовая клава 1")
        self.assertLessEqual(response.data[0]["count"], 2)


class SalesViewTest(ProductTestBase):
    def test_sales_list(self):
        """
        Тестирование получения списка товаров со скидкой.
        """
        response = self.client.get("/api/sales")
        self.assertEqual(response.status_code, 200)
        self.assertIn("items", response.data)
        self.assertEqual(response.data["currentPage"], 1)
        self.assertTrue(len(response.data["items"]) == 1)
        sale = response.data["items"][0]
        self.assertIn("id", sale)
        self.assertIn("title", sale)
        self.assertIn("price", sale)
        self.assertIn("salePrice", sale)
        self.assertIn("dateFrom", sale)
        self.assertIn("dateTo", sale)
        self.assertIn("images", sale)


class BannersViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Создание 12-ти продуктов. В баннер попадут только последние 10.
        """
        cls.client = APIClient()
        cls.image = Image.objects.create(src="images/test.png", alt="картинка")
        cls.category = Category.objects.create(
            title="категория", image=cls.image
        )
        cls.tag = Tag.objects.create(name="баннер")
        for i in range(12):
            product = Product.objects.create(
                category=cls.category,
                title=f"Продукт в баннере {i+1}",
                standart_price=100 + i,
                count=5,
                description="Описание",
                fullDescription="Полное описание",
                freeDelivery=True,
                rating=4.0 + i * 0.1,
            )
            product.images.add(cls.image)
            product.tags.add(cls.tag)

    def test_banners_limit(self):
        """
        Тестирование баннера.
        """
        response = self.client.get("/api/banners")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 10)
        for product in response.data:
            self.assertIn("id", product)
            self.assertIn("title", product)
            self.assertIn("images", product)


class ProductDetailViewTest(ProductTestBase):
    def test_product_detail(self):
        """
        Тестирование вывода детальной информации о продукте.
        """
        response = self.client.get(f"/api/product/{self.product1.id}")
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data["id"], self.product1.id)
        self.assertEqual(data["title"], self.product1.title)
        self.assertEqual(data["price"], self.product1.price)
        self.assertEqual(data["count"], self.product1.count)
        self.assertEqual(data["description"], self.product1.description)
        self.assertEqual(
            data["fullDescription"], self.product1.fullDescription
        )
        self.assertEqual(data["freeDelivery"], self.product1.freeDelivery)
        self.assertEqual(data["rating"], self.product1.rating)
        self.assertTrue(len(data["images"]) > 0)
        self.assertTrue(len(data["tags"]) > 0)
        self.assertIsInstance(data["tags"][0], dict)
        self.assertTrue(len(data["reviews"]) > 0)
        self.assertTrue(len(data["specifications"]) > 0)


class ProductReviewViewTest(ProductTestBase):
    def test_add_review(self):
        """
        Тестирование добавление отзывов к продуктам.
        """
        author = "челикс"
        text = "харош"
        data = {
            "author": author,
            "email": "user@ya.ru",
            "text": text,
            "rate": 5,
        }
        response = self.client.post(
            f"/api/product/{self.product1.id}/reviews", data, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) > 0)
        review = response.data[2]
        self.assertEqual(review["author"], author)
        self.assertEqual(review["rate"], 5)
        self.assertEqual(review["text"], text)

    def test_add_review_invalid(self):
        """
        Тестирование неверно отправленных отзывов.
        """
        data = {
            "author": "ашибачные данные",
            "email": "12312 ",
            "text": "232",
            "rate": "777",
        }
        response = self.client.post(
            f"/api/product/{self.product1.id}/reviews", data, format="json"
        )
        self.assertEqual(response.status_code, 400)


class TagListViewTest(ProductTestBase):
    def test_get_all_tags(self):
        """
        Тестирование получения всех тэгов.
        """
        response = self.client.get("/api/tags")
        self.assertEqual(response.status_code, 200)
        tag_names = [tag["name"] for tag in response.data]
        self.assertIn("Игровой", tag_names)
        self.assertIn("Офисный", tag_names)

    def test_get_tags_by_category(self):
        """
        Тестирование получения всех тэгов по категории.
        """
        response = self.client.get(f"/api/tags?category={self.category.id}")
        self.assertEqual(response.status_code, 200)
        tag_names = [tag["name"] for tag in response.data]
        self.assertIn("Игровой", tag_names)
        self.assertIn("Офисный", tag_names)
