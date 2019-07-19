from ..models import Horaire, Jour, QuartChoix, Profession
from ..utils.dateutils import daterange, ajouter_28_jours, now, dernier_isojour, prochain_jour, normalize
from django.db import transaction, IntegrityError
from datetime import datetime, timedelta

def _creer_horaire(profession, debut):
  """
  Ajoute un horaire dans la base de données.
  préconditions: 
    - Il ne faut pas q'un horaire dont la porté des dates début et fin
      contienne la date `debut` passé en paramètre.
  """
  if debut.isoweekday() != 7:
    raise ValueError("La date de départ pour un horaire doit être un dimanche.")
    
  norm_debut = normalize(debut)
  norm_fin = normalize(ajouter_28_jours(norm_debut))
  with transaction.atomic():
    horaire = Horaire(date_debut=norm_debut, date_fin=norm_fin, profession=profession)
    horaire.save()
    for date_cellule in daterange(norm_debut, norm_fin):
      jour = Jour(horaire=horaire, date=date_cellule)
      jour.save()
    return horaire

def get_horaire_at(profession, date):
  """
  Retourne l'horaire pour une profession et où la date passé
  en paramètre fait partie de l'intervalle: 
  horaire.date_debut <= date <= horaire.date_fin.
  Sinon retourne None.
  """
  horaires = Horaire.objects.filter(profession=profession, 
                                    date_debut__lte=date, 
                                    date_fin__gt=date)
  if horaires.exists():
    assert len(horaires) == 1, "Il est supposé avoir qu'une seul horaire par porté de date"
    return horaires[0]
  
  return None

def get_horaire_courant(profession):
  """
  Retourne l'horaire courant d'une profession
  préconditions:
    - La profession passé en paramètre doit être valide.
  """
  assert profession != None

  today = now()
  horaire = get_horaire_at(profession=profession, date=today)
  if not horaire:
    date_depart_horaire = dernier_isojour(today, jour=7) # Dernier dimanche
    try:
      horaire = _creer_horaire(profession=profession, debut=date_depart_horaire)
    except IntegrityError as error:
      # Peut etre que l'horaire à déjà été créé entre temps.
      horaire = get_horaire_at(profession=profession, date=today)
      assert horaire != None
      return horaire
  
  return horaire

def get_prochain_horaire(profession):
  """
  Retourne le prochain horaire qui débutera après l'horaire courant.
  """
  horaire_courant = get_horaire_courant(profession)
  debut_prochain = date=horaire_courant.date_fin
  prochain_horaire = get_horaire_at(profession=profession, date=debut_prochain)

  if not prochain_horaire:
    prochain_horaire = _creer_horaire(profession=profession, debut=debut_prochain)

  return prochain_horaire

