from ..models import Employe, User, TypeEmploye, Gestionnaire
from ..utils import dateutils
from ..errors import InvalidPrimaryKeyError, IncompatibleProfessionError
from django.db import transaction, IntegrityError


def _creer_default(matricule, password=None,nom="",prenom="",email="", user_type=0):
  """
  Crée un objet Utilsateur ayant comme username le matricule passé en paramètre.
  Returns:
    - Une instance de User non-commité (pas enregistrer dans la bd).
  """
  try:
    _user = User.objects.get(username=matricule)
    raise ValueError("Erreur: le matricule utilisé est déjà assigné à un autre utilisateur")
  except User.DoesNotExist:
    pass

  if not password or len(password) == 0:
    raise ValueError("Erreur: le mot de passe ne pas être vide")

  user = User(username=matricule,
    is_staff=True, 
    is_active=True,
    last_name=nom,
    first_name=prenom,
    email=email,
    user_type=user_type)
  user.set_password(password)
  return user

def creer_gestionnaire(profession, matricule, password=None,nom="",prenom="",email=""):
  """
  Enregistre un nouveau gestionnaire dans la BD.
  Args:
    - profession (:obj: Profession): La profession de l'employé
    - matricule (str) : Identifiant unique utilisé par la classe `User` comme `username`.
  Returns:
    - Une instance de Gestionnaire commité
  """
  if not profession:
    raise ValueError("Erreur: la profession ne peut pas être null")
  with transaction.atomic():
    user = _creer_default(matricule=matricule,password=password,nom=nom,prenom=prenom,email=email,user_type=2)
    user.save()
    gestionnaire = Gestionnaire.objects.create(user=user, profession=profession)
    return gestionnaire

def creer_employe(profession, matricule, type_employe=TypeEmploye.TPR, password=None, nom="", prenom="", email="", date_debut=dateutils.now()):
  """
  Enregistre un nouvel employé dans la BD.
  Args:
    - profession (:obj: Profession): La profession de l'employé
    - matricule (str) : Identifiant unique utilisé par la classe `User` comme `username`.
    - type_employe (TPR|TPO|TP) : Le type d'employé
  Returns:
    - Une instance d'Employe commité
  """
  if not profession:
    raise ValueError("Erreur: la profession ne peut pas être null")

  with transaction.atomic():
    user = _creer_default(matricule=matricule,password=password,nom=nom,prenom=prenom,email=email, user_type=3)
    user.save()
    employe = Employe.objects.create(user=user, 
      profession=profession, 
      type_employe=type_employe,
      date_debut=date_debut)
    return employe



