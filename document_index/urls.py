from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from document_index import views

urlpatterns = patterns('',
    url(r'^api-auth/', include('rest_framework.urls',
        namespace='rest_framework')),
    url(r'^oauth2/', include('provider.oauth2.urls', namespace='oauth2')),
    url(r'^groups/parent/(?P<pk>[0-9]+)/$', views.GroupList.as_view(),
        name='group-list'),
    url(r'^groups/(?P<pk>[0-9]+)/$', views.GroupDetail.as_view(),
        name='group-detail'),
    url(r'groups/annotated_list/(?P<pk>[0-9]+)/$',
        views.GroupAnnotatedList.as_view(), name='group-annotated-list'),
    url(r'^groups/(?P<pk>[0-9]+)/move/$', views.GroupMove.as_view(),
        name='group-move'),
    url(r'^groups/(?P<pk>[0-9]+)/delete/$', views.GroupDetail.as_view(),
        name='group-delete'),
    url(r'^documents/$', views.DocumentList.as_view(), name='document-list'),
    url(r'^documents/(?P<pk>[0-9]+)/$',
        views.DocumentDetail.as_view(), name='document-detail'),
    url(r'^sources/(?P<pk>[0-9]+)/$',
        views.SourceDetail.as_view(), name='source-detail'),
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
