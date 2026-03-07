"""
Django forms for user registration and cart operations.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    """
    Custom signup form - extends Django's UserCreationForm
    with email field for better user identification.
    """
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class AddToCartForm(forms.Form):
    """Simple form to add product to cart with quantity."""
    quantity = forms.IntegerField(min_value=1, max_value=99, initial=1)
