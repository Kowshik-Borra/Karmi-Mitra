from django.urls import path, include
from rest_framework.routers import DefaultRouter
from services.views import ServiceCategoryViewSet

app_name = 'services'

router = DefaultRouter()
router.register(r'categories', ServiceCategoryViewSet, basename='service_categories')

urlpatterns = [
    path('api/', include(router.urls)),
]
