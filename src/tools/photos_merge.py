"""Ajoute src/tools/out/new_photos.json ({id: dataURL}) à photos.json (racine) et met à jour data.json.
Crédits : src/tools/out/new_credits.json ({id: {"author":..,"license":..,"page":..}}) — obligatoires (licences CC)."""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(H); ROOT = os.path.dirname(SRC)
new = json.load(open(os.path.join(H, 'out', 'new_photos.json')))
cr = json.load(open(os.path.join(H, 'out', 'new_credits.json')))
P = json.load(open(os.path.join(ROOT, 'photos.json')))
D = json.load(open(os.path.join(SRC, 'data.json'), encoding='utf-8'))
for x in D:
    if x['id'] in new:
        k = 'photos/' + x['id'] + '.jpg'; P[k] = new[x['id']]; c = cr[x['id']]
        x['photo'] = k; x['credit'] = f"{c['author'][:40]} · {c['license']}"; x['credit_url'] = c['page']
json.dump(P, open(os.path.join(ROOT, 'photos.json'), 'w'), separators=(',', ':'))
json.dump(D, open(os.path.join(SRC, 'data.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('photos ajoutées :', len(new))
