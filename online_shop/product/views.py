import logging
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from .models import (
    Category,
    Product,
    Tag,
    SaleItem,
    Review,
)
from .serializers import (
    CategorySerializer,
    ProductShortSerializer,
    ProductFullSerializer,
    SaleItemSerializer,
    ReviewSerializer,
    TagSerializer,
)


log = logging.getLogger(__name__)


class CategoryListView(APIView):
    """Вьюха для списка категорий"""

    def get(self, request):
        categories = Category.objects.filter(parent__isnull=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CatalogView(APIView):
    """Вьюха для каталога продуктов"""

    def get(self, request):
        products = Product.objects.all()

        # Фильтрация по названию
        name = request.query_params.get("filter[name]")

        if name:
            products = products.filter(title__icontains=name)

        # Фильтрация по цене
        min_price = request.query_params.get("filter[minPrice]")
        max_price = request.query_params.get("filter[maxPrice]")

        if min_price is not None and min_price != "":
            products = products.filter(standart_price__gte=float(min_price))
        if max_price is not None and max_price != "":
            products = products.filter(standart_price__lte=float(max_price))

        # Фильтрация по доставке и доступности
        free_delivery = request.query_params.get("filter[freeDelivery]")
        available = request.query_params.get("filter[available]")

        if free_delivery is not None and free_delivery != "":
            if free_delivery.lower() == "true":
                products = products.filter(freeDelivery=True)
        if available is not None and available != "":
            if available.lower() == "true":
                products = products.filter(count__gt=0)

        # Фильтрация по категории
        category = request.query_params.get("category")
        if category:
            products = products.filter(category=category)

        # Фильтрация по тегам
        tags = request.query_params.getlist("tags[]")
        if tags:
            products = products.filter(tags__id__in=tags).distinct()

        # Сортировка
        sort = request.query_params.get("sort", "date")
        sort_type = request.query_params.get("sortType", "dec")
        sort_map = {
            "rating": "rating",
            "price": "standart_price",
            "reviews": "reviews",
            "date": "date",
        }
        sort_field = sort_map.get(sort, "date")
        if sort_type == "dec":
            sort_field = "-" + sort_field
        products = products.order_by(sort_field)

        # Пагинация
        limit = int(request.query_params.get("limit", 20))
        page = int(request.query_params.get("currentPage", 1))

        total = products.count()
        last_page = (total + limit - 1) // limit
        start = (page - 1) * limit
        end = start + limit

        serializer = ProductShortSerializer(products[start:end], many=True)
        log.info(f"Paginating products: page {page}, limit {limit}")
        return Response(
            {
                "items": serializer.data,
                "currentPage": page,
                "lastPage": last_page,
            }
        )


class ProductsPopularView(APIView):
    """Вьюха для популярных продуктов"""

    def get(self, request):
        products = Product.objects.order_by("sort_index", "-rating")[:8]
        serializer = ProductShortSerializer(products, many=True)
        return Response(serializer.data)


class ProductsLimitedView(APIView):
    """Вьюха для лимитированных продуктов"""

    def get(self, request):
        products = Product.objects.filter(limitedEdition=True).order_by(
            "sort_index"
        )[:16]
        serializer = ProductShortSerializer(products, many=True)
        return Response(serializer.data)


class SalesView(APIView):
    """Вьюха для акций"""

    def get(self, request):
        sales = SaleItem.objects.all().order_by("-dateFrom")
        limit = int(request.query_params.get("limit", 20))
        page = int(request.query_params.get("currentPage", 1))
        total = sales.count()
        last_page = (total + limit - 1) // limit
        start = (page - 1) * limit
        end = start + limit

        serializer = SaleItemSerializer(sales[start:end], many=True)
        return Response(
            {
                "items": serializer.data,
                "currentPage": page,
                "lastPage": last_page,
            }
        )


class BannersView(APIView):
    """Вьюха для баннеров"""

    def get(self, request):
        products = Product.objects.all()[:10]
        serializer = ProductShortSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailView(RetrieveAPIView):
    """Вьюха для деталей продукта"""

    queryset = Product.objects.all()
    serializer_class = ProductFullSerializer
    lookup_field = "id"


class ProductReviewView(APIView):
    """Вьюха для отзывов о продукте"""

    def post(self, request, id):
        product = Product.objects.filter(id=id).first()
        if not product:
            log.warning(f"Review creation failed: product {id} not found")
            return Response({"error": "Product not found"}, status=404)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = Review.objects.create(
                author=serializer.validated_data["author"],
                email=serializer.validated_data["email"],
                text=serializer.validated_data["text"],
                rate=serializer.validated_data["rate"],
            )
            product.reviews.add(review)
            product.save()
            log.info(
                f"Review added for product {product.id} by {review.author}"
            )
            reviews = product.reviews.all()
            out_serializer = ReviewSerializer(reviews, many=True)
            return Response(out_serializer.data, status=200)
        log.warning(
            f"Review creation failed for product {id}: {serializer.errors}"
        )
        return Response(serializer.errors, status=400)


class TagListView(APIView):
    """Вьюха для списка тегов"""

    def get(self, request):
        category_id = request.query_params.get("category")
        if category_id:
            tags = Tag.objects.filter(
                products__category_id=category_id
            ).distinct()
        else:
            tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)
