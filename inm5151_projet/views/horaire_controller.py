from django.shortcuts import render
from ..services import horaire_service, jour_service
from ..decorators import gestionnaire_required, employe_required
from ..utils import dateutils
from ..frontend_models import HoraireFE, HoraireEmployeFE
from ..models import Jour, Employe, QuartChoix, Activite, Assignation
from django.http import HttpResponseBadRequest, HttpResponseServerError, HttpResponse
from ..errors import ConflitHoraireError
import json

@employe_required
def horaire_employe(request):
  employe = request.employe
  horaire_choisi = request.GET.get('horaire_choisi')

  if horaire_choisi is None or horaire_choisi == "courant":
    horaire_choisi = "courant"
    horaire = horaire_service.get_horaire_courant(profession=employe.profession)
  else:
    horaire = horaire_service.get_prochain_horaire(profession=employe.profession)
  dates = [date for date in dateutils.daterange(debut=horaire.date_debut, fin=horaire.date_fin)]
  horaire = HoraireEmployeFE(horaire, employe)
  context = {
    "horaire_page": "active",
    "horaire": horaire,
    "dates": dates,
    "horaire_choisi": horaire_choisi,
    }
  return render(request, "horaire_employe.html", context)

@employe_required
def horaire_general(request):
  employe = request.employe
  horaire_choisi = request.GET.get('horaire_choisi')

  if horaire_choisi is None or horaire_choisi == "courant":
    horaire_choisi = "courant"

    horaire = horaire_service.get_horaire_courant(profession=employe.profession)
  else:

    horaire = horaire_service.get_prochain_horaire(profession=employe.profession)
    
  jours = horaire.jours()
  dates = [date for date in dateutils.daterange(debut=horaire.date_debut, fin=horaire.date_fin)]
  mid = len(dates) // 2
  now = dateutils.now()
  semaine_choisie = request.GET.get('semaine_set')
  
  if semaine_choisie is not None:
    now = dates[mid-1] if semaine_choisie == "1" else dates[mid]
  else:
    semaine_choisie = "2"

  date_milieu = dates[mid-1]
  if now > date_milieu:
    dates = dates[mid:]
    semaine_choisie = "2"
  else:
    dates = dates[:mid]
    semaine_choisie = "1"

  jours = jours[:mid]
  horaireFE = HoraireFE(horaire)
  un_horaire = horaireFE.semaines_selon_date(date=now)
  context = {
    "horaire_general_page": "active",
    "horaire_id": horaire.id,
    "dates": dates,
    "horaire": un_horaire,
    "horaire_choisi": horaire_choisi,
    "semaine_choisie" : semaine_choisie,
    "profession" : employe.profession
    }
  return render(request, "horaire_general.html", context)


@gestionnaire_required
def planification_horaire(request):
  gestionnaire = request.gestionnaire
  horaire_choisi = request.GET.get('horaire_choisi')

  if horaire_choisi is None or horaire_choisi == "courant":
    horaire_choisi = "courant"

    horaire = horaire_service.get_horaire_courant(profession=gestionnaire.profession)
  else:

    horaire = horaire_service.get_prochain_horaire(profession=gestionnaire.profession)
    
  jours = horaire.jours()
  dates = [date for date in dateutils.daterange(debut=horaire.date_debut, fin=horaire.date_fin)]
  mid = len(dates) // 2
  now = dateutils.now()
  semaine_choisie = request.GET.get('semaine_set')
  
  if semaine_choisie is not None:
    now = dates[mid-1] if semaine_choisie == "1" else dates[mid]
  else:
    semaine_choisie = "2"

  date_milieu = dates[mid-1]
  if now > date_milieu:
    dates = dates[mid:]
    semaine_choisie = "2"
  else:
    dates = dates[:mid]
    semaine_choisie = "1"

  jours = jours[:mid]
  horaireFE = HoraireFE(horaire)
  un_horaire = horaireFE.semaines_selon_date(date=now)
  context = {
    "horaire_page": "active",
    "horaire_id": horaire.id,
    "dates": dates,
    "horaire": un_horaire,
    "horaire_choisi": horaire_choisi,
    "semaine_choisie" : semaine_choisie,
    "profession" : gestionnaire.profession
    }
  return render(request, "planification.html", context)

@gestionnaire_required
def assigner_employe(request, horaire_id):
  body = json.loads(request.body)
  print(body)
  try:
    jour = Jour.objects.get(pk=body["jour_id"])
    employe = Employe.objects.get(pk=body["employe_id"])
    quart_to_activite = dict()
    for quart_periode, activite_id in body["quart_to_activite"].items():
      if activite_id is None:
        continue
      quart_to_activite[QuartChoix(int(quart_periode))] = Activite.objects.get(pk=activite_id)
    jour_service.assigner_employe(jour=jour, employe=employe,quart_to_activite=quart_to_activite)
    return render(request, "cellule_horaire.html", {'quart_to_activite': quart_to_activite}, status=201)
  except Jour.DoesNotExist:
    return HttpResponseBadRequest("La journée sélectionné n'existe pas")
  except Employe.DoesNotExist:
    return HttpResponseBadRequest("L'employé sélectionné n'existe pas")
  except Activite.DoesNotExist:
    return HttpResponseBadRequest("Une ou plusieurs activité choisi n'existe pas")
  except ValueError as error:
    return HttpResponseBadRequest(str(error))
  except ConflitHoraireError as error:
    return HttpResponseBadRequest(str(error))
  except Exception as error:
    print(str(error))
    return HttpResponseServerError("Erreur interne: désolé de l'incovénient veuillez réessayer un peu plus tard")

@gestionnaire_required
def retirer_employe(request, horaire_id, employe_id, jour_id):
    try:
        assignations = Assignation.objects.filter(
          employe_id=employe_id,
          jour_id=jour_id
        )
        for assignation in assignations:
            assignation.delete()
        return HttpResponse(status=204)
    except Jour.DoesNotExist:
        return HttpResponseBadRequest("La journée sélectionné n'existe pas")
    except Employe.DoesNotExist:
        return HttpResponseBadRequest("L'employé sélectionné n'existe pas")
    except Exception as error:
        print(str(error))
        return HttpResponseServerError("Erreur interne: désolé de l'incovénient veuillez réessayer un peu plus tard")


