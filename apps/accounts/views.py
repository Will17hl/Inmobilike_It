from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from apps.accounts.models import AgentProfile
from .forms import LoginForm, RegisterForm

class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm

    def form_valid(self, form):
        messages.success(self.request, "Bienvenido 👋")
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
            messages.success(request, "Cuenta creada ✅")
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
        # Activar host
        request.session["mode"] = "host"

        # ✅ crea AgentProfile si no existe (Airbnb-like: cualquiera puede ser host)
        AgentProfile.objects.get_or_create(user=request.user)

        messages.info(request, "Modo anfitrión activado ✅")
    else:
        # Volver a guest
        request.session["mode"] = "guest"
        messages.info(request, "Modo usuario activado ✅")

    return redirect(request.GET.get("next") or "home")