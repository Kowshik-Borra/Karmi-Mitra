from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'feedback'

router = DefaultRouter()
router.register(r'api', views.FeedbackViewSet, basename='api_feedback')

urlpatterns = [
    # DRF Router
    path('', include(router.urls)),

    # Legacy HTML View
    path('submit/', views.submit_feedback, name='submit'),
]
