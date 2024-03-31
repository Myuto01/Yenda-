
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .utils import  hash_trip_id, decode_hashed_trip_id

app_name = 'app'

urlpatterns = [

   path("register-user", views.register_user, name="register-user"),
   path("login", views.login_register, name="login"),
   path("logout", views.logoutUser, name="logout"),
   path("", views.dashboard, name="dashboard"),
   path("popular-places", views.popular_places, name="popular places"),
   path('search/', views.search, name='search'),
   path('update_bookmark_status/', views.update_bookmark_status, name='update_bookmark_status'),
   path('bookmarked/', views.bookmarked_trips, name='bookmarked_trips'),
   path('select_tickets/<uuid:trip_id>/', views.select_tickets, name='select_tickets'),
   path('enter_passenger_details/<uuid:trip_id>/', views.enter_passenger_details, name='enter_passenger_details'),
   path('ticket_confirmation/<uuid:trip_id>/', views.ticket_confirmation, name='ticket_confirmation'),
   path('ticket_cancel', views.cancel_confirmation, name ='ticket-cancel'),
   path('ticket_success/<uuid:trip_id>/', views.ticket_success, name='ticket_success'),
   path('tickets', views.tickets, name='tickets'),
   path('update_ticket_active_status/<int:ticket_id>/', views.update_ticket_active_status, name='update_ticket_active_status'),
   path('previous-tickets', views.previous_tickets, name='previous-tickets'),
   path('account-details',views.user_account_details, name = 'account-details'),
   path('about-&-info', views.about_info, name = 'about-info'),
   path('change-name', views.change_name, name='change-name'),
   path('change-profile picture', views.change_profilepic, name='change-profile_pic'),

    
   #Courier Service
   path('courier-search/', views.courier_search, name='courier-search' ),
   path('enter-package-details/', views.enter_package_details, name = 'enter-package-details'),
   path('superuser/messages/', views.superuser_messages, name='superuser_messages'),
   path('inbox/', views.inbox_list, name='inbox-list'),
   path('conversation/<int:sender_id>/', views.conversation, name='conversation'),
   path('check-new-messages/', views.check_new_messages, name='check_new_messages'),
   path('mark-messages-as-read/', views.mark_messages_as_read, name='mark_messages_as_read'),
   path('package-payment/', views.package_payment, name='package-payment'),
   path('courier-receipts/', views.courier_receipts, name='courier-receipts'),
   path('edit/<int:message_id>/', views.edit_message, name='edit_message'),
   path('delete/<int:message_id>/', views.delete_message, name='delete_message'),
   path('toggle_active/<int:receipt_id>/', views.toggle_active, name='toggle_active'),
   path('courier-done/', views.fulfilled_receipts, name='courier-done'),

   
   #Customer Service
   #path('customer-service/message/<int:sender_id>/', views.customer_service_message, name='customer_service_message'),
   path('customer-service/inbox/', views.customer_service_inbox, name='customer_service_inbox'),
   path('submit_message/<int:sender_id>/', views.submit_message, name='submit_message'),


   #Suggestions
   path('submit-suggestion/', views.submit_suggestion, name='submit_suggestion'),


   #Forgot Password
   path('reset_password/',
   auth_views.PasswordResetView.as_view(
      template_name="../templates/registration/reset_password.html",
      success_url = reverse_lazy("app:password_reset_done")
   ), name='reset_password'),

   path('reset_password_sent/',
    auth_views.PasswordResetDoneView.as_view(
    ), name="password_reset_done"),

   path('reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
      template_name="registration/password_reset_confirm.html",
      success_url = reverse_lazy("app:password_reset_complete")
  ), name='password_reset_confirm'),

   path('reset_password_complete/',
    auth_views.PasswordResetCompleteView.as_view(
      template_name="registration/password_reset_complete.html"
    ), name="password_reset_complete"),


# DRF URLS
   path('ticket-confirmation/<uuid:trip_id>', views.TicketConfirmationAPIView.as_view(), name='ticket-confirmation'),

]  

# Add the following line to serve media files during development
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)























