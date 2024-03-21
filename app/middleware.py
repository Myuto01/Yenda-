from django.http import HttpResponseRedirect
from django.urls import reverse

class PreventPasswordResetMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define the URLs that you want to prevent logged-in users from accessing
        password_reset_urls = [
            reverse('app:reset_password'),
            reverse('app:password_reset_done'),
            reverse('app:password_reset_complete'),
        ]

        if request.user.is_authenticated and request.path in password_reset_urls:
            # If the user is logged in and trying to access a password reset URL,
            # redirect them to a different page, such as the dashboard
            return HttpResponseRedirect(reverse('app:dashboard'))  # Change 'dashboard' to your desired URL
        
        response = self.get_response(request)
        return response
