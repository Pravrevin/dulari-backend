from rest_framework import generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer, ProductListSerializer


class ProductListView(generics.ListAPIView):
    """
    GET /api/products/
    Optional query params:
      ?is_new_launch=true
      ?is_trending_near_you=true
      ?is_in_spotlight=true
      ?search=<name>
    """
    serializer_class = ProductListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product_name", "manufacturer_name", "short_composition1", "short_composition2"]
    ordering_fields = ["product_name", "mrp"]

    def get_queryset(self):
        queryset = Product.objects.prefetch_related("images")
        is_new_launch = self.request.query_params.get("is_new_launch")
        is_trending = self.request.query_params.get("is_trending_near_you")
        is_spotlight = self.request.query_params.get("is_in_spotlight")
        is_discontinued = self.request.query_params.get("is_discontinued")

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
    queryset = Product.objects.prefetch_related("images")
    serializer_class = ProductSerializer
    lookup_field = "product_id"


@api_view(["GET"])
def new_launches(request):
    """GET /api/products/new-launches/ — all products flagged as new launch."""
    products = Product.objects.prefetch_related("images").filter(is_new_launch=True)
    serializer = ProductListSerializer(products, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def trending_near_you(request):
    """GET /api/products/trending-near-you/ — all products flagged as trending."""
    products = Product.objects.prefetch_related("images").filter(is_trending_near_you=True)
    serializer = ProductListSerializer(products, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
def in_the_spotlight(request):
    """GET /api/products/in-the-spotlight/ — all products flagged as spotlight."""
    products = Product.objects.prefetch_related("images").filter(is_in_spotlight=True)
    serializer = ProductListSerializer(products, many=True, context={"request": request})
    return Response(serializer.data)
