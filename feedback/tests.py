from django.test import TestCase
from django.db.models import Avg
from workers.models import Worker
from feedback.models import Feedback

class FeedbackRatingTest(TestCase):
    def setUp(self):
        self.worker = Worker.objects.create(
            name="Painter Worker",
            age=29,
            gender="Male",
            category="Painter",
            contact_number="9111111111",
            email="painter@example.com",
            city_name="Puri",
            skill_type="Painting",
            experience_level="Intermediate",
            years_of_experience=4
        )

    def test_average_rating_calculation(self):
        Feedback.objects.create(worker=self.worker, customer_name="Cust 1", rating=5)
        Feedback.objects.create(worker=self.worker, customer_name="Cust 2", rating=3)

        avg_rating = self.worker.feedbacks.aggregate(Avg('rating'))['rating__avg']
        self.worker.rating = round(avg_rating, 1)
        self.worker.save()

        self.assertEqual(float(self.worker.rating), 4.0)
