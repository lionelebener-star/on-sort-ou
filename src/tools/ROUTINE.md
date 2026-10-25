# Routine du jeudi — « Wochenend-Abenteuer »

Consignes pour la session Claude lancée automatiquement **chaque jeudi vers 19:00 (Europe/Zurich)**.
Tu travailles **seul** : personne ne répond aux questions. Fais le travail, publie, puis termine par un court rapport.

Dépôt : `lionelebener-star/on-sort-ou`, branche **`main`** (publication directe, Vercel met en ligne).
Lis d'abord `src/README.md` (structure, build, schéma de `data.json`).

## 0. Préparation

1. Attacher le dépôt avec l'outil `mcp__claude-code-remote__add_repo` (`owner: lionelebener-star`, `repo: on-sort-ou`, `access: push`), puis le cloner avec la commande renvoyée, ou faire `git pull origin main` s'il est déjà là. **Sans cette étape, le push est refusé (403).**
2. Calculer en heure de Zurich : `aujourdhui`, le **samedi qui suit** et le dimanche.
3. Vérifier l'accès web avec l'outil **`WebFetch`** (pas `curl`) sur un site officiel, par ex. `https://www.nmbe.ch/de/kalender`. Utiliser ensuite `WebFetch` pour lire les pages officielles des musées et organisateurs.
   - Si les sites officiels sont inaccessibles, continuer avec la recherche web seule, être plus prudent (mettre plus de choses dans `check_*`) et le signaler dans le rapport.

## Règles communes (toutes les cartes)

- **Grands musées et programme culturel du moment d'abord** : ateliers familles, expositions temporaires, visites familles, journées spéciales. Puis ce qui est lié à la région et à la saison (fêtes, marchés, Saint-Nicolas, Noël, carnaval…). Puis les activités sympas pour les familles.
- **Actualité > offres permanentes.**
- **Ne jamais inventer** une date, un horaire, un prix ou un âge. Ce qui n'est pas confirmé va dans `check_xx` (week-end) ou n'est pas publié.
- Ne pas confondre la date de publication d'une page avec la date de l'événement. Rejeter les pages d'une saison précédente.
- Sources par ordre de confiance : site officiel de l'organisateur ou du musée > commune, canton ou tourisme > agenda régional sérieux > média local > agrégateur.
- Textes en **FR, DE et ES** (naturels, courts, ton chaleureux et concret pour des parents).
- Âge réaliste : une activité « famille » n'est pas forcément adaptée à 3 ans.
- Aucune adresse privée, aucun nom de personne privée.
- `type` ∈ `chateaux, sentiers, animaux, musees, jeux, eau, nature, trains, spectacles, pluie, fetes`.
- Coordonnées (`lat`, `lon`) : celles du lieu réel (4 décimales).
- `site` : URL **https** officielle de l'événement ou du lieu.

## Partie A — « Ce week-end » (perso de Lionel) → `src/weekend.json`

Pour le **samedi et le dimanche qui suivent**, au départ de **Rüti bei Büren (BE)**, **≤ ~60 min en voiture**, **enfants de 3 à 7 ans**.

À chercher : les grands musées de la région et leur programme du week-end, à vérifier **à chaque fois** :
- **Berne** : Creaviva / Zentrum Paul Klee, Naturhistorisches Museum, Bernisches Historisches Museum, Museum für Kommunikation, Kunstmuseum, ALPS, Tierpark Dählhölzli ;
- **Bienne** : NMB, Pasquart ;
- **Soleure** : Naturmuseum, Kunstmuseum, Enter (Derendingen) ;
- **autour** : Papiliorama (Kerzers).

