from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CartItemView, CartView,
    ChangePasswordView,
    ForgotPasswordView,
    LoginView, LogoutView,
    OrderDetailView, OrderView,
    PrescriptionUploadView,
    ProfileView,
    ResetPasswordView,
    SignupView,
    WishlistItemView, WishlistView,
)

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────────
    path("signup/",           SignupView.as_view(),         name="signup"),
    path("login/",            LoginView.as_view(),          name="login"),
    path("logout/",           LogoutView.as_view(),         name="logout"),
    path("token/refresh/",    TokenRefreshView.as_view(),   name="token_refresh"),
    path("forgot-password/",  ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/",   ResetPasswordView.as_view(),  name="reset_password"),
    path("prescriptions/upload/", PrescriptionUploadView.as_view(), name="upload_prescription"),

    # ── Profile ────────────────────────────────────────────────────────────────
    path("profile/",                  ProfileView.as_view(),        name="profile"),
    path("profile/change-password/",  ChangePasswordView.as_view(), name="change_password"),

    # ── Cart ───────────────────────────────────────────────────────────────────
    path("cart/",          CartView.as_view(),     name="cart"),
    path("cart/<int:pk>/", CartItemView.as_view(), name="cart_item"),

    # ── Wishlist ───────────────────────────────────────────────────────────────
    path("wishlist/",          WishlistView.as_view(),     name="wishlist"),
    path("wishlist/<int:pk>/", WishlistItemView.as_view(), name="wishlist_item"),

    # ── Orders ─────────────────────────────────────────────────────────────────
    path("orders/",          OrderView.as_view(),       name="orders"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
]
