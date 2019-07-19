from django.shortcuts import render
from ..decorators import gestionnaire_required, employe_required
from ..services import conge_service, horaire_service
from ..models import MotifConge, QuartChoix, Horaire, Jour
from django.shortcuts import redirect
from ..utils import dateutils
from datetime import datetime


@gestionnaire_required
def demandes_conge(request):
    gestionnaire = request.gestionnaire
    horaire = horaire_service.get_horaire_courant(
        profession=gestionnaire.profession)
    demandes = conge_service.get_demandes_attentes(horaire)
    print(demandes)
    context = {
        "conges_page": "active",
        "demandes": demandes,
    }
    return render(request, "demandes_conge.html", context)


@gestionnaire_required
def approuver_conge(request):
    employe = request.POST.get("employe")
    jour = request.POST.get("jour")
    conge_service.accepter_conge(employe=employe, jour=jour)
    return redirect("/conges/")


@gestionnaire_required
def refuser_conge(request):
    employe = request.POST.get("employe")
    jour = request.POST.get("jour")
    conge_service.refuser_conge(employe=employe, jour=jour)
    return redirect("/conges/")


@employe_required
def demande_conge(request):
    employe = request.employe
    motifs = MotifConge.__members__.items()
    horaire = horaire_service.get_horaire_courant(
        profession=employe.profession)
    demandes_conge = conge_service.get_demandes_employe(
        employe=employe, horaire=horaire)
    context = {
        "conge_page": "active",
        "motifs": motifs,
        "horaire_id": horaire.id,
        "conges": [(a, b, c.name.replace('_', ' ')) for a, b, c in demandes_conge]
    }
    return render(request, "demande_conge.html", context)


@employe_required
def traiter_formulaire_conge(request):
    employe = request.employe
    horaire = Horaire.objects.get(id=int(request.POST.get("horaire")))
    date = request.POST.get("jour")
    jour = Jour.objects.get(date=datetime.strptime(
        date, "%Y-%m-%d"), horaire__profession=employe.profession)
    quarts = [q for q in QuartChoix]
    motif = MotifConge(request.POST.get("motif"))
    raison = request.POST.get("raison")
    conge_service.creer_demande_conge(
        employe=employe, jour=jour, quarts=quarts, motif=motif, raison=raison)
    return redirect("/conges/employe/")
