# urls.py in the E_medi folder

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Include authentication URLs
    path('', include('E_Med.urls')),  # Include your app's URLs
]
