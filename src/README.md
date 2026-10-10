# Sources de « On sort où ?! »

- `data.json` : les activités (FR/DE/ES, prix, horaires, photos, coordonnées)
- `template.html` : l'app (HTML/CSS/JS) avec les emplacements `__DATA__`, `__MX__`…
- `osrm_matrix.txt` + `osrm_ids.json` : temps et distances calculés (OSRM) depuis 193 lieux de départ
- `towns.txt` : liste des villes de départ
- `build.py` : `python3 src/build.py` régénère `index.html` à la racine

Pour publier : modifier les sources, lancer le build, commit → Vercel met en ligne automatiquement.
