from django import template

register = template.Library() 

# code taken from https://stackoverflow.com/a/51090108
@register.filter(name='dict_key')
def dict_key(d, k):
  """
  Retourne la valeur à la clé `k` d'un dictionnaire `d`.
  """
  return d[k]

# code taken from https://stackoverflow.com/a/24402622
@register.filter(name='one_more')
def one_more(_1, _2):
  return _1, _2

@register.filter(name='has_tuple')
def has_tuple(args, t2):
  container, t1 = args
  return (t1,t2) in container