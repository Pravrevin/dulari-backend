from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Cart, Order, OrderItem, Prescription, Wishlist
from .serializers import (
    CartAddSerializer, CartSerializer, CartUpdateSerializer,
    ChangePasswordSerializer, ForgotPasswordSerializer,
    LoginSerializer, LogoutSerializer,
    OrderCreateSerializer, OrderSerializer,
    PrescriptionSerializer, PrescriptionUploadSerializer,
    ProfileSerializer, ResetPasswordSerializer,
    SignupSerializer, WishlistAddSerializer, WishlistSerializer,
)

User = get_user_model()


# ── Auth ──────────────────────────────────────────────────────────────────────

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "Account created successfully.",
                 "user": {"id": user.id, "name": user.name, "email": user.email, "mobile": user.mobile}},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            tokens = serializer.validated_data["tokens"]
            return Response(
                {"message": "Login successful.",
                 "user": {
                     "id": user.id,
                     "name": user.name,
                     "email": user.email,
                     "mobile": user.mobile,
                     "is_staff": user.is_staff,
                     "is_superuser": user.is_superuser,
                 },
                 "tokens": tokens},
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            try:
                RefreshToken(serializer.validated_data["refresh"]).blacklist()
                return Response({"message": "Logged out successfully."})
            except TokenError:
                return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                "message": "Password reset token generated.",
                "reset_token": serializer.validated_data["token"],
                "note": "In production this token is sent via email/SMS. Use it in /reset-password/.",
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset successfully. Please login again."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ── Profile ───────────────────────────────────────────────────────────────────

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user).data)

    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated.", "user": serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data["new_password"])
            request.user.save(update_fields=["password"])
            return Response({"message": "Password changed successfully. Please login again."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrescriptionUploadView(APIView):
    def post(self, request):
        upload_serializer = PrescriptionUploadSerializer(data=request.data)
        if not upload_serializer.is_valid():
            return Response(upload_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None
        tokens = None

        if user is None:
            signup_serializer = SignupSerializer(data=request.data)
            if not signup_serializer.is_valid():
                return Response(
                    {
                        "error": "Authentication required. Provide valid signup details to continue.",
                        "signup_errors": signup_serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = signup_serializer.save()
            refresh = RefreshToken.for_user(user)
            tokens = {"refresh": str(refresh), "access": str(refresh.access_token)}

        prescription = Prescription.objects.create(
            user=user,
            prescription_file=upload_serializer.validated_data["prescription_file"],
        )

        response_data = {
            "message": "Prescription uploaded successfully.",
            "prescription": PrescriptionSerializer(prescription).data,
        }

        if tokens:
            response_data.update(
                {
                    "auth_message": "Account created and authenticated successfully.",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "mobile": user.mobile,
                    },
                    "tokens": tokens,
                }
            )

        return Response(response_data, status=status.HTTP_201_CREATED)


# ── Cart ──────────────────────────────────────────────────────────────────────

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Cart.objects.filter(user=request.user).select_related("product")
        return Response({"cart": CartSerializer(items, many=True).data, "count": items.count()})

    def post(self, request):
        serializer = CartAddSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data["product_id"]
            quantity = serializer.validated_data["quantity"]
            item, created = Cart.objects.get_or_create(
                user=request.user, product_id=product_id,
                defaults={"quantity": quantity},
            )
            if not created:
                item.quantity += quantity
                item.save(update_fields=["quantity"])
            return Response(
                {"message": "Added to cart." if created else "Quantity updated.",
                 "item": CartSerializer(item).data},
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_item(self, pk):
        try:
            return Cart.objects.get(pk=pk, user=self.request.user)
        except Cart.DoesNotExist:
            return None

    def patch(self, request, pk):
        item = self._get_item(pk)
        if not item:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CartUpdateSerializer(data=request.data)
        if serializer.is_valid():
            item.quantity = serializer.validated_data["quantity"]
            item.save(update_fields=["quantity"])
            return Response({"message": "Quantity updated.", "item": CartSerializer(item).data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = self._get_item(pk)
        if not item:
            return Response({"error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({"message": "Item removed from cart."})


# ── Wishlist ──────────────────────────────────────────────────────────────────

class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Wishlist.objects.filter(user=request.user).select_related("product")
        return Response({"wishlist": WishlistSerializer(items, many=True).data, "count": items.count()})

    def post(self, request):
        serializer = WishlistAddSerializer(data=request.data)
        if serializer.is_valid():
            item, created = Wishlist.objects.get_or_create(
                user=request.user, product_id=serializer.validated_data["product_id"]
            )
            if not created:
                return Response({"message": "Already in wishlist."})
            return Response(
                {"message": "Added to wishlist.", "item": WishlistSerializer(item).data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WishlistItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            Wishlist.objects.get(pk=pk, user=request.user).delete()
            return Response({"message": "Removed from wishlist."})
        except Wishlist.DoesNotExist:
            return Response({"error": "Wishlist item not found."}, status=status.HTTP_404_NOT_FOUND)


# ── Orders ────────────────────────────────────────────────────────────────────

class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related("items__product")
        return Response({"orders": OrderSerializer(orders, many=True).data, "count": orders.count()})

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            items = serializer.validated_data["items"]
            order = Order.objects.create(
                user=request.user,
                total_amount=serializer.validated_data["total_amount"],
                delivery_address=serializer.validated_data["delivery_address"],
            )
            OrderItem.objects.bulk_create([
                OrderItem(order=order, product=i["product"], quantity=i["quantity"], price=i["price"])
                for i in items
            ])
            # Clear cart if order was placed from it (no explicit products list)
            if not request.data.get("products"):
                Cart.objects.filter(user=request.user).delete()

            order.refresh_from_db()
            return Response(
                {"message": "Order placed successfully.", "order": OrderSerializer(order).data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_order(self, pk):
        try:
            return Order.objects.prefetch_related("items__product").get(pk=pk, user=self.request.user)
        except Order.DoesNotExist:
            return None

    def get(self, request, pk):
        order = self._get_order(pk)
        if not order:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order).data)

    def patch(self, request, pk):
        order = self._get_order(pk)
        if not order:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        if order.status != Order.Status.PENDING:
            return Response(
                {"error": f"Cannot cancel an order with status '{order.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])
        return Response({"message": "Order cancelled.", "order": OrderSerializer(order).data})
