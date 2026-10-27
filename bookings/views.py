from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta

from workers.models import Worker
from .models import Booking
from .forms import BookingForm, OTPVerificationForm
from .services import (
    generate_secure_otp,
    generate_whatsapp_worker_link,
    generate_whatsapp_customer_link,
    send_booking_notification_email
)
from notifications.models import Notification

# DRF Imports
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from bookings.serializers import (
    BookingSerializer,
    BookingCreateSerializer,
    OTPVerifySerializer
)

# -------------------------------------------------------------------
# DRF REST API VIEWS
# -------------------------------------------------------------------

class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Booking.objects.all().order_by('-booking_date')
        if hasattr(user, 'worker_profile') and user.worker_profile:
            return Booking.objects.filter(worker=user.worker_profile).order_by('-booking_date')
        return Booking.objects.filter(customer=user).order_by('-booking_date')

    def perform_create(self, serializer):
        user = self.request.user
        worker = serializer.validated_data['worker']

        # Prevent double booking if worker already has booking at same scheduled time
        scheduled_date = serializer.validated_data.get('scheduled_date')
        scheduled_time = serializer.validated_data.get('scheduled_time')
        if scheduled_date and scheduled_time:
            exists = Booking.objects.filter(
                worker=worker,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                status__in=['Pending', 'Accepted', 'Scheduled', 'In Progress']
            ).exists()
            if exists:
                from rest_framework.exceptions import ValidationError
                raise ValidationError("Worker is already booked for this requested date and time slot.")

        booking = serializer.save(
            customer=user if user.is_authenticated else None,
            status='Pending'
        )

        # Create notification for worker if user linked
        if worker.user:
            Notification.objects.create(
                user=worker.user,
                title="New Booking Request Received",
                message=f"New request from {booking.customer_name} for {booking.work_details[:50]}...",
                notification_type='BOOKING'
            )

        send_booking_notification_email(booking, event_type='created')

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        booking = self.get_object()
        if hasattr(request.user, 'worker_profile') and request.user.worker_profile == booking.worker or request.user.is_staff:
            booking.status = 'Accepted'
            # Generate 6-digit OTP
            booking.otp = generate_secure_otp(6)
            booking.otp_created_at = timezone.now()
            booking.save()

            if booking.customer:
                Notification.objects.create(
                    user=booking.customer,
                    title="Booking Accepted!",
                    message=f"Worker {booking.worker.name} accepted your booking request.",
                    notification_type='BOOKING'
                )

            return Response({
                'status': 'Accepted',
                'otp': booking.otp,
                'message': 'Booking accepted. OTP generated.'
            })
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        booking = self.get_object()
        if hasattr(request.user, 'worker_profile') and request.user.worker_profile == booking.worker or request.user.is_staff:
            reason = request.data.get('reason', 'Worker declined request')
            booking.status = 'Rejected'
            booking.cancellation_reason = reason
            booking.save()

            if booking.customer:
                Notification.objects.create(
                    user=booking.customer,
                    title="Booking Declined",
                    message=f"Worker {booking.worker.name} declined booking: {reason}",
                    notification_type='BOOKING'
                )

            return Response({'status': 'Rejected'})
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        booking = self.get_object()
        if hasattr(request.user, 'worker_profile') and request.user.worker_profile == booking.worker or request.user.is_staff:
            booking.status = 'In Progress'
            booking.save()
            return Response({'status': 'In Progress'})
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        reason = request.data.get('reason', 'User cancelled booking')
        booking.status = 'Cancelled'
        booking.cancellation_reason = reason
        booking.save()
        return Response({'status': 'Cancelled'})

    @action(detail=True, methods=['post'])
    def verify_otp(self, request, pk=None):
        booking = self.get_object()
        entered_otp = request.data.get('otp', '').strip()

        if booking.otp_attempts >= 3:
            return Response({
                'error': 'Maximum OTP attempts exceeded (3/3). Please generate a new OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if booking.otp_created_at and timezone.now() > booking.otp_created_at + timedelta(minutes=10):
            return Response({
                'error': 'OTP has expired (10 minute limit). Please request a new OTP.'
            }, status=status.HTTP_400_BAD_REQUEST)

        booking.otp_attempts += 1

        if booking.otp and booking.otp == entered_otp:
            booking.status = 'Completed'
            booking.otp_verified = True
            booking.save()

            booking.worker.update_availability_status()
            send_booking_notification_email(booking, event_type='completed')

            if booking.customer:
                Notification.objects.create(
                    user=booking.customer,
                    title="Work Completed Successfully!",
                    message=f"Work for booking #{booking.id} completed. Please leave your review!",
                    notification_type='BOOKING'
                )

            return Response({'status': 'Completed', 'otp_verified': True})

        booking.save(update_fields=['otp_attempts'])
        return Response({
            'error': f'Invalid OTP. Attempt {booking.otp_attempts}/3.'
        }, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------------------------------
# LEGACY TEMPLATE VIEWS
# -------------------------------------------------------------------

def book_worker(request, worker_id):
    """
    Booking worker page with HTML5 Geolocation & details submission
    """
    worker = get_object_or_404(Worker, pk=worker_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.worker = worker
            if request.user.is_authenticated:
                booking.customer = request.user
            booking.save()

            # Check and update worker availability if >= 3 completed bookings
            worker.update_availability_status()

            # Send email notification
            send_booking_notification_email(booking, event_type='created')

            messages.success(request, f"You have successfully booked {worker.name}!")
            return redirect('bookings:booking_detail', booking_id=booking.id)
        else:
            messages.error(request, "Error processing booking. Please verify the form.")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['customer_name'] = request.user.get_full_name() or request.user.username
            initial_data['customer_email'] = request.user.email
            if hasattr(request.user, 'customer_profile'):
                initial_data['customer_contact'] = request.user.customer_profile.phone_no
                initial_data['customer_address'] = request.user.customer_profile.address
        form = BookingForm(initial=initial_data)

    return render(request, 'bookings/book_worker.html', {
        'worker': worker,
        'form': form
    })

def booking_detail(request, booking_id):
    """
    View individual booking status and details
    """
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})

def send_to_worker(request, booking_id):
    """
    Preview and send customer details & OTP verification link to Worker via WhatsApp
    """
    booking = get_object_or_404(Booking, pk=booking_id)
    whatsapp_url, message_preview = generate_whatsapp_worker_link(request, booking)

    return render(request, 'bookings/send_to_worker.html', {
        'booking': booking,
        'message_preview': message_preview,
        'whatsapp_url': whatsapp_url
    })

def send_to_customer(request, booking_id):
    """
    Generate secure 6-digit OTP, store in booking, and generate WhatsApp link for customer
    """
    booking = get_object_or_404(Booking, pk=booking_id)

    # Generate 6-digit OTP if not existing
    if not booking.otp:
        booking.otp = generate_secure_otp(6)
        booking.otp_created_at = timezone.now()
        booking.save(update_fields=['otp', 'otp_created_at'])

    whatsapp_url, message_preview = generate_whatsapp_customer_link(request, booking, booking.otp)

    return render(request, 'bookings/send_to_customer.html', {
        'booking': booking,
        'message_preview': message_preview,
        'whatsapp_url': whatsapp_url
    })

def verify_otp(request):
    """
    Verify OTP for work completion
    """
    booking_id = request.GET.get('booking_id') or request.POST.get('booking_id')
    worker_id = request.GET.get('worker_id') or request.POST.get('worker_id')

    booking = None
    if booking_id and worker_id:
        booking = get_object_or_404(Booking, pk=booking_id, worker_id=worker_id)

    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            b_id = form.cleaned_data['booking_id']
            w_id = form.cleaned_data['worker_id']
            entered_otp = form.cleaned_data['otp'].strip()

            target_booking = get_object_or_404(Booking, pk=b_id, worker_id=w_id)

            if target_booking.otp and target_booking.otp == entered_otp:
                target_booking.status = 'Completed'
                target_booking.otp_verified = True
                target_booking.save(update_fields=['status', 'otp_verified'])

                # Update worker availability if threshold reached
                target_booking.worker.update_availability_status()

                # Send email notification for completion
                send_booking_notification_email(target_booking, event_type='completed')

                messages.success(request, "✅ OTP Verified Successfully! Work marked as Completed.")
                return redirect('bookings:booking_success', booking_id=target_booking.id)
            else:
                messages.error(request, "❌ Invalid OTP! Please double check and try again.")
    else:
        initial_data = {}
        if booking:
            initial_data['booking_id'] = booking.id
            initial_data['worker_id'] = booking.worker.id
        form = OTPVerificationForm(initial=initial_data)

    return render(request, 'bookings/verify_otp.html', {
        'form': form,
        'booking': booking
    })

def booking_success(request, booking_id):
    """
    Success page after OTP completion
    """
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, 'bookings/booking_success.html', {'booking': booking})

@staff_member_required
def admin_dashboard(request):
    """
    Custom Admin Dashboard for managing bookings
    """
    bookings = Booking.objects.all().select_related('worker')
    return render(request, 'dashboard/admin_dashboard.html', {
        'bookings': bookings
    })
