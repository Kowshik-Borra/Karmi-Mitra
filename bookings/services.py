import secrets
import string
from urllib.parse import quote
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def generate_secure_otp(length=6):
    """
    Generate a secure 6-digit numeric OTP.
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def generate_whatsapp_worker_link(request, booking):
    """
    Generate a WhatsApp URL with customer booking details for the worker.
    """
    verify_url = request.build_absolute_uri(
        reverse('bookings:verify_otp') + f"?booking_id={booking.id}&worker_id={booking.worker.id}"
    )

    message = (
        f"Hello {booking.worker.name}!\n\n"
        f"Here are the customer details for your assigned work:\n"
        f"👤 Customer Name: {booking.customer_name}\n"
        f"🎂 Age: {booking.customer_age}\n"
        f"📍 Address: {booking.customer_address}\n"
        f"📞 Contact: {booking.customer_contact}\n"
        f"📅 Booking Date: {booking.booking_date.strftime('%Y-%m-%d %H:%M')}\n"
        f"📧 Email: {booking.customer_email}\n"
        f"📌 Location: {booking.location_url or 'N/A'}\n"
        f"🔹 Work Details: {booking.work_details}\n\n"
        f"✅ After completing the work, verify OTP here:\n"
        f"{verify_url}"
    )

    phone = booking.worker.contact_number.strip()
    if not phone.startswith("+"):
        phone = "+91" + phone.lstrip("0")

    encoded_msg = quote(message)
    return f"https://wa.me/{phone}?text={encoded_msg}", message

def generate_whatsapp_customer_link(request, booking, otp_code):
    """
    Generate a WhatsApp URL with worker details & completion OTP for the customer.
    """
    feedback_url = request.build_absolute_uri(
        reverse('feedback:submit') + f"?booking_id={booking.id}&worker_id={booking.worker.id}"
    )

    message = (
        f"Hello {booking.customer_name}!\n\n"
        f"Here are the details of the worker assigned to you:\n"
        f"👷 Name: {booking.worker.name}\n"
        f"📞 Contact: {booking.worker.contact_number}\n"
        f"🔹 Category: {booking.worker.category}\n"
        f"🛠 Skill: {booking.worker.skill_type}\n"
        f"⏳ Experience: {booking.worker.years_of_experience} years\n\n"
        f"📌 *Your Work Completion OTP: {otp_code}*\n\n"
        f"🔹 Share this OTP with the worker only when the work is completed.\n\n"
        f"⭐ Once the work is completed, please give your feedback here:\n"
        f"{feedback_url}"
    )

    phone = booking.customer_contact.strip()
    if not phone.startswith("+"):
        phone = "+91" + phone.lstrip("0")

    encoded_msg = quote(message)
    return f"https://wa.me/{phone}?text={encoded_msg}", message

def send_booking_notification_email(booking, event_type='created'):
    """
    Send SMTP email notification for booking events.
    """
    try:
        if event_type == 'created':
            subject = f"Karmi Mitra - Booking Confirmation #{booking.id}"
            message = (
                f"Dear {booking.customer_name},\n\n"
                f"Your booking request for worker '{booking.worker.name}' ({booking.worker.category}) has been submitted successfully.\n\n"
                f"Work Details: {booking.work_details}\n"
                f"Status: {booking.status}\n\n"
                f"Thank you for choosing Karmi Mitra!"
            )
            recipient_list = [booking.customer_email]
            if booking.worker.email:
                recipient_list.append(booking.worker.email)

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipient_list,
                fail_silently=True,
            )

        elif event_type == 'completed':
            subject = f"Karmi Mitra - Work Completed for Booking #{booking.id}"
            message = (
                f"Dear {booking.customer_name},\n\n"
                f"The work for booking #{booking.id} by worker {booking.worker.name} has been marked as Completed.\n"
                f"Please leave your feedback and rating to help us serve you better.\n\n"
                f"Best regards,\nKarmi Mitra Team"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[booking.customer_email],
                fail_silently=True,
            )
    except Exception as e:
        print(f"Email notification error: {e}")
