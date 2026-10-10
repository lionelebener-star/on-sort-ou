"""Écrit src/osrm_matrix.txt et src/osrm_ids.json à partir de src/tools/out/osrm_enc.txt (sortie de ENC)."""
import json, os, shutil
H = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.dirname(H)
rows = open(os.path.join(H, 'out', 'osrm_enc.txt'), encoding='utf-8').read().strip().split('\n')
ids = json.load(open(os.path.join(H, 'out', 'osrm_ids.json')))
assert len(rows) == len(ids['O']) and all(len(r) == 2 * len(ids['A']) + 1 for r in rows), 'taille inattendue'
open(os.path.join(SRC, 'osrm_matrix.txt'), 'w', encoding='utf-8').write('\n'.join(rows))
shutil.copy(os.path.join(H, 'out', 'osrm_ids.json'), os.path.join(SRC, 'osrm_ids.json'))
print('ok', len(rows), 'x', len(ids['A']))
