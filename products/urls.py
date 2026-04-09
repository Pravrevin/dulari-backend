from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.ProductListView.as_view(), name="product-list"),
    path("products/new-launches/", views.new_launches, name="new-launches"),
    path("products/trending-near-you/", views.trending_near_you, name="trending-near-you"),
    path("products/in-the-spotlight/", views.in_the_spotlight, name="in-the-spotlight"),
    path("products/<int:product_id>/", views.ProductDetailView.as_view(), name="product-detail"),
]
