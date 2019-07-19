import json
from datetime import timedelta
from django.shortcuts import render
from django.http import Http404, HttpResponseBadRequest, HttpResponse
from ..models import Disponibilite, Assignation, Horaire, Employe, Activite, QuartChoix, Jour, Quart, CentreActivite
from ..services import disponibilite_service, horaire_service
from ..decorators import employe_required
from ..utils import dateutils, postutils
from django.shortcuts import redirect
from django.contrib import messages
import math
import itertools

@employe_required
def get_formulaire_disponibilite(request):
  employe = request.employe
  activites = [(activite.id, activite.nom) for activite in Activite.objects.filter(profession=employe.profession)]
  quarts = [quart for quart in QuartChoix]
  horaire_choisi = request.GET.get('horaire_choisi')

  if horaire_choisi is None or horaire_choisi == "courant":
    horaire = horaire_service.get_horaire_courant(profession=employe.profession)
  else:
    horaire = horaire_service.get_prochain_horaire(profession=employe.profession)

  dates = [date for date in dateutils.daterange(debut=horaire.date_debut, fin=horaire.date_fin)]
  
  temp = []
  partition_size = int(math.sqrt(len(activites)))
  
  if partition_size > 4:
    partition_size += 1  # ajdust the size if the number of activities is too small.

  for limit in range(partition_size, len(activites), partition_size):
    temp.append(activites[limit-partition_size:limit])

  if len(activites[limit:]) > 0:
    temp.append(activites[limit:])
  temp = list(itertools.zip_longest(*temp))
  activites_partitionne = [list(filter(lambda x: x is not None, l)) for l in [list(t) for t in temp]]
  
  disponibilites_courantes = Disponibilite.objects.filter(
    employe=employe, 
    jour__id__in=[jour.id for jour in horaire.jours()]
  ).values_list('jour', 'quart')

  try:
    activites_courantes = CentreActivite.objects.get(employe=employe,horaire=horaire).activites.all().values_list('id', flat=True)
  except CentreActivite.DoesNotExist:
    activites_courantes = []

  jours = horaire.jours().values_list('id', flat=True)
  assignations_courantes = Assignation.objects.filter(employe=employe, jour__id__in=jours).values_list('jour', 'quart')
  
  context = { 
    "employe_id": employe.id,
    "horaire_id": horaire.id,
    "dates": dates,
    "jours": horaire.jours(),
    "disponibilites_courantes": list(disponibilites_courantes),
    "activites_courantes": activites_courantes,
    "activites_partitionne": activites_partitionne,
    "assignations_courantes": list(assignations_courantes),
    "semaines_set": [("Semaines 1-2", ":14"), ("Semaines 3-4", "14:")],
    "quarts": quarts,
  }
  return render(request, "formulaire_disponibilite.html", context)

@employe_required
def traiter_formulaire_dispo(request):
  body = postutils.body_to_dict(bytez=request.body)
  employe = request.employe
  horaire = Horaire.objects.get(id=int(body['horaire']))
  if horaire == horaire_service.get_horaire_courant(profession=employe.profession):
    horaire_choisi = "courant"
  else:
    horaire_choisi = "prochain"
  activites = Activite.objects.filter(pk__in=[int(k.split('-')[1]) for k,v in body.items() if k.startswith('activite') and v == "on"])
  if activites.count() == 0:
    messages.add_message(request, messages.ERROR, "Vous devez sélectionner au moins une activité.")
    return redirect('/disponibilites/formulaire_disponibilite.html?horaire_choisi='+horaire_choisi)

  quart_to_jour = [(QuartChoix(int(arr[1])), int(arr[2])) for arr in (k.split('-') for (k,_) in body.items() if k.startswith('disponibilite'))]
  jour_to_quarts = {jour_id: set() for (_,jour_id) in quart_to_jour}
  [jour_to_quarts[jour_id].add(QuartChoix(quart_id)) for (quart_id, jour_id) in quart_to_jour]
  temp = Disponibilite.objects.filter(
    employe=employe, 
    jour__id__in=[jour.id for jour in horaire.jours()]
  ).delete()
  for jour_id, quarts in jour_to_quarts.items():
    jour = Jour.objects.get(id=jour_id)
    disponibilite_service.creer_disponibilites(
      jour=jour,
      quarts=quarts,
      employe=employe,
    )
  try:
    CentreActivite.objects.get(horaire=horaire, employe=employe).delete()
  except CentreActivite.DoesNotExist:
    pass
  disponibilite_service.creer_centres_activites(horaire=horaire, employe=employe, activites=list(activites))
  messages.add_message(request, messages.SUCCESS, "Vos disponibilités ont étés mises à jour avec succès!")
  return redirect('/disponibilites/formulaire_disponibilite.html?horaire_choisi='+horaire_choisi)

def get_disponibilite_employe(request):
  employe_id = request.GET.get('employe_id')
  horaire_id = request.GET.get('horaire_id')
  semaine_choisie = int(request.GET.get('semaine_choisie'))
  if not employe_id or not horaire_id or not semaine_choisie:
    return HttpResponseBadRequest("Il faut l'id de l'employé de l'horaire et de la semaine choisie")

  employe = Employe.objects.get(id=employe_id)
  horaire = Horaire.objects.get(id=horaire_id)
  date_debut = horaire.date_debut
  if semaine_choisie == 2:
    date_debut += timedelta(days=14)

  dispo_vec = disponibilite_service.vectorize_disponibilite_employe(horaire,employe)
  return HttpResponse(json.dumps(dispo_vec))


def get(request):
  employe_id = request.GET.get('employe_id')
  jour_id = request.GET.get('jour_id')
  if not employe_id or not jour_id:
    return HttpResponseBadRequest("Il faut l'id de l'employé et celui de la journée choisie")

  jour = Jour.objects.get(id=jour_id)
  employe = Employe.objects.get(id=employe_id)
  disponibilites = Disponibilite.objects.filter(jour=jour, employe=employe).all()
  quarts_disponibles = [QuartChoix(d.quart.enum) for d in disponibilites]
  
  # Liste d'assignations en cours pour le ou les différents quarts de cette journée.
  temp = Assignation.objects.filter(jour=jour, employe=employe)
  assignations_courantes = {assignation.quart.enum: assignation.activite.id for assignation in temp}

  centre_activite = CentreActivite.objects.get(horaire=jour.horaire)
  if not disponibilites.exists():
    raise Http404("L'employe n'a émis aucune disponiblité pour cette journée")

  #for dispo in disponibilites:
  #  quart_to_activites[dispo.quart.enum] = dispo.activites.all()
  context = {
    "employe_id": employe_id,
    "jour_id": jour_id,
    "quarts_disponibles": quarts_disponibles,
    "centre_activite": centre_activite.activites.all(),
    "assignations_courantes": assignations_courantes,
  }
  return render(request, "assignation_popover.html", context)
  
  
  

