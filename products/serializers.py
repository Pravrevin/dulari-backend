from rest_framework import serializers
from .models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "mrp",
            "is_discontinued",
            "manufacturer_name",
            "pack_size_label",
            "short_composition1",
            "short_composition2",
            "is_new_launch",
            "is_trending_near_you",
            "is_in_spotlight",
            "images",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "product_name",
            "mrp",
            "is_discontinued",
            "manufacturer_name",
            "pack_size_label",
            "short_composition1",
            "short_composition2",
            "is_new_launch",
            "is_trending_near_you",
            "is_in_spotlight",
            "images",
        ]