Puis : théâtre enfants et marionnettes (Berner Puppen Theater, TOBS, Bühnen Bern), fêtes de saison, marchés avec programme enfants, YB (hommes, femmes, juniors ; signaler qu'un match à 20 h 30 est trop tard pour des 3–7 ans), 1–2 idées dehors (forêt, nœuds, camping, feu seulement si autorisé, paddle seulement si les conditions sont sûres).

À vérifier :
- **météo** distincte samedi et dimanche (températures, pluie, vent) ;
- **feu** : interdictions cantonales BE/SO ;
- **eau et vent** si une activité nautique est envisagée ;
- **âge, prix, réservation, horaires** de chaque proposition.

Sélection : **4 à 8 cartes** variées (pas 6 musées pareils, pas tout à Berne), dont **un seul `"tip": true`** (Top-Tipp = âge + actualité + météo + distance + simplicité + originalité).

Format : **remplacer entièrement** `src/weekend.json` (voir l'exemple existant dans le dépôt) :

```json
{
  "weekend": "AAAA-MM-JJ (samedi)",
  "generated": "horodatage ISO",
  "weather": {"sat_fr","sat_de","sat_es","sun_fr","sun_de","sun_es","note_fr","note_de","note_es"},
  "items": [
    {"id": "wk-<slug>-<date>", "wk": true, "tip": false, "type": "...", "hot": false,
     "name_fr/de/es", "town", "canton", "lat", "lon",
     "start": "AAAA-MM-JJ", "end": "AAAA-MM-JJ",
     "when_fr/de/es", "desc_fr/de/es", "kids_fr/de/es": ["emoji + 2-4 mots"],
     "age_min", "age_max", "indoor": true, "seasons": [],
     "price_fr/de/es", "why_fr/de/es", "check_fr/de/es (facultatif)",
     "site": "https://…", "sources": ["https://…"]}
  ]
}
```

- `weather.note_*` : feu, paddle, YB, autres avertissements.
- Les dates `start`/`end` doivent être le samedi et/ou le dimanche du week-end.

## Partie B — Actualisation publique → `src/data.json`

Pour tous les utilisateurs de l'app, dans toute la Suisse, avec la priorité au Mittelland (Berne, Bienne, Soleure, Fribourg, Neuchâtel), puis Bâle, Zurich, Lucerne et Vaud.

1. **Nouveaux événements (10 à 20)** qui commencent dans les **6 prochaines semaines**. Mêmes priorités : grands musées (expositions temporaires, journées familles), spectacles enfants, fêtes de saison.
   - **Éviter les doublons** : chercher avant d'ajouter si le même événement ou le même lieu à la même date existe déjà dans `data.json` (`id`, `name_*`, `town`).
   - Format : même schéma que les événements existants de `data.json`, plus `"added": "<aujourdhui>"`, `"start"`, `"end"`, `"when_fr/de/es"`, `"hot": false`, `"seasons": []`, `"src"` (URL source), **sans** `photo` (l'app dessine une illustration).
   - `id` = slug + année, par ex. `marche-noel-berne-2026`.
   - Ajouter à la fin du tableau.
2. **Vérification par rotation (environ 20)** : prendre les activités **permanentes** (sans `start`) dont `checked` est absent ou le plus ancien. Vérifier sur le site officiel prix, horaires et saison.
   - Corriger les champs `price_*`, `season_*`, `duration_*` si besoin, puis mettre `"checked": "<aujourdhui>"`.
   - Si l'activité a **définitivement fermé** : la supprimer de `data.json` et le dire dans le rapport.
   - En cas de doute : ne rien changer, sauf `checked`.
3. **Ménage** : supprimer de `data.json` les événements dont `end` est passé depuis plus de 30 jours.

Les nouvelles activités n'ont pas de temps de route mesuré : l'app utilise une estimation. C'est accepté. Ne pas toucher à `osrm_matrix.txt`.

## Publication

1. `python3 src/build.py` doit passer. Il vérifie les champs, les dates, les coordonnées, les ids et les URLs, et incrémente lui-même la version et le cache.
   - En cas d'erreur, **corriger les données** puis relancer. Ne jamais contourner les vérifications.
2. Contrôle rapide (Playwright, Chromium dans `/opt/pw-browsers/chromium`) : la page se charge sans erreur JS (une 404 sur l'icône est connue), et « Du moment » affiche des cartes.
3. `git add index.html sw.js src/` puis commit en français, court : « Actualisation du jeudi JJ.MM : N nouveautés, week-end du JJ.MM ». Ensuite `git push origin main`, avec jusqu'à 4 essais (2 s, 4 s, 8 s, 16 s) en cas d'erreur réseau, et `git pull --rebase` si la branche a bougé.
4. Ne jamais pousser un build cassé. Si le build ne peut pas être réparé : ne rien pousser et l'expliquer dans le rapport.

## Rapport final (dernier message de la session)

- Publié ou non, avec le numéro de version (en bas de `index.html`).
- Météo samedi et dimanche en une ligne chacun, Top-Tipp, liste des cartes du week-end.
- Nouveautés publiques ajoutées (nom, ville, date), activités vérifiées, corrigées ou supprimées.
- Limites rencontrées (sites inaccessibles, informations non confirmées).
