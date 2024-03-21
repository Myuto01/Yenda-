# reservation_system/urls.py

from django.urls import path
from . import views


app_name = 'reservation_system'

urlpatterns = [
    path('register/', views.register, name='register-bus'),  # Note the trailing slash in the URL pattern
    path('', views.bus_operator_dashboard, name='bus_operator_dashboard'),
    path('login', views.login_register, name="bus-operator-login"),
    path('Detail Entry', views.detail_entry, name="detail-entry"), 
    path('qrcode-scanner/', views.qr_code_scanner, name='qrcode-scanner'),
    path('verify-ticket/', views.verify_ticket, name='verify_ticket'),
]
