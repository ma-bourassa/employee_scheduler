from ..services import disponibilite_service, horaire_service, user_service, jour_service
from ..models import *
from django.test import TestCase
from ..utils import dateutils
from django.db import IntegrityError
from ..errors import ConflitHoraireError


class CelluleTestCase(TestCase):
  
  def setUp(self):
    for quart in QuartChoix:
      Quart.objects.create(periode=quart.value)
    self.profession = Profession.objects.create(nom="Profession A")
    self.a1 = Activite.objects.create(nom="A1",profession=self.profession)
    self.a2 = Activite.objects.create(nom="A2",profession=self.profession)
    self.a3 = Activite.objects.create(nom="A3",profession=self.profession)
    self.horaire = horaire_service.get_horaire_courant(profession=self.profession)
    self.employe = user_service.creer_employe(
      profession=self.profession,
      matricule="1",
      type_employe=TypeEmploye.TPR,
      password="Test1234"
    )
  
  def test_assigner_employe(self):
    disponibilite_service.creer_centres_activites(
      employe=self.employe,
      horaire=self.horaire,
      activites=[self.a1, self.a2, self.a3]
    )

    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    disponibilite = disponibilite_service.creer_disponibilites(
      jour=jour, 
      quarts=[QuartChoix.JOUR],
      employe=self.employe
    )
    jour_service.assigner_employe(
      jour=jour,
      employe=self.employe,
      quart_to_activite={
        QuartChoix.JOUR: self.a1
      }
    )
 
  def test_conflit_horaire_selon_disponibilite(self):
    quart_to_activite = {
      QuartChoix.JOUR: self.a1,
    }
    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    self.assertRaises(
      ConflitHoraireError, 
      jour_service.assigner_employe,
      jour=jour,
      employe=self.employe,
      quart_to_activite=quart_to_activite
    )
  
  def test_conflit_horaire_selon_activites(self):
    quart_to_activite = {
      QuartChoix.JOUR: self.a1,
    }

    disponibilite_service.creer_centres_activites(
      employe=self.employe,
      horaire=self.horaire,
      activites=[self.a2, self.a3]
    )

    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    disponibilite = disponibilite_service.creer_disponibilites(
      jour=jour, 
      quarts=[QuartChoix.JOUR],
      employe=self.employe
    )
    self.assertRaises(
      ConflitHoraireError, 
      jour_service.assigner_employe,
      jour=jour,
      employe=self.employe,
      quart_to_activite=quart_to_activite
    )
 
  def test_conflit_horaire_selon_quart(self):
    quart_to_activite = {
      QuartChoix.JOUR: self.a1,
    }

    disponibilite_service.creer_centres_activites(
      employe=self.employe,
      horaire=self.horaire,
      activites=[self.a1]
    )

    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    disponibilite = disponibilite_service.creer_disponibilites(
      jour=jour, 
      quarts=[QuartChoix.NUIT],
      employe=self.employe
    )
    self.assertRaises(
      ConflitHoraireError, 
      jour_service.assigner_employe,
      jour=jour,
      employe=self.employe,
      quart_to_activite=quart_to_activite
    )

  
  def test_retirer_employe(self):
    quart_to_activite = {
      QuartChoix.JOUR: self.a1,
    }

    disponibilite_service.creer_centres_activites(
      employe=self.employe,
      horaire=self.horaire,
      activites=[self.a1]
    )

    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    disponibilite = disponibilite_service.creer_disponibilites(
      jour=jour, 
      quarts=[QuartChoix.JOUR],
      employe=self.employe
    )
    jour_service.assigner_employe(
      jour=jour,
      employe=self.employe,
      quart_to_activite=quart_to_activite
    )
    jour_service.retirer_employe_at(employe=self.employe, jour=jour,quart=QuartChoix.JOUR)
  
  
  def test_retirer_employe_deja_retire(self):
    quart_to_activite = {
      QuartChoix.JOUR: self.a1,
    }

    disponibilite_service.creer_centres_activites(
      employe=self.employe,
      horaire=self.horaire,
      activites=[self.a1]
    )

    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    disponibilite = disponibilite_service.creer_disponibilites(
      jour=jour, 
      quarts=[QuartChoix.JOUR],
      employe=self.employe
    )
    jour_service.assigner_employe(
      jour=jour,
      employe=self.employe,
      quart_to_activite=quart_to_activite
    )
    jour_service.retirer_employe_at(employe=self.employe, jour=jour,quart=QuartChoix.JOUR)

    self.assertRaises(
      ValueError, 
      jour_service.retirer_employe_at,
      employe=self.employe,
      jour=jour,
      quart=QuartChoix.JOUR)