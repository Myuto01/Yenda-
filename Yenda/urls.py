from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("app.urls")),
    path('reservation/', include('reservation_system.urls')),
    path('api-token-auth/', obtain_auth_token), #gives us access to token auth

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)