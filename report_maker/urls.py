"""report_maker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URL conf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include
from report import urls as report_urls
from account import urls as account_urls
from connection import urls as connection_urls
from django.contrib.auth import views as auth_views
from connection import views as connection_views
from report_maker import settings

urlpatterns = [
    path('login/', auth_views.login, {'template_name': 'account/login.html'}, name='login'),
    path('logout/', auth_views.logout, {'template_name': 'account/logout.html'}, name='logout'),
    path('admin/', admin.site.urls),
    path('account/', include((account_urls, 'account'), namespace='account')),
    path('report/', include((report_urls, 'report'), namespace='report')),
    path('connection/', include((connection_urls, 'connection'), namespace='connection')),
    path('', connection_views.main_page, name='main_page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
