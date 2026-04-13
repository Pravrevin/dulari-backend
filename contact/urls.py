from django.urls import path
from .views import ContactQueryCreateView, ContactQueryListView

urlpatterns = [
    path("", ContactQueryCreateView.as_view(), name="contact-create"),
    path("list/", ContactQueryListView.as_view(), name="contact-list"),
]
