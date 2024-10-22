from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('resend-activation/', views.resend_activation_email, name='resend_activation'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.auth_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('', include('django.contrib.auth.urls')),  # Include auth URLs here
]