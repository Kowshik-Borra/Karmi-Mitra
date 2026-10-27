from django.urls import path
from recommendations.views import RecommendWorkersAPIView, ClassifyProblemAPIView

app_name = 'recommendations'

urlpatterns = [
    path('api/rank/', RecommendWorkersAPIView.as_view(), name='api_rank_workers'),
    path('api/classify/', ClassifyProblemAPIView.as_view(), name='api_classify_problem'),
]
