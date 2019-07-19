from ..models import Jour, Employe, Disponibilite, Quart, Assignation, Activite, CentreActivite
from ..errors import ConflitHoraireError, IncompatibleProfessionError
from django.db import transaction

def assigner_employe(jour, employe, quart_to_activite):
  """
  Assigne un employé à une journée, un quart et une activité précise.
  Args:
    - jour (:obj: Jour) : correspond à journée de l'horaire.
    - employe (:obj: Employe) : correspond à l'employé à assigner
    - quarts_to_activite (:dict: QuartChoix: Activite) : Représente les quarts suivit de leur activité à accomplir.
  Returns: 
    - void
  Raises:
    - ValueError si la jour est null ou
        si l'employe est null ou
        si quarts_to_activite est vide ou null
    - ConflitHoraireError si l'employé n'a jamais offert de disponibilité pour ce jour ou
        si le quart ne fait pas partie d'une des disponibilités de l'employé pour ce jour ou
        si l'employé n'a pas offert une ou plusieurs activité dans la liste.

  """
  # Validation des objets
  if not jour:
    raise ValueError("Erreur: La jour ne peut pas être null")
  if not employe:
    raise ValueError("Erreur: L'employe ne peut pas être null")
  if not quart_to_activite or len(quart_to_activite) == 0:
    raise ValueError("Erreur: Chaque quart assigné à l'employé doit avoir une seule activité")

  profession = jour.horaire.profession
  activites = quart_to_activite.values()

  try:
    # Vérifications de l'existence des activités
    for activite in activites:
      _a = profession.activites.get(pk=activite.pk)
  except Activite.DoesNotExist:
    raise IncompatibleProfessionError("Erreur: l'une des activités ne fait pas partie de la profession de l'horaire.")
  
  try:
    # Est-ce qu'il existe une dispo. pour cette journée?
    disponibilites = jour.disponibilites.filter(employe=employe)

    if not disponibilites:
      raise Disponibilite.DoesNotExist

    centre_activite = CentreActivite.objects.get(employe=employe,horaire=jour.horaire)

    for (quart, activite) in quart_to_activite.items():
      dispo_quart = disponibilites.get(quart=quart.model)
      if activite not in centre_activite.activites.all():
        raise Activite.DoesNotExist

    
    with transaction.atomic():
      for (quart, activite) in quart_to_activite.items():
        Assignation.objects.create(
          employe=employe,
          activite=activite,
          quart=quart.model,
          jour=jour
        )
  except Disponibilite.DoesNotExist:
    raise ConflitHoraireError("Erreur: l'employé sélectionné n'a aucune disponibilité pour cette journée", Disponibilite)
  except Quart.DoesNotExist:
    raise ConflitHoraireError("Erreur: L'employé n'est pas disponible pour l'un ou plusieurs des quarts sélectionnés", Quart)
  except CentreActivite.DoesNotExist:
    raise ConflitHoraireError("Erreur: L'employé n'est pas disponible pour une ou plusieurs activités sélectionnées.", Activite)
  except Activite.DoesNotExist:
    raise ConflitHoraireError("Erreur: L'employé n'est pas disponible pour une ou plusieurs activités sélectionnées.", Activite)



def retirer_employe_at(employe, jour, quart):
  """
  Retire un employe d'une journée et à un quart précis.
  Args:
    - jour (:obj: Jour) : correspond à journée de l'horaire.
    - employe (:obj: Employe) : correspond à l'employé à assigner.
    - quart (:obj: QuartChoix) : Représente le quart de la journée.
  """
  try:
    cellule_employe = Assignation.objects.get(jour=jour,employe=employe,quart=quart.model)
    cellule_employe.delete()
  except Assignation.DoesNotExist:
    raise ValueError("Erreur: l'employé à retirer est déjà absent pour cette journée au quart spécifié")

