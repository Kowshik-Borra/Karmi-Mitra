from django.db import models
from django.contrib.auth.models import User
from workers.models import Worker

from django.utils import timezone

STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Rejected', 'Rejected'),
    ('Scheduled', 'Scheduled'),
    ('In Progress', 'In Progress'),
    ('Completed', 'Completed'),
    ('Cancelled', 'Cancelled'),
]

class Booking(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='bookings')
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_bookings')
    customer_name = models.CharField(max_length=150, verbose_name="Customer Full Name")
    customer_age = models.PositiveIntegerField(verbose_name="Customer Age", default=25)
    customer_address = models.TextField(verbose_name="Customer Address")
    customer_contact = models.CharField(max_length=15, verbose_name="Customer Contact")
    customer_email = models.EmailField(verbose_name="Customer Email")
    work_details = models.TextField(verbose_name="Work Details")
    location_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Location URL")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=20.2961, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=85.8245, verbose_name="Longitude")
    scheduled_date = models.DateField(default=timezone.now, verbose_name="Scheduled Work Date")
    scheduled_time = models.TimeField(default="10:00:00", verbose_name="Scheduled Work Time")
    estimated_amount = models.DecimalField(max_digits=8, decimal_places=2, default=500.00, verbose_name="Estimated Amount (INR)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    otp = models.CharField(max_length=6, blank=True, null=True, verbose_name="OTP Code")
    otp_verified = models.BooleanField(default=False)
    otp_created_at = models.DateTimeField(blank=True, null=True, verbose_name="OTP Created At")
    otp_attempts = models.PositiveSmallIntegerField(default=0, verbose_name="OTP Attempts")
    cancellation_reason = models.TextField(blank=True, null=True)
    booking_date = models.DateTimeField(auto_now_add=True, verbose_name="Booking Date")

    class Meta:
        db_table = 'Booking_info'
        ordering = ['-booking_date']

    def __str__(self):
        return f"Booking #{self.id} - {self.customer_name} -> {self.worker.name} ({self.status})"

