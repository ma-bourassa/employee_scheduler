from ..services import disponibilite_service, horaire_service, user_service
from ..models import *
from django.test import TestCase
from ..utils import dateutils
from django.db import IntegrityError

class DisponibiliteTestCase(TestCase):
  
  def setUp(self):
    for quart in QuartChoix:
      Quart.objects.create(periode=quart.value)
    self.profession = Profession.objects.create(nom="Profession A")
    a1 = Activite.objects.create(nom="A1",profession=self.profession)
    a2 = Activite.objects.create(nom="A2",profession=self.profession)
    a3 = Activite.objects.create(nom="A3",profession=self.profession)
    self.activites = [a1, a2, a3]
    self.horaire = horaire_service.get_horaire_courant(profession=self.profession)
  
  def test_creation_de_disponibilite(self):
    employe = user_service.creer_employe(
      profession=self.profession,
      matricule="1",
      type_employe=TypeEmploye.TPR,
      password="Test1234"
    )

    # Cellule de demain.
    quarts = [QuartChoix.JOUR, QuartChoix.NUIT]
    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    disponibilites = disponibilite_service.creer_disponibilites(jour=jour, quarts=quarts, employe=employe)

    self.assertEqual(len(disponibilites), 2)
    self.assertEqual(len(jour.disponibilites), 2)

  def test_reecriture_de_disponibilite(self):
    employe = user_service.creer_employe(
      profession=self.profession,
      matricule="1",
      type_employe=TypeEmploye.TPR,
      password="Test1234"
    )

    # Cellule de demain.
    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))

    quarts = [QuartChoix.JOUR, QuartChoix.NUIT]
    disponibilites = disponibilite_service.creer_disponibilites(jour=jour, quarts=quarts, employe=employe)
    quarts = [QuartChoix.JOUR]
    disponibilites = disponibilite_service.creer_disponibilites(jour=jour, quarts=quarts, employe=employe)
    self.assertEqual(len(disponibilites), 1)
    self.assertEqual(len(Disponibilite.objects.filter(jour=jour)), 1)

