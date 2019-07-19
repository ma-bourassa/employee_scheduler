import math
import random
from django.core.management.base import BaseCommand, CommandError
from ...models import *
from ...services import user_service, horaire_service, jour_service, disponibilite_service
from ...utils import dateutils
from django.db import transaction
from multiprocessing import Process, Pool

PASSWORD = 'Test1234'

class Command(BaseCommand):

  help = "Remplit la base de données de valeurs par défaut"

  def generate_disponibilites(self, profession):
    print("Génération aléatoire de disponibilités...")
    horaire = horaire_service.get_horaire_courant(profession)
    activites = set(profession.activites)
    employes = profession.employes
    quarts = [quart for quart in QuartChoix]
    jours = set(horaire.jours())

    for employe in employes:
      nb_disponibilites = random.randint(0, 28)
      shuffled_jours = random.sample(jours, len(jours))
      for i in range(nb_disponibilites):
        quarts_to_activites = dict()
        for quart in quarts:
          if random.choice([True, False]):
            shuffled_activites = random.sample(activites, len(activites))
            nb_activites = random.randint(1,len(shuffled_activites))
            quarts_to_activites[quart] = [shuffled_activites.pop() for _ in range(nb_activites)]

        if len(quarts_to_activites) > 0:
          disponibilite_service.creer_disponibilites(
            jour=shuffled_jours.pop(),
            quarts_to_activites=quarts_to_activites,
            employe=employe
          )
    print("fin génération aléatoire de disponibilités")

  def generate_professions(self, nb_profession):
    print("Génération aléatoire de %s professions..." % (nb_profession))
    profession_names = ["Profession " + str(i) for i in range(nb_profession)]
    result = []
    k = 0
    with transaction.atomic():
      for profession_name in profession_names:
          profession = Profession.objects.create(nom=profession_name)
          _activites = [Activite.objects.create(nom="Activite"+str(i), profession=profession) for i in range(k,k+5)]
          k += 5
          result.append(profession)
    
    print("Fin génération professions")
    return result

  def generate_employes(self, names, profession):
    print("Génération aléatoire de %s employés pour la profession: %s"%(len(names), profession.nom))
    for (name, number) in names:
      prenom, nom, *_ = name.split(' ')
      user_service.creer_employe(
        profession=profession,
        matricule="employe"+str(number),
        nom=nom,
        prenom=prenom,
        password=PASSWORD
      )

  def generate_personnel(self, names, professions):
    print("Génération du personnel pour toutes les professions...")
    shuffled_names = random.sample(names, len(names))
    for i, profession in enumerate(professions):
      prenom, nom, *_ = shuffled_names.pop(0).split(' ')
      user_service.creer_gestionnaire(
        profession=profession,
        matricule="gestionnaire"+str(i+1),
        password=PASSWORD,
        nom=nom,
        prenom=prenom,
      )

    #profession_partition = [0 for _ in range(len(professions))]
    profession_partition = [15, 15]
    
    # for i in range(len(shuffled_names)):
    #   k = random.randint(0, len(professions)-1)
    #   profession_partition[k] += 1

    shuffled_indexed_names = [(name, i+1) for i, name in enumerate(shuffled_names)]
    offset = 0
    for i, size in enumerate(profession_partition):
      name_subset = shuffled_indexed_names[offset:offset+size]
      self.generate_employes(name_subset, professions[i])
      offset += size
    
    print("Fin génération du personnel")

  def generate_all(self, filename):
    with open(filename, "r") as file:
      names = [line[:-1] for line in file]
      professions = self.generate_professions2()
      self.generate_personnel(names=names, professions=professions)
      #for profession in professions:
      #  self.generate_disponibilites(profession=profession)

  def generate_professions2(self):
    print("Génération professions...")
    activite_labo = ["Biochimie", "Hématologie", "Microbiologie", "Pathologie"]
    activite_inf = ["Urgence", "Observation", "Dialyse", "Pédiatrie", "Psychiatrie", "UETT", "Chirurgie", "5 Sud", "5 Nord", "6 Sud", "6 Nord", "7 Sud", "7 Nord"]
    profession_names = {
      "Technologiste médical" : activite_labo,
      "Infimière" : activite_inf
    }
    result = []
    with transaction.atomic():
      for profession_name, activite_names in profession_names.items():
          profession = Profession.objects.create(nom=profession_name)
          for activite_name in activite_names:
            Activite.objects.create(nom=activite_name, profession=profession)
          result.append(profession)
    
    print("Fin génération professions")
    return result

  def handle(self, *args, **options):
    
    for quart in QuartChoix:
      Quart.objects.create(periode=quart.value)

    self.generate_all(filename="random_names.txt")
    superuser = User(username="admin",email="admin@gmail.com")
    superuser.set_password("Bingo1234")
    superuser.is_superuser = True
    superuser.is_staff = True
    superuser.is_active = True
    superuser.save()

    
    
