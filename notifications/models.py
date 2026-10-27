from django.db import models
from django.contrib.auth.models import User

NOTIFICATION_TYPE_CHOICES = [
    ('BOOKING', 'Booking Update'),
    ('PAYMENT', 'Payment Status'),
    ('SYSTEM', 'System Alert'),
    ('REVIEW', 'Review Received'),
]

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default='BOOKING')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'User_notification'
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

