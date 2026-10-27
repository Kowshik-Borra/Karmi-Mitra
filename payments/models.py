from django.db import models
from bookings.models import Booking

PAYMENT_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('SUCCESS', 'Success'),
    ('FAILED', 'Failed'),
    ('REFUNDED', 'Refunded'),
]

PAYMENT_METHOD_CHOICES = [
    ('UPI', 'UPI / QR Code'),
    ('CARD', 'Credit / Debit Card'),
    ('NETBANKING', 'Net Banking'),
    ('CASH', 'Cash on Service Completion'),
]

class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Payment Amount (INR)")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='UPI')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Payment_info'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment #{self.id} for Booking #{self.booking.id} - {self.status} (₹{self.amount})"

