from rest_framework import serializers
from django.contrib.auth.models import User
from document_index.models import GroupTreeList, Group, Document, Source
from django.contrib.auth.models import User

class GroupSerializer(serializers.Serializer):
    group = serializers.HyperlinkedIdentityField(view_name='group-detail')
    owner = serializers.Field(source='owner.username')
    name = serializers.CharField(max_length=32)
    description = serializers.CharField(max_length=256)
    comment = serializers.CharField(max_length=1024)
    parent = serializers.IntegerField()
    numchild = serializers.SerializerMethodField('get_children_count')

    def restore_object(self, attrs, instance=None):
        """
        Override Serializer restore_object.
        """
        user = self.context['request'].user
        if instance is not None:
            instance.owner = user
            instance.name = attrs.get('name', instance.name)
            instance.description = attrs.get('description',
                    instance.description)
            instance.comment = attrs.get('comment', instance.comment)
            return instance

        parent_id = int(attrs.get('parent'))

        # This will fail once for the first root node. Then we create it.
        try:
            tree_id = GroupTreeList.objects.get(name=user.username).id
        except: # DoesNotExist
            tree = GroupTreeList(name=user.username)
            tree.save()
            tree_id = tree.id

        group = None
        if (parent_id == 0):
            # If this branch taken, there should be check for GroupTreeList

            # create new root node
            group = Group.add_root(
                tree_id = tree_id,
                owner = user,
                name=attrs.get('name'),
                description = attrs.get('description'),
                comment = attrs.get('comment'),
            )
        else:
            parent = Group.objects.get(id=parent_id)
            group = parent.add_child(
                tree_id = tree_id,
                owner = user,
                name=attrs.get('name'),
                description = attrs.get('description'),
                comment = attrs.get('comment'),
            )

        return group

    def get_parent_id(self, obj):
        """Parent node id."""
        parent = obj.get_parent()
        if (not parent):
            return None
        return obj.get_parent().id

    def get_children_count(self, obj):
        """Number of children below node."""
        return obj.get_children_count()


class SourceSerializer(serializers.ModelSerializer):
    source = serializers.HyperlinkedIdentityField(view_name='source-detail')

    class Meta:
        model = Source
        fields = ('source', 'document', 'name', 'description',
                  'sequence', 'filename', 'mime_type', 'comment', 'created',
                  'modified')


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    group = serializers.HyperlinkedRelatedField(view_name='group-detail')
    sources = SourceSerializer(many=True)

    class Meta:
        model = Document
        fields = ('document_id', 'group', 'name', 'description',
                  'created', 'modified', 'source_count',
                  'comment', 'sources')


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username')
