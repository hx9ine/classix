from django import forms


class LoginForm(forms.Form):
    """
    Form for collecting user credentials.
    Authentication is handled by AuthenticationService.
    """
    
    email = forms.EmailField(
        label="Email",
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "autofocus": True,
                "placeholder": "Enter your email",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "placeholder": "Enter your password",
            }
        ),
    )

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()