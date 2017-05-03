from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.directory, {'directory': settings.ROOT_ID}, name='directory'),
    url(r'^login$', views.login,{'template_name': 'login.html'}),
    url(r'^latest/$', views.latest, {'type':'all'}, name='latest'),
    url(r'^latest/1080p$', views.latest, {'type':'1080p'}, name='latest'),
    url(r'^latest/720p$', views.latest, {'type':'720p'}, name='latest'),
    url(r'^latest/SD$', views.latest, {'type':'SD'}, name='latest'),
    url(r'^(?P<directory>.*?)/$', views.directory, name='directory'),
    url(r'^(?P<fileId>.*)/(?P<fileName>.*)$', views.download, name='download'),
]

