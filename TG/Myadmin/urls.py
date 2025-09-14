from django.urls import path
from Myadmin import views

urlpatterns = [
    path('', views.ahome, name='ahome'),
    path('Orders',views.aorder,name='aorder'),
    path('Employee',views.aemployee,name='aemployee'),
    path('customers/', views.customer_list_view, name='customer_list'),
    path('partner-list/', views.partner_list, name='partner_list'),
    path('partner-details/<int:partner_id>/', views.partner_details_view, name='partner_details'),
    path('alogin',views.alogin,name='alogin'),
    path('alogout',views.alogout_view,name='alogout')
]