from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    path("login", views.login),
    path("",views.home),
    path("logout",views.logout),
    path('charge', views.charge, name='charge'),
]
    