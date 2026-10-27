from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from workers import views as worker_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', worker_views.index, name='index'),

    # OpenAPI 3 Schema & Swagger UI Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # Application Endpoint Routes
    path('accounts/', include('accounts.urls')),
    path('workers/', include('workers.urls')),
    path('bookings/', include('bookings.urls')),
    path('feedback/', include('feedback.urls')),
    path('services/', include('services.urls')),
    path('recommendations/', include('recommendations.urls')),
    path('payments/', include('payments.urls')),
    path('notifications/', include('notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
