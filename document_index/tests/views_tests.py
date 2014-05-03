import copy
import json
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import (APIRequestFactory, APIClient,
        force_authenticate)
from rest_framework import status
from document_index.views import GroupList, GroupDetail
from document_index.models import Group, GroupTreeList
import document_index
from factories import GroupTreeListFactory, GroupFactory


class GetGroupPostData(object):
    """
    Supporting class. Reduce duplication.
    """
    group_post_data = {
            'name': 'Group Node Name Root',
            'description': 'Group Node Description Root',
            'comment': 'Group Node Comment Root',
    }

    @classmethod
    def get_group_post_data(cls):
        return copy.copy(cls.group_post_data)


class GroupListViewTest(TestCase):
    """
    TODO: This class may be superceded.
    """
    def setUp(self):
        self.user = User.objects.create_user(
                username='test', email='test@_', password='secret')

    def test_group_list_with_tree(self):
        GroupTreeListFactory(name='test').save()
        client = APIClient()
        client.login(username='test', password='secret')
        response = client.get('/groups/parent/0/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_group_list_without_tree(self):
        client = APIClient()
        client.login(username='test', password='secret')
        response = client.get('/groups/parent/0/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GroupListCreateViewWithoutTreeTest(TestCase):
    """
    Test group create without pre-existing tree.
    """
    def setUp(self):
        self.user = User.objects.create_user(
                username='test', email='test@_', password='secret')

    def test_create_group_post_root_without_tree(self):
        """Create a new group via POST before tree exists."""
        data = GetGroupPostData.get_group_post_data()
        factory = APIRequestFactory()
        view = GroupList.as_view()
        request = factory.post('/groups/parent/', data, format='json')
        force_authenticate(request, self.user)
        response = view(request, pk=0)
        group = Group.objects.get(name='Group Node Name Root')
        tree = GroupTreeList.objects.get(name='test')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(group.description, 'Group Node Description Root')
        self.assertEqual(tree.name, 'test')


class GroupListCreateViewWithTreeTest(TestCase):
    """
    Test group list and create view.
    """
    def setUp(self):
        """Setup the tests."""
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
        data = GetGroupPostData.get_group_post_data()
        factory = APIRequestFactory()
        view = GroupList.as_view()
        request = factory.post('/groups/parent/0/', data, format='json')
        force_authenticate(request, self.user)
        response = view(request, pk=0)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_group_post_child(self):
        """Create a new child group via POST."""
        data = GetGroupPostData.get_group_post_data()
        factory = APIRequestFactory()
        view = GroupList.as_view()
        request = factory.post('/groups/parent/', data, format='json')
        force_authenticate(request, self.user)
        response = view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_group_get(self):
        """
        GET a list of groups consisting of only 1 which was created in setUp().
        """
        factory = APIRequestFactory()
        view = GroupList.as_view()
        request = factory.get('/groups/parent/0/')
        force_authenticate(request, self.user)
        response = view(request, pk=0)
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
    def setUp(self):
        """Setup the tests."""
        self.user = User.objects.create_user(
                username='test', email='test@_', password='secret')
        self.tree = GroupTreeListFactory(name='test')
        self.tree.save()
        tree_id = self.tree.id
        self.group1 = Group.add_root(tree_id=tree_id, owner=self.user,
            name='test group 1 name', description='test group 1 description',
            comment='test group 1 comment')
        self.group2 = Group.add_root(tree_id=tree_id, owner=self.user,
            name='test group 2 name', description='test group 2 description',
            comment='test group 2 comment')
        self.group3 = Group.add_root(tree_id=tree_id, owner=self.user,
            name='test group 3 name', description='test group 3 description',
            comment='test group 3 comment')
        self.group4 = Group.add_root(tree_id=tree_id, owner=self.user,
            name='test group 4 name', description='test group 4 description',
            comment='test group 4 comment')

    def test_group_move(self):
        """
        Move group node to new parent.
        """
        client = APIClient()
        client.login(username='test', password='secret')
        gnode1 = Group.objects.get(name='test group 1 name')
        gnode2 = Group.objects.get(name='test group 2 name')
        move_url = '/groups/{0}/move/'.format(gnode2.id)
        move_data = {'parent': gnode1.id}
        response = client.patch(move_url, data=json.dumps(move_data),
                content_type='application/json')

        if response.status_code == 200:
            gnode_parent = Group.objects.get(name='test group 1 name')
            self.assertEqual(gnode1.id, gnode_parent.id)
        else:
            self.assertTrue(False)

    def test_group_update_put(self):
        gnode3 = Group.objects.get(name='test group 3 name')
        put_data = {'name': 'new test group 3 name',
                    'description': 'new test group 3 description',
                    'comment': 'new test group 3 comment',}
        client = APIClient()
        client.login(username='test', password='secret')
        put_url = '/groups/{0}/'.format(gnode3.id)
        response = client.put(put_url, data=json.dumps(put_data),
                content_type='application/json')
        if response.status_code == status.HTTP_200_OK:
            pass
            new_gnode3 = Group.objects.get(id=gnode3.id)
            self.assertEqual(new_gnode3.name, 'new test group 3 name')
            self.assertEqual(new_gnode3.description,
                    'new test group 3 description')
            self.assertEqual(new_gnode3.comment, 'new test group 3 comment')
        else:
            self.assertTrue(False)

    def test_group_update_patch(self):
        gnode4 = Group.objects.get(name='test group 4 name')
        patch_data = {'name': 'new test group 4 name',}
        client = APIClient()
        client.login(username='test', password='secret')
        patch_url = '/groups/{0}/'.format(gnode4.id)
        response = client.patch(patch_url, data=json.dumps(patch_data),
                content_type='application/json')
        if response.status_code == status.HTTP_200_OK:
            new_gnode4 = Group.objects.get(id=gnode4.id)
            self.assertEqual(new_gnode4.name, 'new test group 4 name')
        else:
            self.assertTrue(False)

