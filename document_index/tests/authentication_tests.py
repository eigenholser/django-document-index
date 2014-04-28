from django.contrib.auth.models import User
from django.test import TestCase
#from django.test.client import Client
from django.test.client import RequestFactory
from rest_framework import status
from document_index.authentication import SuperUserSessionAuthentication


class SuperUserSessionAuthenticationTestCases(TestCase):
    """
    Test cases for session authentication for superusers using the Django REST
    Framework browseable API.
    """

    def setUp(self):
        """
        Do setup for permissions tests.
        """
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
                username='test', email='test@_', password='secret')
        self.adminuser = User.objects.create_user(
                username='admin', email='admin@_', password='secret')
        self.adminuser.is_superuser=True
        self.adminuser.save()

    def test_superuserauthentication_superuser(self):
        """
        Test authentication when is superuser.
        """
        request = self.factory.get('/')
        request._request = request # something meaningful for real requests?
        request.user = self.adminuser
        authentication_class = SuperUserSessionAuthentication()
        is_authenticated = authentication_class.authenticate(request)
        self.assertTrue(is_authenticated)

    def test_superuserauthentication_notsuperuser(self):
        """
        Test authentication when not superuser.
        """
        request = self.factory.get('/')
        request._request = request # something meaningful for real requests?
        request.user = self.user
        authentication_class = SuperUserSessionAuthentication()
        is_authenticated = authentication_class.authenticate(request)
        self.assertFalse(is_authenticated)

    def test_superuserauthentication_nouser(self):
        """
        Test authentication with no user.
        """
        request = self.factory.get('/')
        request._request = request # something meaningful for real requests?
        request.user = None
        authentication_class = SuperUserSessionAuthentication()
        is_authenticated = authentication_class.authenticate(request)
        self.assertFalse(is_authenticated)
