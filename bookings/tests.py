from django.test import TestCase
from workers.models import Worker
from bookings.models import Booking
from bookings.services import generate_secure_otp

class BookingFlowTest(TestCase):
    def setUp(self):
        self.worker = Worker.objects.create(
            name="Mason Worker",
            age=35,
            gender="Male",
            category="Mason",
            contact_number="9876543210",
            email="mason@example.com",
            city_name="Cuttack",
            skill_type="Brickwork",
            experience_level="Expert",
            years_of_experience=8
        )

    def test_booking_and_otp_verification(self):
        otp_code = generate_secure_otp(6)
        self.assertEqual(len(otp_code), 6)

        booking = Booking.objects.create(
            worker=self.worker,
            customer_name="John Customer",
            customer_age=30,
            customer_address="123 Street",
            customer_contact="9123456789",
            customer_email="john@example.com",
            work_details="Need wall construction",
            otp=otp_code
        )

        self.assertEqual(booking.status, "Pending")
        self.assertFalse(booking.otp_verified)

        # Simulate OTP Verification
        if booking.otp == otp_code:
            booking.status = "Completed"
            booking.otp_verified = True
            booking.save()

        self.assertEqual(booking.status, "Completed")
        self.assertTrue(booking.otp_verified)
