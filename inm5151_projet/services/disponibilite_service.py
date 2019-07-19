from ..models import Disponibilite, Employe, Horaire, Jour, CentreActivite
from ..utils import dateutils
from ..errors import InvalidPrimaryKeyError, IncompatibleProfessionError
from django.db import transaction, IntegrityError

def creer_disponibilites(jour, quarts, employe):
  """
  Crée une disponiblité pour une journée de travail.
  Si la disponibilité existe déjà, elle sera écrasé par la nouvelle.
  Args:
    jour (:obj: Jour): La jour dans lequel l'employé souhaite déposé une disponibilité.
  Raises:
    ValueError: Si jour est égale à null ou
      si activites est égale à null ou
      si activites est une liste vide ou
      si la liste de quarts est vide ou null.
    InvalidPrimaryKeyError: Si la clé primaire du User n'existe pas.
    IncompatibleProfesssionError: Si la profession de l'employé ne correspond à la profession de la jour ou
      si les activités sélectionnés ne font pas partie de la profession.
  Returns:
    La nouvelle disponibilite qui a été créé, sinon null.
  """
  if jour == None:
    raise ValueError("La jour choisi ne peut pas être null")

  if not employe:
    raise ValueError("L'employé ne peut pas être null")
  
  profession = jour.horaire.profession

  if employe.profession != profession:
    raise IncompatibleProfessionError("L'employé ne fait pas partie de la profession", employe, profession)
  
  today = dateutils.now()
  #if jour.date < today:
  #  raise ValueError("Impossible d'envoyer des disponibilité sur une date déjà passé.")
  disponibilites = []
  with transaction.atomic():
    try:
      #print("allo", jour, quarts)
      Disponibilite.objects.filter(jour=jour, employe=employe).delete()
    except Disponibilite.DoesNotExist:
      pass
    for quart in quarts:
      disponibilite = Disponibilite.objects.create(
        jour=jour, 
        employe=employe, 
        quart=quart.model)
      disponibilites.append(disponibilite)
    return disponibilites


def creer_centres_activites(horaire, activites, employe):
  if len(activites) == 0:
    raise ValueError("Le nombre d'activités ne peut pas être 0")
  with transaction.atomic():
    try:
      old_c_a = CentreActivite.objects.get(horaire=horaire, employe=employe).delete()
    except CentreActivite.DoesNotExist:
      pass
    new_c_a = CentreActivite(horaire=horaire, employe=employe)
    new_c_a.save()
    new_c_a.activites.set(activites)
    new_c_a.save()
    return new_c_a 
    #return CentreActivite.objects.create(horaire=horaire, activites=set(activites), employe=employe)

def get_disponibilite_employe(horaire, employe):
  return Disponibilite.objects.filter(
    employe=employe,
    jour__date__gte=horaire.date_debut, 
    jour__date__lte=horaire.date_fin
  ).order_by('jour__date')

def vectorize_disponibilite_employe(horaire, employe):
  disponibilites = get_disponibilite_employe(horaire, employe)
  dates = [date for date in dateutils.daterange(horaire.date_debut, horaire.date_fin)]
  vec = [0 for _ in dates]
  i = 0
  j = 0
  while i < len(dates) and j < len(disponibilites):
    date1 = dates[i]
    date2 = disponibilites[j].jour.date
    if date1 < date2: i += 1
    elif date2 < date1: j += 1
    else:
      vec[i] = 1
      i += 1
  return vec

#def vectorize_assignation_employe(horaire, employe):


  


