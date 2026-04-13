from django.db import models


class ContactQuery(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("resolved", "Resolved"),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "contact_query"
        ordering = ["-created_at"]
        verbose_name_plural = "Contact Queries"

    def __str__(self):
        return f"{self.name} — {self.mobile}"
