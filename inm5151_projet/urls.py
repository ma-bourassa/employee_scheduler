"""inm5151_projet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import logging
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.http import HttpResponseNotAllowed
from .views import index, horaire_controller, disponibilite_controller, conge_controller

admin.site.site_header = 'CISSS Montérégie-Centre - Administrateur'
logger = logging.getLogger(__name__)


def method_dispatch(**table):
    """
    Permet d'associer plusieurs méthodes à une même vue selon
    le verbe http reçu dans une requête.
    """
    # Code taken from: https://stackoverflow.com/a/20898410
    def invalid_method(request, *args, **kwargs):
        logger.warning('Method Not Allowed (%s): %s', request.method, request.path,
                       extra={
                           'status_code': 405,
                           'request': request
                       }
                       )
        return HttpResponseNotAllowed(table.keys())

    def d(request, *args, **kwargs):
        handler = table.get(request.method, invalid_method)
        return handler(request, *args, **kwargs)

    return d


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index.home, name='home'),
    path('horaires/<int:horaire_id>',
         method_dispatch(PUT=horaire_controller.assigner_employe)),
    path('horaires/<int:horaire_id>/<int:employe_id>/<int:jour_id>',
         method_dispatch(DELETE=horaire_controller.retirer_employe)),
    path('horaires/horaire_employe.html',
         horaire_controller.horaire_employe, name='horaire_employe'),
    path('horaires/horaire_general.html',
         horaire_controller.horaire_general, name='horaire_general'),
    path('horaires/planification.html',
         horaire_controller.planification_horaire, name='planification'),
    path('disponibilites/formulaire_disponibilite.html',
         disponibilite_controller.get_formulaire_disponibilite, name='disponibilite'),
    path('disponibilites/', method_dispatch(GET=disponibilite_controller.get,
                                            POST=disponibilite_controller.traiter_formulaire_dispo)),
    path('disponibilites/employe/',
         disponibilite_controller.get_disponibilite_employe),
    path('conges/employe/', conge_controller.demande_conge, name='conge'),
    path('conges/nouvelle_demande/',
         method_dispatch(POST=conge_controller.traiter_formulaire_conge)),
    path('conges/', conge_controller.demandes_conge, name='demandes_conge'),
    path('conges/approuver/', method_dispatch(POST=conge_controller.approuver_conge)),
    path('conges/refuser/', method_dispatch(POST=conge_controller.refuser_conge)),
    path('profil/', index.profil, name='profil'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html',
                                                redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
]
