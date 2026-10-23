"""Construit l'app à partir des sources.  Usage :  python3 src/build.py   (depuis la racine du dépôt)
Entrées (src/) : template.html, data.json, tt.json, osrm_ids.json, osrm_matrix.txt
Photos : photos.json (racine) — clés "photos/<id>.jpg" -> data URI
Sortie : index.html (racine)
"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = lambda f: os.path.join(ROOT, 'src', f)
D = json.load(open(S('data.json'), encoding='utf-8'))
tpl = open(S('template.html'), encoding='utf-8').read()
d = json.dumps(D, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
tt = open(S('tt.json'), encoding='utf-8').read()
ids = json.load(open(S('osrm_ids.json'))); N = len(ids['A'])
rows = open(S('osrm_matrix.txt'), encoding='utf-8').read().split('\n')
col = {a: i for i, a in enumerate(ids['A'])}
mx = {'o': ids['O'], 'a': [x['id'] for x in D],
      'd': [''.join(r[col[x['id']]] if x['id'] in col else '!' for x in D) for r in rows],
      'k': [''.join(r[N + 1 + col[x['id']]] if x['id'] in col else '!' for x in D) for r in rows]}
mxs = json.dumps(mx, separators=(',', ':')).replace('</', '<\\/')
# Cartes « Ce week-end » (recherche du jeudi) : vérifiées avant publication
WKF = S('weekend.json')
WK = json.load(open(WKF, encoding='utf-8')) if os.path.exists(WKF) else {'items': []}
TYPES = {'chateaux', 'sentiers', 'animaux', 'musees', 'jeux', 'eau', 'nature', 'trains', 'spectacles', 'pluie', 'fetes'}
seen = {x["id"] for x in D}
for x in WK.get('items', []):
    miss = [k for k in ('id', 'type', 'town', 'canton', 'lat', 'lon', 'start', 'end', 'age_min', 'age_max', 'site')
            + tuple(f + '_' + l for f in ('name', 'desc', 'price', 'when', 'why') for l in ('fr', 'de', 'es')) if x.get(k) in (None, '')]
    assert not miss, f"weekend.json {x.get('id')}: champs manquants {miss}"
    assert x['id'].startswith('wk-') and x["id"] not in seen, f"weekend.json: id invalide ou en double {x['id']}"
    seen.add(x["id"])
    assert x['type'] in TYPES, f"weekend.json {x['id']}: type inconnu {x['type']}"
    assert re.fullmatch(r'\d{4}-\d\d-\d\d', x['start']) and re.fullmatch(r'\d{4}-\d\d-\d\d', x['end']) and x['start'] <= x['end'], f"weekend.json {x['id']}: dates"
    assert 45.8 < x['lat'] < 47.9 and 5.9 < x['lon'] < 10.6, f"weekend.json {x['id']}: coordonnées hors de Suisse"
    assert x['site'].startswith('https://'), f"weekend.json {x['id']}: site"
    x['wk'] = True
wks = json.dumps(WK, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
html = tpl.replace('__DATA__', d).replace('__TT__', tt).replace('__MX__', mxs).replace('__PH__', '{}').replace('__WK__', wks)
html = html.replace('!/claude/.test(location.host)', '!/claude\\.ai|claudeusercontent/.test(location.host)')
out = ('<!doctype html>\n<html lang="fr"><head><meta charset="utf-8"><script>window.__noPhotos=true</script>'
       '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
       + html.replace('<style>', '</head><body>\n<style>', 1) + '\n</body></html>')
# Version : si le contenu change, on incrémente le cache de sw.js et on date la version
import datetime, zoneinfo
OUT, SW = os.path.join(ROOT, 'index.html'), os.path.join(ROOT, 'sw.js')
VRE = re.compile(r'<p class="ver">.*?</p>')
sw = open(SW, encoding='utf-8').read()
num = int(re.search(r'const C="onsortou-v(\d+)"', sw).group(1))
old = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else ''
oldver = VRE.search(old)
if oldver and VRE.sub('', old) == VRE.sub('', out):
    ver = oldver.group(0)                       # rien n'a changé : on garde la version
else:
    num += 1
    open(SW, 'w', encoding='utf-8').write(re.sub(r'onsortou-v\d+', f'onsortou-v{num}', sw, count=1))
    now = datetime.datetime.now(zoneinfo.ZoneInfo('Europe/Zurich')).strftime('%d.%m.%Y · %H:%M')
    ver = f'<p class="ver">Version {num} · {now}</p>'
out = out.replace('<p class="ver">__VER__</p>', ver)
open(OUT, 'w', encoding='utf-8').write(out)
print('version', num)
print('index.html ok —', len(D), 'activités,', len(WK.get('items', [])), 'cartes week-end')
