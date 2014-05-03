from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from document_index.models import GroupTreeList, Group, Document, Source
from document_index.serializers import (GroupSerializer, DocumentSerializer,
        SourceSerializer, UserSerializer)
from document_index.permissions import IsOwnerOrReadOnly


class GroupList(generics.ListCreateAPIView):
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def pre_save(self, obj):
        # TODO: conditionally if not already present.
        obj.owner = self.request.user

    def get_queryset(self, *args, **kwargs):
        # TODO: request.user available only if logged in user.
        try:
            if self.parent == 0:
                tree_id = GroupTreeList.objects.get(
                        name=self.request.user.username).id
                queryset = Group.get_root_nodes().filter(tree_id=tree_id)
            else:
                parent_node = Group.objects.get(id=self.parent)
                queryset = parent_node.get_children()
        except ObjectDoesNotExist:
            queryset = Group.objects.none()

        return queryset

    def get(self, request, *args, **kwargs):
        # Need parent_id for get_queryset()
        self.parent = int(kwargs['pk'])
        return super(GroupList, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Create new group node.
        Need parent_id
        """
        # needs error handling
        self.parent = int(kwargs['pk'])
        return super(GroupList, self).post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Override create method on CreateModelMixin to prevent double save.
        treebeard calls save() on node add. Maybe there is a way around that.
        """
        request.DATA['parent'] = kwargs['pk']
        serializer = self.get_serializer(data=request.DATA, files=request.FILES)

        if serializer.is_valid():
            self.pre_save(serializer.object)
            self.post_save(serializer.object, created=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                    headers=headers)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupAnnotatedList(APIView):
    """
    Implements API endpoint for retrieving an annotated list from any node in
    the group tree including the node itself.
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        # Need parent_id for get_queryset()
        self.parent = int(kwargs['pk'])
        queryset = None

        try:
            if self.parent == 0:
                tree_id = GroupTreeList.objects.get(
                        name=self.request.user.username).id
                queryset = Group.get_root_nodes().filter(tree_id=tree_id)
            else:
                parent_node = Group.objects.get(id=self.parent)
                queryset = parent_node.get_children()
        except ObjectDoesNotExist:
            queryset = Group.objects.none()


        master_annotated_list = []

        for parent_node in queryset:
            for child_node, info in parent_node.annotated_list():
                serializer = GroupSerializer(child_node,
                        context={'request': request})
                combined_data = dict(serializer.data.items() + info.items())
                master_annotated_list.append(combined_data)

        return Response(master_annotated_list, status=status.HTTP_200_OK)


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
        # TODO: conditionally if not already present.
        obj.owner = self.request.user

    def update(self, request, *args, **kwargs):
        """
        Update group instance. PUT replaces the entire object. Logic to reside
        in model object.
        """
        group_id = kwargs['pk']
        gnode = Group.objects.get(id=group_id)
        gnode.update_group_instance(request.DATA)
        # TODO: This response assumes success.
        serializer = self.serializer_class(gnode)
        return Response(serializer.data, status=status.HTTP_200_OK)


#   def partial_update(self, request, *args, **kwargs):
#       """
#       Partial update group instance. Is this even useful? It
#       """
#       group_id = kwargs['pk']
#       gnode = Group.objects.get(id=group_id)
#       gnode.update_group_instance(request.DATA)
#       # TODO: This response assumes success.
#       return Response({'detail': 'node updated'},
#               status=status.HTTP_206_PARTIAL_CONTENT)

    def delete(self, request, *args, **kwargs):
        """
        Delete group node. Logic to reside in model object. Do not allow
        delete if group has documents attached.
        """
        # TODO: Check for child nodes. Refuse to delete if child nodes exist.
        # Look into Treebeard exceptions if this is attempted.
        group_id = kwargs['pk']
        return Response({'detail': '{0} deleted'.format(group_id)},
            status=status.HTTP_204_NO_CONTENT)


class GroupMove(generics.UpdateAPIView):
    """
    Provide functionality for moving group node to be child of another group
    node. Logic to reside in model. HTTP verb will be PUT since this will be
    construed as an update of the entire group instance. Some fuzziness here.
    See https://tabo.pe/projects/django-treebeard/docs/1.61/api.html#treebeard.models.Node.move
    """
    def patch(self, request, *args, **kwargs):

        parent_id = request.DATA['parent']
        parent_node = Group.objects.get(id=parent_id)
        node_id = kwargs['pk']
        node = Group.objects.get(id=node_id)
        node.move(parent_node, 'sorted-child')
        # This response assumes success. Check and handle.
        return Response({'detail': 'node moved'}, status.HTTP_200_OK)




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
