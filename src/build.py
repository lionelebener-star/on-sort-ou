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
html = tpl.replace('__DATA__', d).replace('__TT__', tt).replace('__MX__', mxs).replace('__PH__', '{}')
html = html.replace('!/claude/.test(location.host)', '!/claude\\.ai|claudeusercontent/.test(location.host)')
out = ('<!doctype html>\n<html lang="fr"><head><meta charset="utf-8"><script>window.__noPhotos=true</script>'
       '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
       + html.replace('<style>', '</head><body>\n<style>', 1) + '\n</body></html>')
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)
print('index.html ok —', len(D), 'activités')
