from django.http import HttpResponse
from django.db import connections
from django.db.utils import DatabaseError
from django.shortcuts import render

def home(request):
    return render(request, "core/home.html")


def healthz(request):
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        return HttpResponse("database unavailable", status=503, content_type="text/plain")

    return HttpResponse("ok", content_type="text/plain")
