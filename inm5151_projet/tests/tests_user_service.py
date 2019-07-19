from ..services import disponibilite_service, horaire_service, user_service
from ..models import Profession, Horaire, Disponibilite, Employe, TypeEmploye, User
from django.test import TestCase
from ..utils import dateutils
from django.db import IntegrityError

class UserTestCase(TestCase):
  
  def setUp(self):
    self.profession = Profession.objects.create(nom="Profession A")
    self.horaire = horaire_service.get_horaire_courant(profession=self.profession)
  
  def test_creation_gestionnaire(self):
    gestionnaire = gestionnaire = user_service.creer_gestionnaire(
      profession=self.profession,
      matricule="1",
      password="Test1234"
    )
    try:
      user = User.objects.get(username="1")
    except User.DoesNotExist:
      self.fail("Création de gestionnaire non réussi.") 

  def test_creation_employe(self):
    employe = user_service.creer_employe(
      profession=self.profession,
      matricule="1",
      type_employe=TypeEmploye.TPR,
      password="Test1234"
    )
    try:
      user = User.objects.get(username="1")
    except User.DoesNotExist:
      self.fail("Création d'employé non réussi.")
    
