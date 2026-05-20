from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from apps.accounts.models import AgentProfile
from .forms import LoginForm, RegisterForm


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm

    def form_valid(self, form):
        messages.success(self.request, _("Bienvenido"))
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("home")


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Cuenta creada"))
            return redirect("home")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


@login_required
def toggle_mode(request):
    current = request.session.get("mode", "guest")

    if current == "guest":
        request.session["mode"] = "host"
        AgentProfile.objects.get_or_create(user=request.user)
        messages.info(request, _("Modo anfitrion activado"))
    else:
        request.session["mode"] = "guest"
        messages.info(request, _("Modo usuario activado"))

    return redirect(request.GET.get("next") or "home")
