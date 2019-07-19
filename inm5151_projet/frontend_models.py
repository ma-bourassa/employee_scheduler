from .models import Assignation, Disponibilite
from datetime import timedelta

class DisponibiliteFE:
  def __init__(self, disponibilite):
    pass

class CelluleFE:
  def __init__(self, employe, quart_to_activite, jour_id):
    self.employe = employe,
    self.quart_to_activite = quart_to_activite
    self.jour_id = jour_id

class HoraireFE:
  def __init__(self, horaire):
    # Il faut avoir les 28 journees
    # chaque journees vas avoir n cellule horaire ou n = nbre. employes
    jours = horaire.jours()
    employes = horaire.profession.employes
    self.employes_cellules = []
    self.horaire = horaire
    for employe in employes:
      cellules = []
      for jour in jours:
        assignations = Assignation.objects.filter(employe=employe, jour=jour)
        quart_to_activite = dict()
        cellule = CelluleFE(employe=employe, quart_to_activite=quart_to_activite, jour_id=jour.id)

        if assignations.exists():
          for ce in assignations:
            quart, activite = ce.quart.enum, ce.activite
            quart_to_activite[quart] = activite
        cellules.append(cellule)
      self.employes_cellules.append((employe, cellules))

  def semaines_selon_date(self, date):
    date_mid = self.horaire.date_debut + timedelta(days=13)
    mid = 14
    if date > date_mid:
      return [(e, cellules[mid:]) for (e, cellules) in self.employes_cellules]
    return [(e, cellules[:mid]) for (e, cellules) in self.employes_cellules]

class HoraireEmployeFE:
  def __init__(self, horaire, employe):
    self.horaire = horaire
    self.cellules = []
    jours = horaire.jours()
    for jour in jours:
      assignations = Assignation.objects.filter(employe=employe, jour=jour)
      quart_to_activite = dict()
      cellule = CelluleFE(employe=employe, quart_to_activite=quart_to_activite, jour_id=jour.id)
      
      if assignations.exists():
        for ce in assignations:
          quart, activite = ce.quart.enum, ce.activite
          quart_to_activite[quart] = activite
      self.cellules.append(cellule)
