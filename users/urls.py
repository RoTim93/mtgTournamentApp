from django.contrib.auth import views as auth_views
from django.urls import path,include
from . import views
from .views import register, CustomLoginView, activate



urlpatterns = [
    path('register/', register, name='register'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('resend-activation/', views.resend_activation_email, name='resend_activation'),
    path('login/', CustomLoginView.as_view(), name='login'),
    # path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('profile/', views.profile, name='profile'),

]