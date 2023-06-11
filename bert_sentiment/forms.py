from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, UsernameField, \
    PasswordResetForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _

from .models import User, History


class UserProfileForm(forms.ModelForm):
    bio = forms.CharField(
        max_length=500,
        widget=forms.Textarea(
            attrs={
                'rows': 4,
                'cols': 40,
                'class': 'form-control',
                'placeholder': 'Bio',
            }
        ),
        label="New Password",
        required=False,
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'bio',)

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_permissions = self.fields.get("user_permissions")
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related(
                "content_type"
            )


class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
    )
    password2 = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email',)

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            })
        }


class LoginForm(AuthenticationForm):
    username = UsernameField(
        label=_("Your Username"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"})
    )
    password = forms.CharField(
        label=_("Your Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
    )


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email'
    }))


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        max_length=50,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "autofocus": True,
                'class': 'form-control',
                'placeholder': 'Old Password'
            }
        ),
    )
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
    )


class SentimentAnalyzerForm(forms.ModelForm):
    text_data = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(
            attrs={
                'rows': 5,
                'cols': 40,
                'class': 'form-control',
                'placeholder': 'Enter you text for analyze',
            }
        ),
        label="Sentiment Analyzer",
        required=True,
    )

    class Meta:
        model = History
        fields = ('text_data',)
