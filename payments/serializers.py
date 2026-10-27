from rest_framework import serializers
from payments.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_method', 'status', 'transaction_id', 'created_at', 'updated_at']
        read_only_fields = ['transaction_id', 'created_at', 'updated_at']
