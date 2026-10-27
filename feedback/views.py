from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg
from workers.models import Worker
from bookings.models import Booking
from .forms import FeedbackForm

# DRF Imports
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from feedback.models import Feedback
from feedback.serializers import FeedbackSerializer
from notifications.models import Notification

# -------------------------------------------------------------------
# DRF REST API VIEWS
# -------------------------------------------------------------------

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().order_by('-created_at')
    serializer_class = FeedbackSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        feedback = serializer.save()
        if feedback.worker and feedback.worker.user:
            Notification.objects.create(
                user=feedback.worker.user,
                title="New Rating & Feedback Received",
                message=f"Received {feedback.rating}⭐ rating from {feedback.customer_name}.",
                notification_type='REVIEW'
            )


# -------------------------------------------------------------------
# LEGACY TEMPLATE VIEWS
# -------------------------------------------------------------------

def submit_feedback(request):
    """
    Handle Customer Feedback & Rating Submission and update Worker Average Rating
    """
    worker_id = request.GET.get('worker_id') or request.POST.get('worker_id')
    booking_id = request.GET.get('booking_id') or request.POST.get('booking_id')

    if not worker_id:
        messages.error(request, "Worker ID is missing.")
        return redirect('index')

    worker = get_object_or_404(Worker, pk=worker_id)
    booking = get_object_or_404(Booking, pk=booking_id) if booking_id else None

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.worker = worker
            feedback.booking = booking
            feedback.save()

            # Calculate new average rating for the worker
            avg_rating = worker.feedbacks.aggregate(Avg('rating'))['rating__avg']
            if avg_rating is not None:
                worker.rating = round(avg_rating, 1)
                worker.save(update_fields=['rating'])

            messages.success(request, f"✅ Thank you! Your feedback for {worker.name} has been submitted successfully.")
            return redirect('workers:worker_detail', pk=worker.pk)
        else:
            messages.error(request, "Please check your feedback input.")
    else:
        initial_data = {}
        if booking:
            initial_data['customer_name'] = booking.customer_name
        form = FeedbackForm(initial=initial_data)

    return render(request, 'feedback/feedback_form.html', {
        'form': form,
        'worker': worker,
        'booking': booking
    })
