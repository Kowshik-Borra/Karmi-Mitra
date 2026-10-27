from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'bookings'

router = DefaultRouter()
router.register(r'api', views.BookingViewSet, basename='api_bookings')

urlpatterns = [
    # DRF Router
    path('', include(router.urls)),

    # Legacy HTML Views
    path('create/<int:worker_id>/', views.book_worker, name='book_worker'),
    path('<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('<int:booking_id>/send-worker/', views.send_to_worker, name='send_to_worker'),
    path('<int:booking_id>/send-customer/', views.send_to_customer, name='send_to_customer'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
