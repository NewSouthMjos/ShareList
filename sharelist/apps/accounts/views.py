from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, CustomUserAuthenticationForm

class SignUpView(generic.CreateView):
    """View for sign up page"""
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class LoginView(LoginView):
    """View for login page"""
    authentication_form = CustomUserAuthenticationForm
    success_url = reverse_lazy('mainpage')
    template_name = 'registration/login.html'
