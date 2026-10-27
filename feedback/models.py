# pyrefly: ignore [missing-import]
from django.db import models
from workers.models import Worker
from bookings.models import Booking

# pyrefly: ignore [missing-import]
from django.db.models import Avg
# pyrefly: ignore [missing-import]
from django.db.models.signals import post_save
# pyrefly: ignore [missing-import]
from django.dispatch import receiver

RATING_CHOICES = [
    (5, '⭐ ⭐ ⭐ ⭐ ⭐ (5 - Excellent)'),
    (4, '⭐ ⭐ ⭐ ⭐ (4 - Good)'),
    (3, '⭐ ⭐ ⭐ (3 - Average)'),
    (2, '⭐ ⭐ (2 - Poor)'),
    (1, '⭐ (1 - Very Bad)'),
]

class Feedback(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='feedbacks')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    customer_name = models.CharField(max_length=150, verbose_name="Customer Name")
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, verbose_name="Rating")
    comments = models.TextField(blank=True, null=True, verbose_name="Comments")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Feedback'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['booking'], name='unique_booking_feedback')
        ]

    def __str__(self):
        return f"Feedback for {self.worker.name} by {self.customer_name} ({self.rating}/5)"


@receiver(post_save, sender=Feedback)
def update_worker_rating_signal(sender, instance, created, **kwargs):
    if instance.worker:
        avg = instance.worker.feedbacks.aggregate(Avg('rating'))['rating__avg']
        if avg is not None:
            instance.worker.rating = round(avg, 1)
            instance.worker.save(update_fields=['rating'])

