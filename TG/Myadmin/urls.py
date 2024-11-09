from django.urls import path
from Myadmin import views

urlpatterns = [
    path('', views.ahome, name='ahome'),
    path('Orders',views.aorder,name='aorder'),
    path('Employee',views.aemployee,name='aemployee')
]