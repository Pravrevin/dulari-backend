from django.contrib import admin
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "product_id", "product_name", "mrp", "manufacturer_name",
        "is_discontinued", "is_new_launch", "is_trending_near_you", "is_in_spotlight",
    ]
    list_filter = ["is_discontinued", "is_new_launch", "is_trending_near_you", "is_in_spotlight"]
    search_fields = ["product_name", "manufacturer_name"]
    list_editable = ["is_new_launch", "is_trending_near_you", "is_in_spotlight"]
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "alt_text"]
    search_fields = ["product__product_name"]
