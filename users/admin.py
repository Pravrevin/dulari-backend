from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Cart, Order, OrderItem, Prescription, User, Wishlist


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["id", "name", "email", "mobile", "is_active", "is_staff", "date_joined"]
    list_filter = ["is_active", "is_staff"]
    search_fields = ["email", "mobile", "name"]
    ordering = ["-date_joined"]
    fieldsets = (
        (None, {"fields": ("email", "mobile", "password")}),
        ("Personal Info", {"fields": ("name",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("name", "email", "mobile", "password1", "password2"),
        }),
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "product", "quantity", "added_at"]
    list_filter = ["added_at"]
    search_fields = ["user__email", "user__mobile", "product__product_name"]
    ordering = ["-added_at"]
    raw_id_fields = ["user", "product"]


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "product", "added_at"]
    list_filter = ["added_at"]
    search_fields = ["user__email", "user__mobile", "product__product_name"]
    ordering = ["-added_at"]
    raw_id_fields = ["user", "product"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "quantity", "price"]
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "total_amount", "created_at", "updated_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["user__email", "user__mobile", "user__name"]
    ordering = ["-created_at"]
    readonly_fields = ["total_amount", "created_at", "updated_at"]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "product", "quantity", "price"]
    search_fields = ["order__id", "product__product_name"]
    raw_id_fields = ["order", "product"]


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "prescription_file", "uploaded_at"]
    list_filter = ["uploaded_at"]
    search_fields = ["user__email", "user__mobile", "user__name"]
    ordering = ["-uploaded_at"]
    raw_id_fields = ["user"]
