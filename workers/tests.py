from django.test import TestCase
from workers.models import Worker

class WorkerModelTest(TestCase):
    def setUp(self):
        self.worker = Worker.objects.create(
            name="Test Worker",
            age=25,
            gender="Male",
            category="Plumber",
            contact_number="9999999999",
            email="test.worker@example.com",
            city_name="Bhubaneswar",
            skill_type="Pipe Repair",
            experience_level="Intermediate",
            years_of_experience=3
        )

    def test_worker_creation(self):
        self.assertEqual(self.worker.name, "Test Worker")
        self.assertEqual(self.worker.availability, "Yes")
        self.assertEqual(str(self.worker), "Test Worker (Plumber) - Bhubaneswar")
