from ..services import horaire_service
from ..models import Profession, Horaire
from django.test import TestCase
from ..utils import dateutils
from django.db import IntegrityError

class HoraireTestCase(TestCase):
  def setUp(self):
    Profession.objects.create(nom="Profession A")
    Profession.objects.create(nom="Profession B")
    Profession.objects.create(nom="Profession C")
    

  def test_get_horaire_courant(self):
    profession = Profession.objects.get(nom="Profession A")
    horaire = horaire_service.get_horaire_courant(profession)
    now = dateutils.now()
    debut = dateutils.dernier_isojour(now, 7)
    fin = dateutils.ajouter_28_jours(debut)
    self.assertEqual(horaire.date_debut, debut)
    self.assertEqual(horaire.date_fin, fin)
    pass

  def test_nombre_courant_horaire_profession_eq_1(self):
    profession = Profession.objects.get(nom="Profession A")
    # Après les 3 appels, il doit avoir eu une seule insertion
    # dans la bd.
    h1 = horaire_service.get_horaire_courant(profession)
    h2 = horaire_service.get_horaire_courant(profession)
    h3 = horaire_service.get_horaire_courant(profession)
    hs = Horaire.objects.filter(profession=profession, date_debut__lte=h1.date_debut)

    self.assertEqual(len(hs), 1)
    pass

  def test_empecher_creer_plusieurs_horaire_pour_meme_profession_et_meme_date(self):
    profession = Profession.objects.get(nom="Profession A")
    # Après les 3 appels, il doit avoir eu une seule insertion
    # dans la bd.
    today = dateutils.now()
    date_depart_horaire = dateutils.dernier_isojour(today, jour=7) # Dernier dimanche
    horaire = horaire_service._creer_horaire(profession=profession, debut=date_depart_horaire)
    self.assertRaises(IntegrityError, horaire_service._creer_horaire, profession=profession, debut=date_depart_horaire)
    pass

  def test_nombre_cellule_egale_28(self):
    profession = Profession.objects.get(nom="Profession A")
    horaire = horaire_service.get_horaire_courant(profession)
    self.assertEqual(len(horaire.jour_set.all()), 28)

  def test_creer_plusieurs_horaire_de_professions_differentes(self):
    profession1 = Profession.objects.get(nom="Profession A")
    profession2 = Profession.objects.get(nom="Profession B")
    horaire1 = horaire_service.get_horaire_courant(profession1)
    horaire2 = horaire_service.get_horaire_courant(profession2)

    self.assertTrue(horaire1 != None)
    self.assertTrue(horaire2 != None)