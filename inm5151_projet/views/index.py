from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
  context = {
    "home_page": "active",
    "title":"Accueil"
    }
  return render(request, "home.html", context)

@login_required
def profil(request):
  context = {"profil_page": "active"}
  return render(request, "profil.html", context)
