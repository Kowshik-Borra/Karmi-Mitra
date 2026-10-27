from django.test import TestCase
from decimal import Decimal
from workers.models import Worker
from recommendations.engine import rank_workers_for_request, classify_problem_description

class RecommendationEngineTestCase(TestCase):
    def setUp(self):
        self.w1 = Worker.objects.create(
            name="Ramesh Electrician",
            age=35,
            gender="Male",
            category="Electrician",
            contact_number="9999999999",
            email="ramesh@test.com",
            city_name="Bhubaneswar",
            skill_type="House Wiring",
            experience_level="Expert",
            years_of_experience=10,
            hourly_rate=Decimal('600.00'),
            latitude=Decimal('20.2961'),
            longitude=Decimal('85.8245'),
            rating=Decimal('4.9'),
            availability="Yes"
        )

    def test_ranking_returns_best_match(self):
        results = rank_workers_for_request(
            category="Electrician",
            skill_keyword="Wiring",
            cust_lat=20.2961,
            cust_lon=85.8245
        )
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]['worker'].id, self.w1.id)
        self.assertGreater(results[0]['match_score'], 80.0)

    def test_nlp_problem_classification(self):
        res = classify_problem_description("My kitchen sink pipe is leaking water everywhere")
        self.assertEqual(res['category'], 'Plumber')
        self.assertEqual(res['urgency'], 'Medium')
