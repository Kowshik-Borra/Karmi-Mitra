import uuid
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from payments.models import Payment
from payments.serializers import PaymentSerializer
from bookings.models import Booking
from notifications.models import Notification

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(booking__customer=user)

    def create(self, request, *args, **kwargs):
        booking_id = request.data.get('booking')
        amount = request.data.get('amount')
        method = request.data.get('payment_method', 'UPI')

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                'amount': amount or booking.estimated_amount,
                'payment_method': method,
                'status': 'SUCCESS',
                'transaction_id': f"TXN-{uuid.uuid4().hex[:10].upper()}"
            }
        )

        if not created and payment.status != 'SUCCESS':
            payment.status = 'SUCCESS'
            payment.save()

        if booking.customer:
            Notification.objects.create(
                user=booking.customer,
                title="Payment Successful",
                message=f"Payment of ₹{payment.amount} for booking #{booking.id} was processed successfully.",
                notification_type='PAYMENT'
            )

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
