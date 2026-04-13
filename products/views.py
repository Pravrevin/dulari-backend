from django.utils import timezone
from django.db.models import FloatField, Value
from django.db.models.functions import Greatest, Coalesce
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework import generics, filters
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from .models import Category, Product, DealOfTheDay, SuperSavingDeal, Combo, ProductFeature, GenericMedicine
from .serializers import CategorySerializer, ProductSerializer, ProductListSerializer, DealOfTheDaySerializer, SuperSavingDealSerializer, ComboSerializer, ProductFeatureSerializer, GenericMedicineSerializer


class CategoryListView(generics.ListAPIView):
    """GET /api/categories/"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListView(generics.ListAPIView):
    """
    GET /api/products/
    Optional query params:
      ?category_id=<id>
      ?is_new_launch=true
      ?is_trending_near_you=true
      ?is_in_spotlight=true
      ?is_discontinued=false
      ?search=<name>
    """
    serializer_class = ProductListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product_name", "manufacturer_name", "short_composition1", "short_composition2"]
    ordering_fields = ["product_name", "mrp"]

    def get_queryset(self):
        queryset = Product.objects.select_related("category").prefetch_related("images")

        category_id = self.request.query_params.get("category_id")
        is_new_launch = self.request.query_params.get("is_new_launch")
        is_trending = self.request.query_params.get("is_trending_near_you")
        is_spotlight = self.request.query_params.get("is_in_spotlight")
        is_discontinued = self.request.query_params.get("is_discontinued")

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if is_new_launch and is_new_launch.lower() == "true":
            queryset = queryset.filter(is_new_launch=True)
        if is_trending and is_trending.lower() == "true":
            queryset = queryset.filter(is_trending_near_you=True)
        if is_spotlight and is_spotlight.lower() == "true":
            queryset = queryset.filter(is_in_spotlight=True)
        if is_discontinued is not None:
            queryset = queryset.filter(is_discontinued=is_discontinued.lower() == "true")

        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    """GET /api/products/<product_id>/"""
    queryset = Product.objects.select_related("category").prefetch_related("images")
    serializer_class = ProductSerializer
    lookup_field = "product_id"


class CategoryProductListView(generics.ListAPIView):
    """
    GET /api/categories/<category_id>/products/
    Returns all products for a given category.
    Optional query params:
      ?search=<name>
      ?ordering=product_name | mrp
      ?is_discontinued=true | false
    """
    serializer_class = ProductListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product_name", "manufacturer_name", "short_composition1", "short_composition2"]
    ordering_fields = ["product_name", "mrp"]

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        if not Category.objects.filter(pk=category_id).exists():
            raise NotFound(detail=f"Category with id {category_id} not found.")

        queryset = Product.objects.select_related("category").prefetch_related("images").filter(category_id=category_id)

        is_discontinued = self.request.query_params.get("is_discontinued")
        if is_discontinued is not None:
            queryset = queryset.filter(is_discontinued=is_discontinued.lower() == "true")

        return queryset


class DealsOfTheDayListView(generics.ListAPIView):
    """
    GET /api/deals-of-the-day/
    Returns all active deals that have not yet expired.
    """
    serializer_class = DealOfTheDaySerializer

    def get_queryset(self):
        return (
            DealOfTheDay.objects
            .select_related("product__category")
            .prefetch_related("product__images")
            .filter(is_active=True, offer_ends_at__gt=timezone.now())
            .order_by("offer_ends_at")
        )


class SuperSavingDealsListView(generics.ListAPIView):
    """
    GET /api/super-saving-deals/
    Returns all active super saving deals.
    """
    serializer_class = SuperSavingDealSerializer

    def get_queryset(self):
        return (
            SuperSavingDeal.objects
            .select_related("product__category")
            .prefetch_related("product__images")
            .filter(is_active=True)
            .order_by("-discount_percentage")
        )


class ComboListView(generics.ListAPIView):
    """
    GET /api/combos/
    Returns all active combos with their two linked products.
    Optional query params:
      ?tag=pain_relief  — filter combos that contain the given tag
    """
    serializer_class = ComboSerializer

    def get_queryset(self):
        queryset = (
            Combo.objects
            .select_related("product1__category", "product2__category")
            .prefetch_related("product1__images", "product2__images")
            .filter(is_active=True)
        )
        tag = self.request.query_params.get("tag")
        if tag:
            # JSONField contains filter: tag must appear in the tags list
            queryset = queryset.filter(tags__contains=[tag])
        return queryset


class ComboDetailView(generics.RetrieveAPIView):
    """GET /api/combos/<id>/"""
    serializer_class = ComboSerializer
    queryset = (
        Combo.objects
        .select_related("product1__category", "product2__category")
        .prefetch_related("product1__images", "product2__images")
    )


class _SearchPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


_SORT_MAP = {
    "price_asc":  "mrp",
    "price_desc": "-mrp",
    "name_asc":   "product_name",
    "name_desc":  "-product_name",
}


class ProductSearchView(generics.ListAPIView):
    """
    GET /api/search/

    Unified search + filter endpoint. Every parameter is optional — combine
    freely. When ?q= is supplied, fuzzy trigram matching (pg_trgm) is applied
    across product name, brand, and category name, handling misspellings.

    ── Search ──────────────────────────────────────────────────────────────
      q                  Fuzzy search term (min 2 chars).
                         Matches product name, manufacturer / brand, category.

    ── Filters ─────────────────────────────────────────────────────────────
      category_id        Filter by category (integer id).
      mrp_min            Minimum MRP price (inclusive).
      mrp_max            Maximum MRP price (inclusive).
      is_discontinued    true | false  (omit to return both).
      is_new_launch      true          Return only new-launch products.
      is_trending_near_you true        Return only trending products.
      is_in_spotlight    true          Return only spotlight products.

    ── Sorting ─────────────────────────────────────────────────────────────
      sort               relevance (default when q given) | name_asc |
                         name_desc | price_asc | price_desc

    ── Pagination ──────────────────────────────────────────────────────────
      page               Page number (default 1).
      page_size          Results per page (default 20, max 100).
    """

    serializer_class = ProductListSerializer
    pagination_class = _SearchPagination
    SIMILARITY_THRESHOLD = 0.15

    def get_queryset(self):
        p = self.request.query_params
        query = p.get("q", "").strip()

        qs = Product.objects.select_related("category").prefetch_related("images")

        # ── Fuzzy search ──────────────────────────────────────────────────
        if query:
            if len(query) < 2:
                raise ValidationError({"q": "Search term must be at least 2 characters."})
            qs = (
                qs.annotate(
                    sim_name=TrigramSimilarity("product_name", query),
                    sim_brand=TrigramSimilarity("manufacturer_name", query),
                    sim_category=Coalesce(
                        TrigramSimilarity("category__name", query),
                        Value(0.0, output_field=FloatField()),
                    ),
                    similarity=Greatest("sim_name", "sim_brand", "sim_category"),
                )
                .filter(similarity__gte=self.SIMILARITY_THRESHOLD)
            )

        # ── Filters ───────────────────────────────────────────────────────
        category_id = p.get("category_id")
        mrp_min     = p.get("mrp_min")
        mrp_max     = p.get("mrp_max")
        discontinued = p.get("is_discontinued")
        new_launch   = p.get("is_new_launch")
        trending     = p.get("is_trending_near_you")
        spotlight    = p.get("is_in_spotlight")

        if category_id:
            qs = qs.filter(category_id=category_id)
        if mrp_min:
            try:
                qs = qs.filter(mrp__gte=float(mrp_min))
            except ValueError:
                raise ValidationError({"mrp_min": "Must be a number."})
        if mrp_max:
            try:
                qs = qs.filter(mrp__lte=float(mrp_max))
            except ValueError:
                raise ValidationError({"mrp_max": "Must be a number."})
        if discontinued is not None:
            qs = qs.filter(is_discontinued=discontinued.lower() == "true")
        if new_launch and new_launch.lower() == "true":
            qs = qs.filter(is_new_launch=True)
        if trending and trending.lower() == "true":
            qs = qs.filter(is_trending_near_you=True)
        if spotlight and spotlight.lower() == "true":
            qs = qs.filter(is_in_spotlight=True)

        # ── Sort ──────────────────────────────────────────────────────────
        sort = p.get("sort", "")
        if sort in _SORT_MAP:
            qs = qs.order_by(_SORT_MAP[sort])
        elif query:
            qs = qs.order_by("-similarity")   # default: best match first
        else:
            qs = qs.order_by("product_name")  # no query → alphabetical

        return qs


class ProductFeatureView(generics.RetrieveAPIView):
    """GET /api/products/<product_id>/features/"""
    serializer_class = ProductFeatureSerializer
    lookup_field = "product_id"

    def get_object(self):
        product_id = self.kwargs["product_id"]
        try:
            return ProductFeature.objects.select_related("product").get(product_id=product_id)
        except ProductFeature.DoesNotExist:
            raise NotFound(detail=f"No features found for product with id {product_id}.")


class GenericMedicineListView(generics.ListAPIView):
    """
    GET /api/products/<product_id>/generic-medicines/

    Returns all generic medicines linked to the given product, including a
    fully-qualified image URL.

    Example response:
    [
      {
        "generic_product_id": 1,
        "name": "Amoxycillin 500mg + Clavulanic Acid 125mg Tablet",
        "brand": "GeneriPharma",
        "mrp": "145.00",
        "image_url": "http://localhost:8000/media/generic_medicines/gen_1.jpg",
        "product_id": 1
      }
    ]
    """
    serializer_class = GenericMedicineSerializer

    def get_queryset(self):
        product_id = self.kwargs["product_id"]
        if not Product.objects.filter(pk=product_id).exists():
            raise NotFound(detail=f"Product with id {product_id} not found.")
        return GenericMedicine.objects.filter(product_id=product_id).order_by("name")


class BrandListView(generics.ListAPIView):
    """
    GET /api/brands/
    Returns a sorted list of all distinct manufacturer names.
    """
    def list(self, request, *args, **kwargs):
        brands = (
            Product.objects
            .values_list("manufacturer_name", flat=True)
            .distinct()
            .order_by("manufacturer_name")
        )
        return Response(list(brands))


class BrandProductListView(generics.ListAPIView):
    """
    GET /api/brands/<manufacturer_name>/products/
    Returns all products for the given manufacturer name (case-insensitive).
    Optional query params:
      ?is_discontinued=true | false
      ?ordering=product_name | mrp
    """
    serializer_class = ProductListSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["product_name", "mrp"]

    def get_queryset(self):
        manufacturer_name = self.kwargs["manufacturer_name"]
        queryset = (
            Product.objects
            .select_related("category")
            .prefetch_related("images")
            .filter(manufacturer_name__iexact=manufacturer_name)
        )
        if not queryset.exists():
            raise NotFound(detail=f"No products found for brand '{manufacturer_name}'.")

        is_discontinued = self.request.query_params.get("is_discontinued")
        if is_discontinued is not None:
            queryset = queryset.filter(is_discontinued=is_discontinued.lower() == "true")

        return queryset


@api_view(["GET"])
def new_launches(request):
    """GET /api/products/new-launches/"""
    products = Product.objects.select_related("category").prefetch_related("images").filter(is_new_launch=True)
    serializer = ProductListSerializer(products, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def trending_near_you(request):
    """GET /api/products/trending-near-you/"""
    products = Product.objects.select_related("category").prefetch_related("images").filter(is_trending_near_you=True)
    serializer = ProductListSerializer(products, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def in_the_spotlight(request):
    """GET /api/products/in-the-spotlight/"""
    products = Product.objects.select_related("category").prefetch_related("images").filter(is_in_spotlight=True)
    serializer = ProductListSerializer(products, many=True, context={"request": request})
    return Response(serializer.data)
