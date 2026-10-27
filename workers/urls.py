from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'workers'

router = DefaultRouter()
router.register(r'api/list', views.WorkerViewSet, basename='api_workers')
router.register(r'api/availability', views.WorkerAvailabilityViewSet, basename='api_worker_availability')

urlpatterns = [
    # DRF Router endpoints
    path('', include(router.urls)),

    # Legacy HTML Views
    path('directory/', views.worker_list, name='worker_list'),
    path('register/', views.worker_register, name='worker_register'),
    path('<int:pk>/', views.worker_detail, name='worker_detail'),
    path('<int:pk>/toggle-availability/', views.toggle_availability, name='toggle_availability'),
]
