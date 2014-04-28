from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from document_index.models import GroupTreeList, Group, Document, Source
from document_index.serializers import (GroupSerializer, DocumentSerializer,
        SourceSerializer, UserSerializer)
from document_index.permissions import IsOwnerOrReadOnly


class GroupList(generics.ListCreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def pre_save(self, obj):
        obj.owner = self.request.user

    def get_queryset(self, *args, **kwargs):
        # TODO: request.user available only if logged in user.
        try:
            tree_id = GroupTreeList.objects.get(name=self.request.user.username).id
            queryset = Group.get_root_nodes().filter(tree_id=tree_id)
        except ObjectDoesNotExist:
            # This gets all root nodes for all users.
            queryset = Group.get_root_nodes()

        return queryset

    def post(self, request, *args, **kwargs):
        """Create new group node.
        Need parent_id
        """
        # needs error handling
        return super(GroupList, self).post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Override create method on CreateModelMixin to prevent double save.
        treebeard calls save() on node add. Maybe there is a way around that.
        """
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.post_save(serializer.object, created=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                    headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Handle Retrieve, Update, Destroy operations with HTTP verbs GET, PUT, and
    DELETE.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
            IsOwnerOrReadOnly,)

    def pre_save(self, obj):
        obj.owner = self.request.user

    def put(self, request):
        """
        Update group instance. PUT replaces the entire object. Logic to reside
        in model object.
        """
        pass

    def patch(self, request):
        """
        Partial update group instance.
        """

    def delete(self, request):
        """
        Delete group node. Logic to reside in model object. Do not allow
        delete if group has documents attached.
        """
        pass


class GroupMove(generics.UpdateAPIView):
    """
    Provide functionality for moving group node to be child of another group
    node. Logic to reside in model. HTTP verb will be PUT since this will be
    construed as an update of the entire group instance. Some fuzziness here.
    See https://tabo.pe/projects/django-treebeard/docs/1.61/api.html#treebeard.models.Node.move
    """
    pass


class DocumentList(generics.ListCreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class DocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class SourceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
