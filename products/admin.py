from django.contrib import admin
from .models import Category, Product, ProductImage, DealOfTheDay, SuperSavingDeal, Combo, ProductFeature, GenericMedicine


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description"]
    search_fields = ["name"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class GenericMedicineInline(admin.TabularInline):
    model = GenericMedicine
    extra = 0
    fields = ["name", "brand", "mrp", "image"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "product_id", "product_name", "mrp", "manufacturer_name", "category",
        "is_discontinued", "is_new_launch", "is_trending_near_you", "is_in_spotlight",
    ]
    list_filter = ["category", "is_discontinued", "is_new_launch", "is_trending_near_you", "is_in_spotlight"]
    search_fields = ["product_name", "manufacturer_name"]
    list_editable = ["is_new_launch", "is_trending_near_you", "is_in_spotlight"]
    inlines = [ProductImageInline, GenericMedicineInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "alt_text"]
    search_fields = ["product__product_name"]


@admin.register(DealOfTheDay)
class DealOfTheDayAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "discount_percentage", "discounted_price", "offer_ends_at", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["product__product_name"]
    list_editable = ["is_active"]


@admin.register(SuperSavingDeal)
class SuperSavingDealAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "discount_percentage", "discounted_price", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["product__product_name"]
    list_editable = ["is_active"]


@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ["id", "combo_name", "product1", "product2", "combo_price", "tags", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["combo_name", "product1__product_name", "product2__product_name"]
    list_editable = ["is_active"]


@admin.register(GenericMedicine)
class GenericMedicineAdmin(admin.ModelAdmin):
    list_display = ["generic_product_id", "name", "brand", "mrp", "product"]
    search_fields = ["name", "brand", "product__product_name"]
    list_filter = ["brand"]
    autocomplete_fields = ["product"]


@admin.register(ProductFeature)
class ProductFeatureAdmin(admin.ModelAdmin):
    list_display = ["product", "short_description", "short_uses", "short_side_effects"]
    search_fields = ["product__product_name", "description", "uses", "benefits"]
    readonly_fields = ["product"]

    def short_description(self, obj):
        return obj.description[:80] + "..." if len(obj.description) > 80 else obj.description
    short_description.short_description = "Description"

    def short_uses(self, obj):
        return obj.uses[:80] + "..." if len(obj.uses) > 80 else obj.uses
    short_uses.short_description = "Uses"

    def short_side_effects(self, obj):
        return obj.side_effects[:80] + "..." if len(obj.side_effects) > 80 else obj.side_effects
    short_side_effects.short_description = "Side Effects"
