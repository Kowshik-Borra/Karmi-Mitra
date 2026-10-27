from rest_framework import serializers
from feedback.models import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'worker', 'booking', 'customer_name', 'rating', 'comments', 'created_at']
        read_only_fields = ['created_at']

    def validate_booking(self, value):
        if value and value.status != 'Completed':
            raise serializers.ValidationError("Feedback can only be submitted for completed bookings.")
        if value and Feedback.objects.filter(booking=value).exists():
            raise serializers.ValidationError("Feedback has already been submitted for this booking.")
        return value
