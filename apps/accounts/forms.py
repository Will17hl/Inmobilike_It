from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": _("Usuario")}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": _("Contrasena")}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = _("Usuario")
        self.fields["username"].widget.attrs["placeholder"] = _("Usuario")
        self.fields["password"].label = _("Contrasena")
        self.fields["password"].widget.attrs["placeholder"] = _("Contrasena")


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder": _("Correo")}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = _("Usuario")
        self.fields["username"].widget.attrs["placeholder"] = _("Usuario")
        self.fields["email"].label = _("Correo")
        self.fields["email"].widget.attrs["placeholder"] = _("Correo")
        self.fields["password1"].label = _("Contrasena")
        self.fields["password2"].label = _("Confirmacion de contraseña")
