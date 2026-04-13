from django.urls import path
from . import views

urlpatterns = [
    path("search/", views.ProductSearchView.as_view(), name="product-search"),
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("combos/", views.ComboListView.as_view(), name="combo-list"),
    path("combos/<int:pk>/", views.ComboDetailView.as_view(), name="combo-detail"),
    path("categories/<int:category_id>/products/", views.CategoryProductListView.as_view(), name="category-products"),
    path("deals-of-the-day/", views.DealsOfTheDayListView.as_view(), name="deals-of-the-day"),
    path("super-saving-deals/", views.SuperSavingDealsListView.as_view(), name="super-saving-deals"),
    path("products/", views.ProductListView.as_view(), name="product-list"),
    path("products/new-launches/", views.new_launches, name="new-launches"),
    path("products/trending-near-you/", views.trending_near_you, name="trending-near-you"),
    path("products/in-the-spotlight/", views.in_the_spotlight, name="in-the-spotlight"),
    path("products/<int:product_id>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("products/<int:product_id>/features/", views.ProductFeatureView.as_view(), name="product-features"),
    path("products/<int:product_id>/generic-medicines/", views.GenericMedicineListView.as_view(), name="product-generic-medicines"),
    path("brands/", views.BrandListView.as_view(), name="brand-list"),
    path("brands/<str:manufacturer_name>/products/", views.BrandProductListView.as_view(), name="brand-products"),
]
