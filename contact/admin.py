from django.contrib import admin
from .models import ContactQuery


@admin.register(ContactQuery)
class ContactQueryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "email", "mobile", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["name", "email", "mobile"]
    ordering = ["-created_at"]
