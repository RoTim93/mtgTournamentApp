from django.contrib import admin
from django.urls import path, include
from homepage.views import HomepageView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomepageView.as_view(), name='homepage'),
    path('tournament/', include('tournament.urls')),
    path('accounts/', include('users.urls')),  # Include users.urls under accounts path
]