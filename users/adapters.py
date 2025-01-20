from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.urls import reverse

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        return reverse('core:home')
        
    def get_signup_redirect_url(self, request):
        return reverse('core:home')
        
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        user.username = user.email  # Define o username como email
        if commit:
            user.save()
        return user 