from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.test.client import RequestFactory
from rest_framework import status
from document_index.views import GroupList, GroupDetail
from document_index.models import Group
from document_index.permissions import IsOwnerOrReadOnly


class PermissionsTests(TestCase):
    """
    Test cases for permission classes.
    """

    def setUp(self):
        """
        Do setup for permissions tests.
        """
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
                username='test', email='test@_', password='secret')

    def test_has_object_permission_safe_method(self):
        """
        Test permission class method with safe method GET.
        """
        request = self.factory.get('/')
        request.user = self.user
        permission_class = IsOwnerOrReadOnly()
        has_permission = permission_class.has_object_permission(
                request, None, None)
        self.assertTrue(has_permission)

    def test_has_object_permission_unsafe_method(self):
        """
        Test permission class method with unsafe method POST.
        """
        request = self.factory.post('/')
        request.user = self.user
        obj = request
        obj.owner = self.user
        permission_class = IsOwnerOrReadOnly()
        has_permission = permission_class.has_object_permission(
                request, None, obj)
        self.assertTrue(has_permission)
