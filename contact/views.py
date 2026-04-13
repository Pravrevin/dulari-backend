from rest_framework import generics, permissions
from .models import ContactQuery
from .serializers import ContactQuerySerializer


class ContactQueryCreateView(generics.CreateAPIView):
    """
    POST /api/contact/
    Public endpoint — any customer can submit a query.
    """
    queryset = ContactQuery.objects.all()
    serializer_class = ContactQuerySerializer
    permission_classes = [permissions.AllowAny]


class ContactQueryListView(generics.ListAPIView):
    """
    GET /api/contact/list/
    Admin-only endpoint to view all submitted queries.
    """
    queryset = ContactQuery.objects.all()
    serializer_class = ContactQuerySerializer
    permission_classes = [permissions.IsAdminUser]
