from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms  import UserForm, PasswordForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.mail import send_mail
from .models import EmailConfirmationToken

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until email is confirmed
            user.save()
            token = EmailConfirmationToken.objects.create(email=user.email)
            send_confirmation_email(user.email, token.token)
            return redirect('users/email_confirmation_sent')
            # Redirect to a page informing the user that a confirmation email was sent
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def register(request):
    # ...existing registration code...


def send_confirmation_email(email, token):
    confirmation_url = request.build_absolute_uri(reverse('confirm_email', kwargs={'token': str(token)}))
    send_mail(
        'Confirm your email address',
        f'Please confirm your email address by clicking the following link: {confirmation_url}',
        'from@babynamer.ai',
        [email],
    )


def confirm_email(request, token):
    try:
        token = EmailConfirmationToken.objects.get(token=token)
        user = User.objects.get(email=token.email)
        user.is_active = True
        user.save()
        token.delete()
        return redirect('users/login')  # Redirect to the login page
    except (EmailConfirmationToken.DoesNotExist, User.DoesNotExist):
        return render(request, 'users/error.html', {'message': 'Invalid confirmation link'})

class LoginView(auth_views.LoginView):
    template_name = 'users/login.html'

class LogoutView(auth_views.LogoutView):
    template_name = 'users/logout.html'

class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'users/password_reset_form.html'

class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'

class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'

class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'

class LogoutView(auth_views.LogoutView):
    template_name = 'users/logout.html'



@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()

    else:
        user_form = UserForm(instance=request.user)

    return render(request, 'users/profile.html', {
        'user_form': user_form,
    })