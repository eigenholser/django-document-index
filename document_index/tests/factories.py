import factory
from django.contrib.auth.models import Group, Permission, User
from document_index.models import GroupTreeList, Group


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    username = 'test'
    email = 'test@_'
    password = 'secret'

class GroupTreeListFactory(factory.Factory):
    FACTORY_FOR = GroupTreeList

    name = factory.Sequence(lambda n: 'Tree {0}'.format(n))
    description = factory.Sequence(lambda n: 'Description {0}'.format(n))


class GroupFactory(factory.Factory):
    FACTORY_FOR = Group

    tree = factory.SubFactory(GroupTreeListFactory)
    owner = factory.SubFactory(UserFactory)
    name = 'Test Group'
    description = 'Group for running tests'
    comment = 'Comment for test group'
