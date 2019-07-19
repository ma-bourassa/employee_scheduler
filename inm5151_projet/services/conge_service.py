from ..models import Conge, StatusConge, Disponibilite, Employe, Jour
from . import jour_service
from django.db import transaction


def creer_demande_conge(employe, jour, motif, quarts, raison=None):
    try:
        demande = Conge.objects.get(
            employe=employe, jour=jour)
        if demande.status == StatusConge.EN_ATTENTE.value:
            return ValueError("La demande existe déjà")
        else:
            demande.delete()
    except Conge.DoesNotExist:
        pass
    quarts2 = [quart.model for quart in quarts]
    with transaction.atomic():
        demande = Conge(employe=employe, jour=jour,
                        motif=motif.value, raison=raison)
        demande.save()
        demande.quarts.set(quarts2)
        demande.save()
        return demande


def accepter_conge(employe, jour):
    try:
        demande = Conge.objects.get(employe=employe, jour=jour)
        if demande.status == StatusConge.ACCEPTE.value:
            return

        with transaction.atomic():
            demande.status = StatusConge.ACCEPTE.value
            demande.save()
            for quart in demande.quarts.all():
                try:
                    jour_service.retirer_employe_at(
                        employe=employe, jour=jour, quart=quart.enum)
                except Exception as e:
                    pass
            Disponibilite.objects.filter(jour=jour, employe=employe).delete()
    except Conge.DoesNotExist:
        pass


def refuser_conge(employe, jour):
    try:
        demande = Conge.objects.get(employe=employe, jour=jour)
        demande.status = StatusConge.REFUSEE.value
        demande.save()
    except Conge.DoesNotExist:
        pass


def get_conges_employe(employe, horaire):
    jours = horaire.jours().values_list('id', flat=True)
    conges = Conge.objects.filter(jour__id__in=jours, employe=employe,
                                  status=StatusConge.ACCEPTE.value).values_list('employe', 'jour')
    return list(conges)


def get_demandes_employe(employe, horaire):
    jours = horaire.jours().values_list('id', flat=True)
    conges = Conge.objects.filter(jour__id__in=jours, employe=employe).values_list(
        'motif', 'jour', 'status')
    conges = [(motif, Jour.objects.get(
        id=jour_id), StatusConge(status)) for motif, jour_id, status in conges]
    print(conges)
    return conges


def get_conges(horaire):
    conges = [get_conges_employe(employe, horaire)
              for employe in horaire.profession.employes]
    return filter(None, sum(conges, []))


def get_demandes_attentes(horaire):
    jours = horaire.jours().values_list('id', flat=True)
    conges = Conge.objects.filter(
        jour__id__in=jours, status=StatusConge.EN_ATTENTE.value)
    return conges
