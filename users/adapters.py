from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.urls import reverse

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        path = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
        return path
        
    def get_signup_redirect_url(self, request):
        path = request.GET.get('next', settings.LOGIN_REDIRECT_URL)
        return path
        
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.username = user.email  # Define o username como email
        if commit:
            user.save()
        return user 

    def is_open_for_signup(self, request):
        return True

    def get_email_verification_redirect_url(self, email_address):
        return reverse('core:home') 