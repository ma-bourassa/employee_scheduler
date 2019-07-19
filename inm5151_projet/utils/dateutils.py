from datetime import datetime, timedelta
import pytz

def daterange(debut, fin):
  # code taken from https://stackoverflow.com/questions/1060279/iterating-through-a-range-of-dates-in-python
  for n in range(int ((fin - debut).days)):
    yield debut + timedelta(n)

def ajouter_28_jours(date_debut=datetime.today()):
  """
  Retourne la date 28 jours après la date_debut
  """
  dt = timedelta(days=28)
  return date_debut + dt

def dernier_isojour(date, jour=1):
  """
  Retourne la date du dernier jour de la semaine passé en paramètre.
  Les jours de la semaine sont numérotés de 1 à 7.
  """
  assert date is not None
  assert jour >= 1 and jour <= 7
  diff = date.isoweekday() - jour
  dt = timedelta(days=diff)
  if diff >= 0:
    return date - dt
  
  semaine_passe = date - timedelta(days=7)
  date_cible = semaine_passe - dt
  return date_cible

def prochain_jour(date):
  """
  Retourne la date qui suit immédiatement la date passé en paramètre.
  """
  return date + timedelta(days=1)

def now():
  """
  Retourne la date d'aujourd'hui avec l'heure,minute,seconde et microseconde mis à zéro.
  """
  return datetime.now()\
    .replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.UTC)

def normalize(date):
  """
  Remet à zéro les heures, minutes, secondes et microseconde d'une date.
  De plus, elle s'assure de lui assigner un timezone local.
  """
  return date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.UTC)

def now_precise():
  """
  Même chose que la fonction now(), sauf que l'heure, minute, seconde et microseconde 
  ne sont pas modifés. De plus, elle s'assure de lui assigner un timezone local.
  """
  return datetime.now(tzinfo=pytz.UTC)
