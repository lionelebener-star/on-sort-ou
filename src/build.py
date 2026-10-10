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
print('index.html ok —', len(D), 'activités')
