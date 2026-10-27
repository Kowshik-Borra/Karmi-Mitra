from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Legacy HTML Views
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile_dashboard, name='profile'),

    # DRF REST API Endpoints
    path('api/register/customer/', views.RegisterCustomerAPIView.as_view(), name='api_register_customer'),
    path('api/register/worker/', views.RegisterWorkerAPIView.as_view(), name='api_register_worker'),
    path('api/login/', TokenObtainPairView.as_view(), name='api_login'),
    path('api/refresh/', TokenRefreshView.as_view(), name='api_refresh'),
    path('api/me/', views.UserProfileAPIView.as_view(), name='api_me'),
    path('api/admin/analytics/', views.AdminAnalyticsAPIView.as_view(), name='api_admin_analytics'),
]

