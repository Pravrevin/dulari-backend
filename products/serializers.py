from rest_framework import serializers
from .models import Category, Product, ProductImage, DealOfTheDay, SuperSavingDeal, Combo, ProductFeature, GenericMedicine


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "image", "count_of_products"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

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
            "category",
            "is_new_launch",
            "is_trending_near_you",
            "is_in_spotlight",
            "images",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

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
            "category",
            "is_new_launch",
            "is_trending_near_you",
            "is_in_spotlight",
            "images",
        ]


class DealOfTheDaySerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    time_remaining_seconds = serializers.SerializerMethodField()

    class Meta:
        model = DealOfTheDay
        fields = [
            "id",
            "product",
            "discount_percentage",
            "discounted_price",
            "offer_ends_at",
            "is_active",
            "time_remaining_seconds",
        ]

    def get_time_remaining_seconds(self, obj):
        from django.utils import timezone
        delta = obj.offer_ends_at - timezone.now()
        return max(int(delta.total_seconds()), 0)


class SuperSavingDealSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = SuperSavingDeal
        fields = [
            "id",
            "product",
            "discount_percentage",
            "discounted_price",
            "is_active",
        ]


class ProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = ["description", "uses", "benefits", "side_effects", "how_to_use", "substitutes"]


class GenericMedicineSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = GenericMedicine
        fields = [
            "generic_product_id",
            "name",
            "brand",
            "mrp",
            "discount_percentage",
            "image_url",
            "product_id",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ComboSerializer(serializers.ModelSerializer):
    product1 = ProductListSerializer(read_only=True)
    product2 = ProductListSerializer(read_only=True)

    class Meta:
        model = Combo
        fields = [
            "id",
            "combo_name",
            "product1",
            "product2",
            "tags",
            "combo_price",
            "is_active",
        ]
