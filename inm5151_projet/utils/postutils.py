



def body_to_dict(bytez,encoding='utf-8'):
  s = bytez.decode(encoding).split('&')
  return {k:v for (k,v) in [(a,b) for (a,b) in (couple.split('=') for couple in s)]}