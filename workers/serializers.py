from rest_framework import serializers
from workers.models import Worker, WorkerAvailability
from feedback.models import Feedback

class WorkerAvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = WorkerAvailability
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_available']


class WorkerFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'customer_name', 'rating', 'comments', 'created_at']


class WorkerListSerializer(serializers.ModelSerializer):
    distance_km = serializers.FloatField(read_only=True, required=False)
    match_score = serializers.FloatField(read_only=True, required=False)
    profile_completion = serializers.SerializerMethodField()

    class Meta:
        model = Worker
        fields = [
            'id', 'name', 'category', 'city_name', 'skill_type',
            'experience_level', 'years_of_experience', 'hourly_rate',
            'price_min', 'price_max', 'latitude', 'longitude',
            'profile_image', 'availability', 'rating', 'is_verified',
            'distance_km', 'match_score', 'profile_completion'
        ]

    def get_profile_completion(self, obj):
        percentage = 40
        if obj.name and obj.contact_number and obj.email and obj.category and obj.city_name:
            percentage += 30
        if obj.bio and len(obj.bio.strip()) >= 10:
            percentage += 15
        if obj.profile_image and 'default' not in str(obj.profile_image).lower():
            percentage += 15
        return min(100, percentage)


class WorkerDetailSerializer(serializers.ModelSerializer):
    availabilities = WorkerAvailabilitySerializer(many=True, read_only=True)
    feedbacks = WorkerFeedbackSerializer(many=True, read_only=True)
    completed_jobs = serializers.SerializerMethodField()
    profile_completion = serializers.SerializerMethodField()

    class Meta:
        model = Worker
        fields = [
            'id', 'user', 'name', 'age', 'gender', 'category', 'contact_number',
            'email', 'city_name', 'skill_type', 'experience_level',
            'years_of_experience', 'hourly_rate', 'price_min', 'price_max',
            'latitude', 'longitude', 'bio', 'profile_image', 'availability',
            'rating', 'is_verified', 'availabilities', 'feedbacks', 'completed_jobs',
            'profile_completion', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'rating', 'is_verified', 'created_at']

    def get_completed_jobs(self, obj):
        return obj.bookings.filter(status='Completed').count()

    def get_profile_completion(self, obj):
        percentage = 40
        if obj.name and obj.contact_number and obj.email and obj.category and obj.city_name:
            percentage += 30
        if obj.bio and len(obj.bio.strip()) >= 10:
            percentage += 15
        if obj.profile_image and 'default' not in str(obj.profile_image).lower():
            percentage += 15
        return min(100, percentage)

