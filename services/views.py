from rest_framework import viewsets, permissions
from services.models import ServiceCategory
from services.serializers import ServiceCategorySerializer

class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceCategory.objects.filter(is_active=True).order_by('name')
    serializer_class = ServiceCategorySerializer
    permission_classes = [permissions.AllowAny]
