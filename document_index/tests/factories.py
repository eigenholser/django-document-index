import factory
from django.contrib.auth.models import Group, Permission
from document_index.models import GroupTreeList


class GroupTreeListFactory(factory.Factory):
    FACTORY_FOR = GroupTreeList

    name = factory.Sequence(lambda n: 'Tree {0}'.format(n))
    description = factory.Sequence(lambda n: 'Description {0}'.format(n))
