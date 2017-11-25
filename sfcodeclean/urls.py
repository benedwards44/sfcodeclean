"""sfcodeclean URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView

from codescanner import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^auth/callback/$', views.AuthCallbackView.as_view(), name='auth-callback'),
    url(r'^logout/$', TemplateView.as_view(template_name="logout.html"), name='logout'),

    url(r'^job/scanning/(?P<slug>[-\w]+)/$', views.JobProcessingView.as_view(), name='job-scanning'),
    url(r'^job/status/(?P<slug>[-\w]+)/$', views.JobStatusView.as_view(), name='job-status'),
    url(r'^job/json/(?P<slug>[-\w]+)/$', views.JobJsonView.as_view(), name='job-json'),
    url(r'^job/(?P<slug>[-\w]+)/$', views.JobView.as_view(), name='job'),

    url(r'^apexclass/(?P<pk>\d+)/$', views.ApexClassBodyView.as_view(), name='apex-class-body'),
]
