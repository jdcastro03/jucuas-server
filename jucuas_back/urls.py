"""jucuas_back URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('activity/manager/', include('activity_manager.urls')),
    path('presenter/', include('presenter.urls')),
    path('representative/', include('representative.urls')),
    path('reviewer/', include('reviewer.urls')),
    path('university/', include('university.urls')),
    path('activity/', include('activity.urls')),
    path('deadline/', include('deadline.urls')),
    path('auth/', include('accounts.urls')),
    re_path(r'^o/', include('oauth2_provider.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)