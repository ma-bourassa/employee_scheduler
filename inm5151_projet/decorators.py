from .models import Gestionnaire, Employe
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def gestionnaire_required(function):
  """
  Oblige que le request.user soit un gestionnaire.
  préconditions:
    - l'attribut request.user existe et n'est pas nulle.
  """
  def f(request, *args, **kwargs):
    user = request.user
    try:
      request.gestionnaire = Gestionnaire.objects.get(user__id=user.pk)
      return function(request, *args, **kwargs)
    except Gestionnaire.DoesNotExist:
      return HttpResponseForbidden("Vous devez être gestionnaire pour accéder à cette page.")
      
  f.__doc__ = function.__doc__
  f.__name__ = function.__name__
  return login_required(f)

def employe_required(function):
  """
  Oblige que le request.user soit un gestionnaire.
  préconditions:
    - l'attribut request.user existe et n'est pas nulle.
  """
  def f(request, *args, **kwargs):
    user = request.user
    try:
      request.employe = Employe.objects.get(user__id=user.pk)
      return function(request, *args, **kwargs)
    except Employe.DoesNotExist:
      return HttpResponseForbidden("Vous devez être un employé pour accéder à cette page.")
      
  f.__doc__ = function.__doc__
  f.__name__ = function.__name__
  return login_required(f)