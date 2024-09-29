from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status

class MenuViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('menu')  # Ensure this matches the name of your URL pattern
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_menu_view_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_menu_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # Assuming the user is not a manager, delivery crew, or customer

    def test_menu_view_authenticated_manager(self):
        self.user.is_staff = True  # Assuming is_staff is used to denote a manager
        self.user.save()
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)