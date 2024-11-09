from django.urls import path
from vparnter import views

urlpatterns = [
    path('', views.vhome, name='vhome'),
    path('orders',views.vorder,name='vorder'),
    path('vprofile',views.vprofile,name='vprofile'),
    path('vlogin',views.vlogin,name='vlogin'),
    path('vregirestion',views.vregisration,name='vreg'),
    path('driver_reg',views.drive_reg,name='driver_reg'),
    path('vlogout',views.vlogout,name='vlogout'),
    path('vechile_reg',views.v_vechile_reg,name="v_vech_reg"),
    path('save-status/', views.save_vehicle_status, name='save_vehicle_status'),
    path('update-location/', views.update_location, name='update_location'),
    path('vehicle_profile_view',views.vehicle_profile_view,name='vehicle_profile_view'),
    path('myearning',views.myearning,name='env'),
    path('new_order',views.new_ord,name="new_ord"),
    path('passbook',views.vpassbook,name='vpass'),
    path('Auto',views.vauto,name='vauot'),
    path('notifications/', views.driver_notifications, name='driver_notifications'),
    path('update-notification-status/',views.update_notification_status, name='update_notification_status'),
    path('Operate',views.order_operation,name='order_opr'),
    path('validate-otp/', views.validate_otp, name='validate_otp'),  # Add this line
    path('update-order-status/', views.update_order_status, name='update_order_status'),
    path('save-verification-status/', views.save_verification_status, name='save_verification_status'),
    path('check-order-status/',views.check_order_status, name='check_order_status'),
    path('start-waiting-time/', views.start_waiting_time, name='start_waiting_time'),
    path('stop-waiting-time/', views.stop_waiting_time, name='stop_waiting_time'),
    path('download-passbook/', views.download_passbook, name='download_passbook'),
    path('delete-vehicle/<int:vehicle_id>/', views.delete_vehicle_view, name='delete_vehicle'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

]