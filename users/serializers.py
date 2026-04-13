import re
import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from products.models import Product
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Cart, Order, OrderItem, Wishlist

User = get_user_model()


# ── Auth ──────────────────────────────────────────────────────────────────────

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "name", "email", "mobile", "password"]

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("mobile"):
            raise serializers.ValidationError("Either email or mobile is required.")
        return attrs

    def validate_mobile(self, value):
        if value and not re.fullmatch(r"[6-9]\d{9}", value):
            raise serializers.ValidationError("Enter a valid 10-digit Indian mobile number.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    mobile = serializers.CharField(required=False, max_length=15)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        mobile = attrs.get("mobile")
        password = attrs.get("password")

        if not email and not mobile:
            raise serializers.ValidationError("Provide either email or mobile to login.")

        try:
            user = User.objects.get(email=email) if email else User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No account found with this email." if email else "No account found with this mobile number."
            )

        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")

        refresh = RefreshToken.for_user(user)
        attrs["tokens"] = {"refresh": str(refresh), "access": str(refresh.access_token)}
        attrs["user"] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    mobile = serializers.CharField(required=False, max_length=15)

    def validate(self, attrs):
        email = attrs.get("email")
        mobile = attrs.get("mobile")

        if not email and not mobile:
            raise serializers.ValidationError("Provide email or mobile.")

        try:
            user = User.objects.get(email=email) if email else User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found.")

        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = timezone.now() + timedelta(minutes=15)
        user.save(update_fields=["reset_token", "reset_token_expires"])
        attrs["token"] = token
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=6)

    def validate_token(self, value):
        try:
            user = User.objects.get(reset_token=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid reset token.")
        if user.reset_token_expires < timezone.now():
            raise serializers.ValidationError("Reset token has expired.")
        self._user = user
        return value

    def save(self):
        self._user.set_password(self.validated_data["new_password"])
        self._user.reset_token = None
        self._user.reset_token_expires = None
        self._user.save(update_fields=["password", "reset_token", "reset_token_expires"])


# ── Profile ───────────────────────────────────────────────────────────────────

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email", "mobile", "date_joined"]
        read_only_fields = ["id", "date_joined"]

    def validate_email(self, value):
        if User.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_mobile(self, value):
        if value and not re.fullmatch(r"[6-9]\d{9}", value):
            raise serializers.ValidationError("Enter a valid 10-digit Indian mobile number.")
        if User.objects.exclude(pk=self.instance.pk).filter(mobile=value).exists():
            raise serializers.ValidationError("This mobile number is already in use.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)

    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


# ── Product (nested) ──────────────────────────────────────────────────────────

class ProductBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["product_id", "product_name", "mrp", "manufacturer_name", "pack_size_label"]


# ── Cart ──────────────────────────────────────────────────────────────────────

class CartSerializer(serializers.ModelSerializer):
    product = ProductBriefSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "product", "quantity", "added_at"]


class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Product not found.")
        return value


class CartUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)


# ── Wishlist ──────────────────────────────────────────────────────────────────

class WishlistSerializer(serializers.ModelSerializer):
    product = ProductBriefSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "product", "added_at"]


class WishlistAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Product not found.")
        return value


# ── Order ─────────────────────────────────────────────────────────────────────

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductBriefSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "total_amount", "delivery_address", "items", "created_at", "updated_at"]


class OrderCreateSerializer(serializers.Serializer):
    delivery_address = serializers.CharField()
    # Optional: provide products directly; omit to create order from cart
    products = serializers.ListField(child=serializers.DictField(), required=False)

    def validate(self, attrs):
        user = self.context["request"].user
        products_data = attrs.get("products")

        if products_data:
            items = []
            for entry in products_data:
                pid = entry.get("product_id")
                qty = int(entry.get("quantity", 1))
                try:
                    product = Product.objects.get(pk=pid)
                except Product.DoesNotExist:
                    raise serializers.ValidationError(f"Product {pid} not found.")
                items.append({"product": product, "quantity": qty, "price": product.mrp})
        else:
            cart_items = Cart.objects.filter(user=user).select_related("product")
            if not cart_items.exists():
                raise serializers.ValidationError("Cart is empty. Add products to cart first.")
            items = [
                {"product": ci.product, "quantity": ci.quantity, "price": ci.product.mrp}
                for ci in cart_items
            ]

        attrs["items"] = items
        attrs["total_amount"] = sum(i["price"] * i["quantity"] for i in items)
        return attrs
