"""pri URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from rentals import views as rentals_views

urlpatterns = [
    path('spork/', admin.site.urls),

    # This is an example of directly registering an app's views in the central site's urls.py. As the site grows,
    # it might be better for each app dir to have its own urls.py and for this file to include that app's urls.py
    # at a specified mount point.
    path('', rentals_views.HomeView.as_view(), name='home'),
]
