from django import forms
from django.contrib.auth.models import User
from .models import Account

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    
    # FLAW 4: No password strength validation - VULNERABILITY
    password = forms.CharField(widget=forms.PasswordInput)
    
    # FIX: Add password validation
    password = forms.CharField(
        widget=forms.PasswordInput,
        min_length=8,
        help_text="Password must be at least 8 characters long"
    )
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long")
        if password.isdigit():
            raise forms.ValidationError("Password cannot be entirely numeric")
        if password.lower() in ['password', '12345678', 'qwerty']:
            raise forms.ValidationError("Password is too common")
        return password

class TransferForm(forms.Form):
    from_account = forms.IntegerField(widget=forms.HiddenInput())
    to_account = forms.CharField(
        max_length=20,
        label="Recipient Account Number"
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01
    )
    description = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Optional description'})
    )