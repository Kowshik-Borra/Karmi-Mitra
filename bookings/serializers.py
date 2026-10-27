from rest_framework import serializers
from bookings.models import Booking
from workers.serializers import WorkerListSerializer
from accounts.serializers import UserSerializer

class BookingSerializer(serializers.ModelSerializer):
    worker_detail = WorkerListSerializer(source='worker', read_only=True)
    has_feedback = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'worker', 'worker_detail', 'customer', 'customer_name',
            'customer_age', 'customer_address', 'customer_contact',
            'customer_email', 'work_details', 'location_url', 'latitude',
            'longitude', 'scheduled_date', 'scheduled_time', 'estimated_amount',
            'status', 'otp', 'otp_verified', 'otp_created_at', 'otp_attempts',
            'cancellation_reason', 'has_feedback', 'booking_date'
        ]
        read_only_fields = ['otp', 'otp_verified', 'otp_created_at', 'otp_attempts', 'booking_date']

    def get_has_feedback(self, obj):
        return hasattr(obj, 'feedbacks') and obj.feedbacks.exists()


class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'worker', 'customer_name', 'customer_age', 'customer_address',
            'customer_contact', 'customer_email', 'work_details',
            'location_url', 'latitude', 'longitude', 'scheduled_date',
            'scheduled_time', 'estimated_amount'
        ]


class OTPVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6, min_length=6)
