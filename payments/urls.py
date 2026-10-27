from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payments.views import PaymentViewSet

app_name = 'payments'

router = DefaultRouter()
router.register(r'api', PaymentViewSet, basename='api_payments')

urlpatterns = [
    path('', include(router.urls)),
]
