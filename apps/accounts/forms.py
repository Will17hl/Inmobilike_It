from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import get_language


def current_language_is_english():
    return (get_language() or "").split("-")[0] == "en"

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Usuario"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Contraseña"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if current_language_is_english():
            self.fields["username"].label = "Username"
            self.fields["username"].widget.attrs["placeholder"] = "Username"
            self.fields["password"].label = "Password"
            self.fields["password"].widget.attrs["placeholder"] = "Password"

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder": "Correo"}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if current_language_is_english():
            self.fields["username"].label = "Username"
            self.fields["email"].label = "Email"
            self.fields["email"].widget.attrs["placeholder"] = "Email"
            self.fields["password1"].label = "Password"
            self.fields["password2"].label = "Password confirmation"
