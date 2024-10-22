from django.contrib import admin
from django.urls import path, include
from homepage.views import HomepageView
from tournament import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomepageView.as_view(), name='homepage'),
    path('tournament/', include('tournament.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('users.urls')),  # Include users URLs
]