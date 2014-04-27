from django.db import models
from treebeard.mp_tree import MP_Node


class GroupTreeList(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    created = models.DateTimeField('Date Created', auto_now_add=True)
    modified = models.DateTimeField('Date Last Modified', auto_now=True)

    def __unicode__(self):
        return self.name


class Group(MP_Node):
    node_order_by = ['name']
    parent = 0

    id = models.AutoField(primary_key=True)
    tree = models.ForeignKey(GroupTreeList)
    owner = models.ForeignKey('auth.User', related_name='dgroups')
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=256, blank=True)
    comment = models.CharField(max_length=1024, blank=True)
    created = models.DateTimeField('Date Created', auto_now_add=True)
    modified = models.DateTimeField('Date Last Modified', auto_now=True)

    def __unicode__(self):
        return self.name


class Document(models.Model):
    document_id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1024)
    created = models.DateTimeField('date created', auto_now_add=True)
    modified = models.DateTimeField('date last modified', auto_now=True)
    source_count = models.IntegerField(default=0)
    comment = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Document, self).save(*args, **kwargs)

    def get_group_id(self):
        return self.group_id


class Source(models.Model):
    source_id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, related_name='sources')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1024)
    sequence = models.IntegerField(default=1)
    filename = models.CharField(max_length=1024)
    mime_type = models.CharField(max_length=50)
    comment = models.CharField(max_length=1024)
    created = models.DateTimeField('date created', auto_now_add=True)
    modified = models.DateTimeField('date last modified', auto_now=True)

    class Meta:
        unique_together = (('source_id', 'sequence'),)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        sequence = Source.objects.filter(
            document_id= \
            self.document_id).aggregate(models.Max('source_id'))['source_id__max']
        if (not sequence):
            self.sequence = 1
        else:
            self.sequence = sequence + 1
        super(Source, self).save(*args, **kwargs)
