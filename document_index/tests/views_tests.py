from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.test.client import RequestFactory
from rest_framework import status
from document_index.views import GroupList, GroupDetail
from document_index.models import Group
import document_index
from factories import GroupTreeListFactory, GroupFactory


class GroupListViewTest(TestCase):
    """
    TODO: This class may be superceded.
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
                username='test', email='test@_', password='secret')

    def test_group_list_with_tree(self):
        GroupTreeListFactory(name='test').save()
        request = self.factory.get('/groups/')
        request.user = self.user
        group_list_view = GroupList.as_view()
        response = group_list_view(request)
        self.assertEqual(response.status_code, 200)

    def test_group_list_without_tree(self):
        request = self.factory.get('/groups/')
        request.user = self.user
        group_list_view = GroupList.as_view()
        response = group_list_view(request)
        self.assertEqual(response.status_code, 200)


class GroupListCreateViewWithoutTreeTest(TestCase):
    """
    Test group create without pre-existing tree.
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
                username='test', email='test@_', password='secret')

    def test_create_group_post_root_without_tree(self):
        """Create a new group via POST before tree exists."""
        post_data = {'parent': 0, 'name': 'Group Node Name Root',
                     'description': 'Group Node Description Root',
                     'comment': 'Group Node Comment Root'}
        client = Client()
        client.login(username='test', password='secret')
        response = client.post('/groups/', post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class GroupListCreateViewWithTreeTest(TestCase):
    """
    Test list and create view.
    """
    def setUp(self):
        """Setup the tests."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
                username='test', email='test@_', password='secret')
        self.tree = GroupTreeListFactory(name='test')
        self.tree.save()
        tree_id = self.tree.id
        self.group = Group.add_root(tree_id=tree_id, owner=self.user,
            name='test group name', description='test group description',
            comment='test group comment')

    def test_create_group_post_root(self):
        """Create a new root group via POST."""
        post_data = {'parent': 0, 'name': 'Group Node Name Root',
                     'description': 'Group Node Description Root',
                     'comment': 'Group Node Comment Root'}
        client = Client()
        client.login(username='test', password='secret')
        response = client.post('/groups/', post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_group_post_child(self):
        """Create a new child group via POST."""
        post_data = {'parent': 1, 'name': 'Group Node Name Child',
                     'description': 'Group Node Description Child',
                     'comment': 'Group Node Comment Child'}
        client = Client()
        client.login(username='test', password='secret')
        response = client.post('/groups/', post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_group_get(self):
        """
        GET a list of groups consisting of only 1 which was created in setUp().
        """
        client = Client()
        client.login(username='tesst', password='secret')
        response = client.get('/groups/')
        self.assertEqual(response.data[0]['name'], 'test group name')
        self.assertEqual(response.data[0]['description'],
                'test group description')
        self.assertEqual(response.data[0]['comment'], 'test group comment')
        self.assertEqual(response.data[0]['owner'], 'test')


class GroupDetailRetrieveUpdateDestroyTest(TestCase):
    """
    Tests for the GroupDetail view which implements Retrieve, Update, and
    Destroy methods.
    """
    pass
