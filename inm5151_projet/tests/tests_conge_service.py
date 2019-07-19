from ..services import horaire_service, user_service, conge_service, disponibilite_service, jour_service
from ..models import *
from django.test import TestCase
from ..utils import dateutils
from django.db import IntegrityError

class CongeTestCase(TestCase):
  
  def setUp(self):
    for quart in QuartChoix:
      Quart.objects.create(periode=quart.value)
    self.profession = Profession.objects.create(nom="Profession A")
    a1 = Activite.objects.create(nom="A1",profession=self.profession)
    a2 = Activite.objects.create(nom="A2",profession=self.profession)
    a3 = Activite.objects.create(nom="A3",profession=self.profession)
    self.activites = [a1, a2, a3]
    self.horaire = horaire_service.get_horaire_courant(profession=self.profession)
    self.employe1 = user_service.creer_employe(
      profession=self.profession,
      matricule="1",
      type_employe=TypeEmploye.TPR,
      password="Test1234"
    )
    self.employe2 = user_service.creer_employe(
      profession=self.profession,
      matricule="2",
      type_employe=TypeEmploye.TPR,
      password="Test1234"
    )
    disponibilite_service.creer_centres_activites(
      employe=self.employe1,
      horaire=self.horaire,
      activites=[a1, a2, a3]
    )
    # Cellule de demain.
    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    disponibilites = disponibilite_service.creer_disponibilites(jour=jour, quarts=[QuartChoix.JOUR, QuartChoix.NUIT], employe=self.employe1)
    jour_service.assigner_employe(
      jour=jour,
      employe=self.employe1,
      quart_to_activite={
        QuartChoix.JOUR: a1
      }
    )
  
  def test_creation_de_conge(self):
    quarts = [q for q in QuartChoix]
    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    employe = self.employe1
    my_demande = conge_service.creer_demande_conge(employe=employe,jour=jour,quarts=quarts,motif=MotifConge.Ferie)
    une_demande = Conge.objects.get(employe=employe,jour=jour)
    self.assertEqual(my_demande.id, une_demande.id)

  def test_accepter_conge(self):
    quarts = [q for q in QuartChoix]
    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    employe = self.employe1
    my_demande = conge_service.creer_demande_conge(employe=employe,jour=jour,quarts=quarts,motif=MotifConge.Ferie)
    conge_service.accepter_conge(employe, jour)
    une_demande = Conge.objects.get(employe=employe,jour=jour)
    self.assertEqual(une_demande.status, StatusConge.ACCEPTE.value)

  def test_verifier_delete_disponibilites(self):
    quarts = [q for q in QuartChoix]
    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    employe = self.employe1
    my_demande = conge_service.creer_demande_conge(employe=employe,jour=jour,quarts=quarts,motif=MotifConge.Ferie)
    conge_service.accepter_conge(employe, jour)
    self.assertTrue(not Disponibilite.objects.filter(employe=employe,jour=jour).exists())

  def test_verifier_delete_assignation(self):
    quarts = [q for q in QuartChoix]
    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    employe = self.employe1
    my_demande = conge_service.creer_demande_conge(employe=employe,jour=jour,quarts=quarts,motif=MotifConge.Ferie)
    conge_service.accepter_conge(employe, jour)
    self.assertTrue(not Assignation.objects.filter(employe=employe,jour=jour).exists())

  def test_refuser_conge(self):
    quarts = [q for q in QuartChoix]
    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    employe = self.employe1
    my_demande = conge_service.creer_demande_conge(employe=employe,jour=jour,quarts=quarts,motif=MotifConge.Ferie)
    conge_service.refuser_conge(employe, jour)
    self.assertRaises(Conge.DoesNotExist, Conge.objects.get, employe=employe, jour=jour)

  def test_get_conges_employe(self):
    quarts = [q for q in QuartChoix]
    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    employe = self.employe1
    my_demande = conge_service.creer_demande_conge(employe=employe,jour=jour,quarts=quarts,motif=MotifConge.Ferie)
    conge_service.accepter_conge(employe, jour)
    conge_employe = conge_service.get_conges_employe(employe=employe,horaire=self.horaire)
    self.assertTrue((employe.id, jour.id) in conge_employe)

  def test_get_conges(self):
    quarts = [q for q in QuartChoix]
    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    employe1 = self.employe1
    employe2 = self.employe2
    conge_service.creer_demande_conge(employe=employe1,jour=jour,quarts=quarts,motif=MotifConge.Ferie)
    conge_service.creer_demande_conge(employe=employe2,jour=jour,quarts=quarts,motif=MotifConge.Ferie)
    conge_service.accepter_conge(employe1, jour)
    conge_service.accepter_conge(employe2, jour)
    conges = conge_service.get_conges(horaire=self.horaire)
    self.assertTrue((employe1.id, jour.id) in conges and (employe2.id, jour.id) in conges)

  def test_get_demandes_employe(self):
    quarts = [q for q in QuartChoix]
    jour = self.horaire.jour_set.get(date=dateutils.prochain_jour(dateutils.now()))
    employe = self.employe1
    my_demande = conge_service.creer_demande_conge(employe=employe,jour=jour,quarts=quarts,motif=MotifConge.Ferie)
    conge_employe = conge_service.get_demandes_employe(employe=employe,horaire=self.horaire)
    self.assertTrue((employe.id, jour.id, StatusConge.EN_ATTENTE.value) in conge_employe)
