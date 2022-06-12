import re

s = '[0-9]+[.][0-9]+'

fname = 'query-one-s-hobbies.svg'

with open(fname) as f:
  t = f.read()

number_map = {s : s[:s.find('.')+1+4] for s in set( re.findall(s, t) ) if len(s[s.find('.')+1:]) > 4}

for org in number_map.keys():
    t = t.replace(org, number_map[org])

with open(fname[:fname.find('.svg')] + '-1.svg', 'x') as f:
    f.write(t)
