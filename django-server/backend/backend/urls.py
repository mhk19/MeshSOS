"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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

from rest_framework.urlpatterns import format_suffix_patterns
from mainapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rlogs/', views.rloglist.as_view()),
    path('sendmsg/', views.SendDownlinkMsg.as_view()),
    path('register/', views.Register.as_view()),
    path('login/', views.Login.as_view()),
    path('user/', views.User.as_view()),
    path('vehicleLocation/', views.EmergencyVehicleLocation.as_view())
]
