from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum
from .utils import dateutils


class StatusConge(Enum):
    ACCEPTE = 1
    EN_ATTENTE = 2
    REFUSEE = 3


class MotifConge(Enum):
    Ferie = "Férié"
    VD = "Vacance"
    Maladie = "Maladie Personnel"
    Autre = "Autre"


class QuartChoix(Enum):
    NUIT = 1
    JOUR = 2
    SOIR = 3

    @property
    def model(self):
        """
        Retourne l'instance du modèle Quart de la base de données
        qui correspond à l'enum courant.
        """
        return Quart.objects.get(periode=self.value)

    def heure_debut(self):
        if self.value == 1:
            return 0
        elif self.value == 2:
            return 8
        return 16

    def heure_fin(self):
        return (self.heure_debut() + 8) % 24


class TypeEmploye(Enum):
    TP = "Temps plein"
    TPO = "Temps partiel occasionnel"
    TPR = "Temps partiel régulier"


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    USER_TYPES = (
        (0, "no_role"),
        (1, "admin"),
        (2, "gestionnaire"),
        (3, "employe"),
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPES, default=0)


class Profession(TimeStampedModel):
    nom = models.CharField(max_length=55, unique=True, null=False)

    @property
    def activites(self):
        return self.activite_set.all()

    @property
    def employes(self):
        """
        Retourne la liste d'employés qui ont comme profession l'instance courante.
        La liste est trié par ordre d'ancienneté.
        """
        return self.employe_set.order_by('-date_debut')

    def __str__(self):
        return self.nom


class Administrateur(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Activite(TimeStampedModel):
    nom = models.CharField(max_length=50, unique=True, null=False)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom

    def __repr__(self):
        return self.__str__()


class Employe(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_debut = models.DateTimeField(null=False)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)

    type_employe = models.CharField(max_length=55,
                                    null=False,
                                    choices=[(type_employe, type_employe.value) for type_employe in TypeEmploye])

    @property
    def gestionnaires(self):
        """
        Retourne les gestionnaires d'un employé
        """
        return self.profession.gestionnaire_set.all()

    @property
    def matricule(self):
        return self.user.username


class Gestionnaire(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)

    @property
    def matricule(self):
        return self.user.username


class Quart(TimeStampedModel):
    periode = models.SmallIntegerField(
        choices=[(quart.value, quart) for quart in QuartChoix], unique=True)

    @property
    def nom(self):
        return QuartChoix(self.periode).name

    @property
    def enum(self):
        return QuartChoix(self.periode)

    def __str__(self):
        return self.nom


class Horaire(TimeStampedModel):
    date_debut = models.DateTimeField(null=False)
    date_fin = models.DateTimeField(null=False)
    profession = models.ForeignKey(Profession, on_delete=models.CASCADE)

    def jours(self, date=None):
        """
        Retourne tous les cellules de l'horaire courant. Si une date est
        passé en paramètre, seulement les cellules dont la date est plus tard ou
        égale à celle en paramètre seront retournés.
        """
        if not date:
            return self.jour_set.all()
        date2 = dateutils.normalize(date)
        js = self.jour_set.filter(date__gte=date2)
        return js

    class Meta:
        # Selon la profession, un horaire doit être unique avec la date de départ.
        unique_together = (('date_debut', 'profession'),)


class Jour(TimeStampedModel):
    horaire = models.ForeignKey(Horaire, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False)
    employes = models.ManyToManyField(Employe, through='Assignation')
    activites = models.ManyToManyField(Activite, through='Assignation')

    @property
    def disponibilites(self):
        """
        Correspond à toutes les disponibilités qui ont été
        envoyé pour la jour courante.
        """
        return Disponibilite.objects.filter(jour=self)


class CentreActivite(TimeStampedModel):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    horaire = models.ForeignKey(Horaire, on_delete=models.CASCADE)
    activites = models.ManyToManyField(Activite)

    class Meta:
        unique_together = (('employe', 'horaire'))


class Assignation(TimeStampedModel):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE)
    jour = models.ForeignKey(Jour, on_delete=models.CASCADE)
    quart = models.ForeignKey(Quart, on_delete=models.CASCADE)


class Disponibilite(TimeStampedModel):
    jour = models.ForeignKey(Jour, on_delete=models.CASCADE)
    quart = models.ForeignKey(Quart, on_delete=models.CASCADE)
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)

    class Meta:
        # Selon la profession, un horaire doit être unique avec la date de départ.
        unique_together = (('quart', 'jour', 'employe'),)


class Conge(TimeStampedModel):
    jour = models.ForeignKey(Jour, on_delete=models.CASCADE)
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    quarts = models.ManyToManyField(Quart)
    motif = models.CharField(max_length=55, choices=[(
        motif.value, motif) for motif in MotifConge])
    raison = models.CharField(max_length=55, null=True)
    status = models.SmallIntegerField(choices=[(
        status.value, status) for status in StatusConge], default=StatusConge.EN_ATTENTE.value)
