"""
Tests for document_index models.
"""
from django.test import TestCase
from document_index.models import GroupTreeList
from document_index.tests.factories import GroupTreeListFactory


class GroupTreeListTestCase(TestCase):
    """Group model tests."""

    def setUp(self):
        group_tree_list = GroupTreeListFactory()
        group_tree_list.save()

    def test_group_tree_list_create(self):
        group_tree_list = GroupTreeList.objects.get(id=1)
        self.assertEqual(group_tree_list.name, 'Tree 0')
        self.assertEqual(group_tree_list.__unicode__(), 'Tree 0')
