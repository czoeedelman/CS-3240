from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.urls import reverse

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_signup_redirect_url(self, request):
        return '/'

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # If the user is already logged in and trying to connect another account
        if request.user.is_authenticated:
            return

        # If this social account already exists, just login
        if sociallogin.is_existing:
            return

        # If we get here, it's a new account
        try:
            # Get email from social account
            email = sociallogin.account.extra_data['email']
            # Continue to the signup form
            return
        except KeyError:
            pass

    def get_connect_redirect_url(self, request, socialaccount):
        return '/'

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        return user 