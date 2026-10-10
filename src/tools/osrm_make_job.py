"""Génère le script navigateur qui calcule la matrice temps/distances avec OSRM.
Usage : python3 src/tools/osrm_make_job.py  -> src/tools/out/osrm_job.js
Puis : ouvrir https://router.project-osrm.org/table/v1/driving/7.418,47.153;8.5417,47.3769?sources=0
dans un navigateur (même origine = pas de CORS), coller le contenu de osrm_job.js dans la console,
attendre P.done===P.total (~2-3 min), puis exécuter ENC(0,OS.length) et sauver le texte dans
src/tools/out/osrm_enc.txt, enfin : python3 src/tools/osrm_decode.py
"""
import json, os, re
H = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(H)
tpl = open(os.path.join(SRC, 'template.html'), encoding='utf-8').read()
O = [(i, float(la), float(lo)) for i, la, lo in re.findall(r'\{id:"(\w+)",c:"\w+",fr:"[^"]*",de:"[^"]*",q:"[^"]*",lat:([\d.]+),lon:([\d.]+)', tpl)]
for l in open(os.path.join(SRC, 'towns.txt'), encoding='utf-8'):
    i, fr, de, c, la, lo = l.strip().split('|')
    if i not in [o[0] for o in O]: O.append((i, float(la), float(lo)))
D = json.load(open(os.path.join(SRC, 'data.json'), encoding='utf-8'))
os.makedirs(os.path.join(H, 'out'), exist_ok=True)
json.dump({'O': [o[0] for o in O], 'A': [x['id'] for x in D]}, open(os.path.join(H, 'out', 'osrm_ids.json'), 'w'))
js = "window.OS=%s;window.AC=%s;\n" % (json.dumps([[round(o[2], 4), round(o[1], 4)] for o in O]), json.dumps([[round(x['lon'], 4), round(x['lat'], 4)] for x in D]))
js += open(os.path.join(H, 'osrm_browser_loop.js'), encoding='utf-8').read()
open(os.path.join(H, 'out', 'osrm_job.js'), 'w', encoding='utf-8').write(js)
print(len(O), 'départs x', len(D), 'activités -> out/osrm_job.js')
