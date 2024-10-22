from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from .forms import RegisterForm, ResendActivationForm
from .forms import EmailAuthenticationForm
from django.contrib.auth.views import LoginView
from .forms import UpdateUsernameForm
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages


User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = f"http://{current_site.domain}/accounts/activate/{uid}/{token}/"
            message = render_to_string('registration/verification_email.html', {
                'user': user,
                'verification_link': verification_link
            })

            send_mail(
                mail_subject,
                '',
                'admin@yourdomain.com',
                [form.cleaned_data['email']],
                fail_silently=False,
                html_message=message
            )

            messages.success(request, 'Account created! Please check your email for verification.')
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully!')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return HttpResponse('Activation link is invalid!')


@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = UpdateUsernameForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UpdateUsernameForm(instance=user)

    context = {
        'form': form,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
    }
    return render(request, 'users/profile.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Check if the input is an email or a username
            if '@' in username_or_email:
                try:
                    user_obj = User.objects.get(email=username_or_email)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None
            else:
                user = authenticate(request, username=username_or_email, password=password)

            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    return redirect('homepage')  # Adjust the redirect as necessary
                else:
                    messages.error(request, "Account is inactive. Please check your email for verification.")
            else:
                messages.error(request, "Invalid login credentials.")
        else:
            messages.error(request, "Form validation failed. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def send_activation_email(user, request):
    current_site = get_current_site(request)
    mail_subject = 'Activate your account.'
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verification_link = f"http://{current_site.domain}/accounts/activate/{uid}/{token}/"
    message = render_to_string('registration/account_activation_mail.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': uid,
        'token': token,
        'verification_link': verification_link,  # Include the verification link
    })

    # Log the uid and token values
    print(f"UID: {uid}")
    print(f"Token: {token}")

    send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [user.email])



def resend_activation_email(request):
    if request.method == 'POST':
        form = ResendActivationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = User.objects.filter(email=email).first()

            if user and not user.is_active:
                current_site = get_current_site(request)
                mail_subject = 'Resend Activation - Activate your account.'
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                verification_link = f"http://{current_site.domain}/accounts/activate/{uid}/{token}/"
                message = render_to_string('registration/verification_email.html', {
                    'user': user,
                    'verification_link': verification_link
                })

                send_mail(
                    mail_subject,
                    '',
                    'admin@mtgtournament.com',
                    [email],
                    fail_silently=False,
                    html_message=message
                )

                messages.success(request, 'Activation email has been resent! Please check your email.')
                return redirect('login')
            else:
                messages.error(request, 'This account is either active or does not exist.')
    else:
        form = ResendActivationForm()

    return render(request, 'registration/resend_activation.html', {'form': form})

class CustomLoginView(LoginView):
    authentication_form = EmailAuthenticationForm

def auth_logout(request):
    logout(request)
    return redirect('homepage')