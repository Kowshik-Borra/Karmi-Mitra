from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

class AuthenticationAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_customer_registration(self):
        url = reverse('accounts:api_register_customer')
        data = {
            'username': 'newcustomer',
            'email': 'newcustomer@example.com',
            'password': 'Password123!',
            'first_name': 'Test',
            'last_name': 'Customer',
            'phone_no': '9988776655',
            'address': 'Test Address, Bhubaneswar'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertEqual(User.objects.filter(username='newcustomer').exists(), True)

    def test_jwt_login_success(self):
        User.objects.create_user(username='loginuser', password='SecretPassword123')
        url = reverse('accounts:api_login')
        response = self.client.post(url, {'username': 'loginuser', 'password': 'SecretPassword123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
