from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from document_index.models import GroupTreeList, Group, Document, Source

class SourceInline(admin.TabularInline):
    model = Source
    extra = 1
    fieldsets = [
        (None, {'fields': ['name', 'description', 'filename', 'mime_type',
                           'comment']}),
    ]


class DocumentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['group', 'name', 'description', 'comment']}),
    ]
    inlines = [SourceInline]
    list_display = ('name', 'description', 'created')
    list_filter = ['created']
    search_fields = ['description']


class GroupAdmin(TreeAdmin):
    form = movenodeform_factory(Group)
    #fields = ['tree', 'owner', 'name'] #, 'description', 'comment']
    #exclude = ['owner']
    list_filter = ('owner',)

#   def save_model(self, request, obj, form, change):
#       obj.save()


admin.site.register(Document, DocumentAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(GroupTreeList)
