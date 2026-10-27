from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from recommendations.engine import rank_workers_for_request, classify_problem_description
from workers.serializers import WorkerListSerializer

class RecommendWorkersAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        category = request.data.get('category')
        skill_keyword = request.data.get('skill_keyword')
        cust_lat = request.data.get('latitude', 20.2961)
        cust_lon = request.data.get('longitude', 85.8245)
        max_dist = float(request.data.get('max_distance_km', 25.0))
        target_budget = request.data.get('budget')
        min_rating = float(request.data.get('min_rating', 0.0))
        min_experience = int(request.data.get('min_experience', 0))

        results = rank_workers_for_request(
            category=category,
            skill_keyword=skill_keyword,
            cust_lat=cust_lat,
            cust_lon=cust_lon,
            max_distance_km=max_dist,
            target_budget=target_budget,
            min_rating=min_rating,
            min_experience=min_experience
        )

        response_data = []
        for item in results:
            w_data = WorkerListSerializer(item['worker']).data
            w_data['distance_km'] = item['distance_km']
            w_data['match_score'] = item['match_score']
            w_data['recommendation_reasons'] = item['reasons']
            response_data.append(w_data)

        return Response({
            'total_matches': len(response_data),
            'top_recommendation': response_data[0] if response_data else None,
            'workers': response_data
        })


class ClassifyProblemAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        description = request.data.get('description', '')
        cust_lat = request.data.get('latitude', 20.2961)
        cust_lon = request.data.get('longitude', 85.8245)

        if not description:
            return Response({'error': 'Problem description text is required.'}, status=status.HTTP_400_BAD_REQUEST)

        classification = classify_problem_description(description)

        # Get recommended workers for classified category
        recommended = rank_workers_for_request(
            category=classification['category'],
            cust_lat=cust_lat,
            cust_lon=cust_lon
        )

        workers_data = []
        for item in recommended[:5]:  # Top 5
            w_data = WorkerListSerializer(item['worker']).data
            w_data['distance_km'] = item['distance_km']
            w_data['match_score'] = item['match_score']
            w_data['recommendation_reasons'] = item['reasons']
            workers_data.append(w_data)

        classification['recommended_workers'] = workers_data
        return Response(classification)
