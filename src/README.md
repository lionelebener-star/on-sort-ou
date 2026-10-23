# On sort où ?! — documentation complète (src/)

Idées de sorties en famille en Suisse, triées par temps de route depuis un point de départ.
Production : **https://go.vamox.ch** (secours : https://on-sort-ou.vercel.app)
Dépôt : `lionelebener-star/on-sort-ou` (branche `main`) → déployé automatiquement par Vercel à chaque commit.

Ce document résume tout ce qui a été construit dans la première session Claude (Cowork, sept.–oct. 2026), ce qui est prévu et les problèmes connus. **Le dépôt est désormais la seule source de vérité** : l'espace de travail de la session d'origine était éphémère.

---

## 1. Structure du dépôt

```
/                      ← servi tel quel par Vercel (site statique, pas de build Vercel)
  index.html           ← GÉNÉRÉ par src/build.py — ne pas éditer à la main
  photos.json          ← toutes les photos (data URI JPEG 480×270), ~6.9 Mo, chargé en différé
  sw.js                ← service worker (cache hors-ligne, push)
  manifest.webmanifest, icon-192.png, icon-512.png
  vercel.json          ← cleanUrls, no-cache pour sw.js, content-type du manifest
  README.md            ← guide court d'installation
/src
  template.html        ← L'APPLICATION (HTML+CSS+JS, un seul fichier) avec 4 marqueurs
  data.json            ← 305 activités (FR/DE/ES)
  towns.txt            ← 186 villes de départ (id|fr|de|canton|lat|lon)
  osrm_ids.json        ← ordre des lignes/colonnes de la matrice ({O:[origines], A:[activités]})
  osrm_matrix.txt      ← temps + distances mesurés (193 départs × 305 activités)
  tt.json              ← ancien tableau de temps des châteaux (plus utilisé, voir §9)
  build.py             ← assemble index.html
  tools/               ← scripts pour recalculer les temps de route et chercher des photos
```

## 2. Build et déploiement

```bash
python3 src/build.py      # depuis la racine ; écrit index.html
```

`build.py` remplace dans `template.html` :

| Marqueur | Contenu |
|---|---|
| `__DATA__` | `data.json` minifié |
| `__TT__` | `tt.json` |
| `__MX__` | matrice OSRM (`{O, A, d:[lignes durées], k:[lignes distances]}`) |
| `__PH__` | `{}` — les photos ne sont pas inlinées ; `window.__noPhotos=true` fait charger `photos.json` en différé |

**Version automatique** : si `index.html` change, `build.py` incrémente lui-même le cache de `sw.js` (`onsortou-vN`) et affiche « Version N · date · heure » (heure de Zurich) en bas de l'app (`<p class="ver">`). Rebuild sans changement = même version. Ne plus incrémenter `sw.js` à la main.

Le garde du service worker dans index.html doit rester : `!/claude\.ai|claudeusercontent/.test(location.host)` (pas de SW dans l'aperçu artefact Claude).

Avant de pousser : ouvrir index.html localement (ex. `python3 -m http.server`) et vérifier la console (aucune erreur), la vue liste, le radar, une fiche, le changement de langue et de départ.

### Infrastructure

| Élément | Détail |
|---|---|
| Hébergement | Vercel, projet `on-sort-ou`, framework « Other », pas de commande de build, racine `/` |
| Domaine | `go.vamox.ch` — CNAME chez Infomaniak (zone vamox.ch) → `8f5aaed05373719a.vercel-dns-017.com` (l'ancien `cname.vercel-dns.com` marche aussi). SSL Vercel OK. |
| Avis (feedback) | Google Apps Script lié à un Google Sheet, onglet « Avis ». URL dans `CFG.feedbackUrl` du template : `https://script.google.com/macros/s/AKfycbw05XYNKwTrY8SXvkoVkciOF7bHFjQyUxH92H35Hs3YzzFLgfhsbVpm3_bhkxaPdJaSAw/exec` |
| Version artefact | Une copie « artefact Claude » existe (photos en data URI, avis via la base de l'artefact). Elle n'est plus maintenue ; la PWA est la référence. |

Script Apps Script déployé (Application Web, exécuter en tant que moi, accès : tout le monde) :

```js
const SHEET='Avis';const COLS=['Reçu le','Catégorie','Message','E-mail','Langue','Départ','Âges','Type','Appareil'];
function doPost(e){const ss=SpreadsheetApp.getActiveSpreadsheet();const sh=ss.getSheetByName(SHEET)||ss.insertSheet(SHEET);
 if(sh.getLastRow()===0)sh.appendRow(COLS);let d={};try{d=JSON.parse(e.postData.contents||'{}')}catch(err){d={text:String(e.postData&&e.postData.contents||'')}}
 const clip=(v,n)=>String(v==null?'':v).slice(0,n);
 sh.appendRow([new Date(),clip(d.cat,40),clip(d.text,2000),clip(d.email,120),clip(d.lang,4),clip(d.origin,40),clip(d.ages,10),clip(d.type,20),clip(d.ua,120)]);
 return ContentService.createTextOutput('ok')}
function testAvis(){doPost({postData:{contents:JSON.stringify({cat:'Test',text:'Message de test',lang:'fr'})}})}
```

L'app envoie `fetch(url,{method:"POST",mode:"no-cors",headers:{"Content-Type":"text/plain"},body:JSON.stringify({...})})` — pas de réponse lisible (no-cors), donc pas de confirmation réelle côté app.

## 3. Fonctionnalités en place

- **Langues** FR / DE / ES (onboarding + sélecteur « 🌍 Langue · Sprache · Idioma »). Textes UI dans `T.fr/T.de/T.es`, types d'activité via `typeName()`, noms de départs via `oname()` (`OES` pour ES). Fallback FR partout : `t()`, `nm()`, `tx()`.
- **Enfants** : on ajoute ses enfants (prénom + âge, emoji) et on choisit pour qui on cherche (`KIDS`, `SELK`, `kidsFor`, `drawKids`, `applyKids`, `addKid`). Filtre par `age_min/age_max`.
- **Point de départ** : 7 départs de base (ruti, solothurn, biel, bern, schoenbuehl, zurich, sion) + 186 villes, champ de recherche (FR/DE), **géolocalisation** (ville la plus proche `nearestTown` + calcul OSRM en direct pour la position exacte, mis en cache localStorage, fallback modèle).
- **Temps de route mesurés** pour toutes les paires départ×activité (OSRM), affichés `🚗 1 h 05 · 72 km`.
- **Filtres** : type (11 catégories : musees, nature, animaux, chateaux, trains, eau, sentiers, fetes, jeux, pluie, spectacles), saison, intérieur/extérieur, temps max, « hot » (tops du week-end), recherche texte (inclut `name_es`).
- **Événements** datés (`start`/`end`) masqués automatiquement après la date (`evLive`).
- **Vue radar** : disque centré sur le départ, distance = temps de route. Cadran en 4 quadrants : **haut = extérieur, bas = intérieur, gauche = culturel, droite = sportif** (`qAngle`, `CS`). Tap → zoom dans la zone (`applyZoom`, `radarTap`, `ZM`), tap sur un point → fiche.
- **Mise en page responsive** : container queries sur `#main` → 1 carte par ligne sur téléphone / fold fermé, 2–3 sur tablette / fold ouvert.
- **Photos** : 197 activités ont une vraie photo (12 châteaux + 185 Wikimedia Commons, crédits + licence affichés sur la fiche). Les 108 autres ont une **illustration** : emoji par règles (`emo()`, `EMO_RULES`), dispersion (`scatter()`, ex. `FARMPUMP` pour les fêtes de la courge), ou SVG dessiné (`SVGILL`/`svgIll()` : ferme avec courges très simplifiée, train avec courges très illustré).
- **12 animations** (toutes gardées à la demande de Lionel ; respectent `prefers-reduced-motion` via `RM`) : fiche qui « vibre » à l'ouverture puis rétrécit vers son origine à la fermeture, cascade des cartes, entrée du radar, tampon, avion en papier (envoi avis), chute d'épingle, compteur roulant, titre animé (`drawTitle`/`titleJump`), choix enfant (`kidSet`), `hop`, etc. Fonction utilitaire `A()`. L'ouverture de fiche est détectée par un `MutationObserver` filtré sur `.scrim`.
- **Bouton « 📲 Installer l'app »** (`#instBtn`) : Android/Chrome → `beforeinstallprompt` (`DPROMPT`, `doInstall`) ; iOS → feuille d'instructions « Partager → Sur l'écran d'accueil » (`#instSheet`, `showInst`).
- **Favoris** : étoile ☆/★ sur chaque carte (`data-f`, `FAV` en localStorage `vx-fav`). Bouton discret « ★ N » en haut (`#favBtn`, visible dès 1 favori) → mode `S.fav` : seuls les favoris, liste et radar, « ✕ Fermer » (`#favOff`). Choisir un type quitte le mode.
- **Cartes qui se retournent** (liste) : tap sur la carte → `flipCard()` (rotation 3D + hauteur animée). Recto : photo, titre, description courte. Verso : description complète, points forts, lieu, trajet, âge, dedans/dehors, durée, prix, horaires, liens. La fiche du radar (`card(x,1)`) montre tout sans retournement.
- **« 📅 Ce week-end » (perso, Lionel seulement)** : cartes de la recherche du jeudi dans `src/weekend.json` (`weekend`, `weather.{sat,sun,note}_xx`, `items[]` au format de data.json + `wk`, `tip`, `why_xx`, `check_xx`, `sources[]`, ids `wk-…`). `build.py` vérifie le fichier (champs FR/DE/ES, dates, coordonnées, type) et l'injecte (`__WK__`). Dans l'app, elles ne sont ajoutées à `DATA` que si `vx-me` est activé : **5 touchers en 3 s sur la ligne « Version … »** en bas (refaire pour désactiver). Le filtre montre la météo, le Top-Tipp, les cartes du jeudi, puis les événements de data.json qui ont lieu ce week-end (≤ 70 min). Les cartes disparaissent seules après leur date `end`. Temps de route : estimation (pas dans la matrice OSRM).
- **Avis** : bouton « Ton avis » → catégorie, message, e-mail optionnel, + contexte (langue, départ, âges, type, appareil) → Google Sheet.
- **Hors-ligne** : service worker (réseau d'abord, cache en secours) ; handler `push` déjà présent pour la phase 2.

## 4. Architecture du template (repères)

Tout est dans `src/template.html` (pas de framework, pas de dépendances externes).

- État global `S` (lang, origine, enfants, filtres, vue) persisté en localStorage (try/catch).
- `ORIS` : départs ; `BIG` : grandes villes prioritaires dans la liste ; `GEO` : position courante.
- Temps de route :

```js
function route(x){const o=ori();
  if(o.geo&&LIVE[x.id])return LIVE[x.id];                  // géoloc : calcul OSRM en direct
  const oi=MXO[o.id],j=MXI[x.id];
  if(oi!=null&&j!=null){const a=MXJ.d[oi][j],b=MXJ.k[oi][j];
    if(a!=="!"&&b!=="!")return [Math.max(5,MXA.indexOf(a)*5),MXA.indexOf(b)*5]}  // matrice mesurée
  return [modelMins(x,o),Math.round(1.3*hav(o.lat,o.lon,x.lat,x.lon))]}         // estimation de secours
function mins(x){const r=route(x);x._k=r[1];return r[0]}
```

- `liveTimes()` : pour une position GPS, appelle `router.project-osrm.org/table` (1 source × ≤ 100 destinations par requête), cache localStorage.
- `CFG={sheetCsv:"", feedbackUrl:"…"}` — `sheetCsv` prévu pour gérer les activités depuis un Google Sheet publié en CSV (colonne `hidden` = booléen pour masquer).

## 5. Schéma de `data.json`

Tableau d'objets :

| Champ | Description |
|---|---|
| `id` | identifiant unique (slug) — clé de la matrice et des photos |
| `type` | une des 11 catégories |
| `name_fr/_de/_es`, `desc_*`, `price_*`, `season_*`, `when_*`, `duration_*`, `kids_*` | textes traduits |
| `town`, `canton`, `lat`, `lon` | lieu |
| `age_min`, `age_max` | âges conseillés |
| `seasons` | liste (`printemps`, `ete`, `automne`, `hiver`) |
| `indoor` | booléen (sert au radar et au filtre pluie) |
| `site`, `src` | site officiel, source de l'info |
| `hot` | mis en avant « tops du week-end » |
| `photo`, `credit`, `credit_url` | `photos/<id>.jpg` (clé dans photos.json), auteur · licence, page Commons |
| `start`, `end` | événements uniquement (ISO) |

**Ajouter une activité** : l'ajouter dans `data.json` (3 langues) → recalculer la matrice (§6) sinon elle utilise l'estimation de secours → éventuellement photo (§7) → `build.py`.

## 6. Temps de route — pipeline OSRM

Serveur public de démo OSRM (`router.project-osrm.org`, API `table`). Le bac à sable cloud de Claude et la VM de l'ordinateur étaient bloqués (403) ; le calcul a été fait **dans un navigateur** (navigateur intégré de Claude desktop), sur l'origine `router.project-osrm.org` pour éviter le CORS.

Format de `osrm_matrix.txt` : une ligne par départ (ordre `osrm_ids.json.O`), chaque ligne = `<305 car. durées>|<305 car. distances>` (611 car.). Un caractère par paire, alphabet `ALPH` = caractères ASCII 35–126 sans `\`. Durée = index × 5 min, distance = index × 5 km, `!` = pas de route. **Découper par position, pas par `|`** (le `|` fait partie de l'alphabet).

Étapes :

1. `python3 src/tools/osrm_make_job.py` → `src/tools/out/osrm_job.js` + `out/osrm_ids.json` (départs = ceux du template + towns.txt ; activités = data.json).
2. Ouvrir dans un navigateur : `https://router.project-osrm.org/table/v1/driving/7.418,47.153;8.5417,47.3769?sources=0`
3. Coller `osrm_job.js` dans la console (boucle de `osrm_browser_loop.js` : blocs de 10 départs × 90 destinations, 1 requête/s, 4 essais). Attendre `P.done===P.total` (~2–3 min ; `P.err` doit être vide).
4. `ENC(0,OS.length)` → copier le texte dans `src/tools/out/osrm_enc.txt` (si trop long pour le presse-papier, faire par tranches `ENC(0,50)`, `ENC(50,100)`… et concaténer avec des sauts de ligne).
5. `python3 src/tools/osrm_decode.py` → écrit `src/osrm_matrix.txt` et `src/osrm_ids.json` (vérifie les tailles).
6. `python3 src/build.py`.

## 7. Photos — pipeline Wikimedia

Règles : uniquement Wikimedia Commons / Wikipedia (licences libres), **crédit auteur + licence + lien obligatoires**, et **revue visuelle de chaque photo** (beaucoup de faux positifs : ex. une crèche d'Avellino pour Lugano, un labyrinthe néerlandais, un ara générique, un ferry solaire — tous rejetés).

1. `src/tools/photos_search.js` (console sur `https://commons.wikimedia.org/wiki/Special:BlankPage`, avec `window.L` défini) : pour chaque activité sans photo, cherche la `pageimage` Wikipedia (articles à ≤ 3 km), sinon géorecherche Commons (≤ 500 m) → `window.PHR`. ~45 % des choix automatiques étaient faux.
   Revue : afficher les miniatures en planche-contact (grille 5 colonnes × 110 px, nom de l'activité sous chaque image) et capturer l'écran ; recharger `Special:BlankPage` avant chaque planche (sinon captures périmées). Pour les rejets : recherche texte Commons (`list=search&srnamespace=6`, nom + ville), 2 candidats chacun, nouvelle revue.
2. Garder la liste validée `PF = [[id, "File:…"], …]`.
3. `src/tools/photos_download.js` : télécharge via `Special:FilePath/<fichier>?width=640`, recadre sur canvas en **480×270 JPEG q=0.62** → `IMS={id:dataURL}`. Exporter par lots ≤ 235 000 caractères (limite des résultats d'outil ~262 K) vers `src/tools/out/new_photos.json` ; crédits (auteur, licence, page) depuis l'API `imageinfo&iiprop=extmetadata` vers `out/new_credits.json`.
4. `python3 src/tools/photos_merge.py` → ajoute à `photos.json` (racine) et renseigne `photo/credit/credit_url` dans `data.json`.
5. `python3 src/build.py`.

## 8. Choix et préférences de Lionel (à respecter)

- Interface et communication en français ; app trilingue FR/DE/ES.
- **Aucune adresse privée dans le contenu public** : le départ « Rüti » utilise seulement `3295 Rüti bei Büren` (corrigé ; voir §9).
- Temps **mesurés**, pas estimés, pour tout.
- Garder les 12 animations ; illustrations claires et parlantes (fête de la courge → beaucoup de courges ; ferme avec courges très simplifiée ; train avec courges très illustré).
- Les cartes doivent bien utiliser l'écran du Galaxy Fold (ouvert : 2–3 colonnes ; fermé : 1).
- Pas de Supabase / backend lourd : tout statique + Google Sheet.
- Les retours de Lionel arrivent souvent sous forme de commentaires sur la page ou de captures d'écran.

## 9. Problèmes connus

- **Adresse privée encore en ligne** tant que le nouvel index.html (sans « Mühlematt ») n'est pas poussé. Vérifier : `grep -c Mühlematt index.html` doit donner 0.
- **Accès mobile** : « die Website ist nicht erreichbar » sur le téléphone de Lionel juste après la création du DNS (propagation/cache probable) — pas encore confirmé résolu. Fallback : on-sort-ou.vercel.app.
- **Avis** : test de bout en bout depuis go.vamox.ch pas encore confirmé ; en no-cors l'app ne peut pas savoir si l'envoi a réussi.
- **Temps OSRM** : ~9 % plus lents que Google en médiane (ratio 1.09 vs temps de référence des châteaux), sans trafic ; détours réels vers certaines destinations de montagne. Serveur de démo : politique d'usage, pas de SLA — si la géoloc en direct tombe, l'app passe à l'estimation.
- **`photos.json` lourd** (6.9 Mo) : chargé en différé mais pèse sur le premier chargement mobile. Piste : un fichier par photo (`/photos/<id>.jpg`) une fois qu'on pousse par git (la limite de 100 fichiers concernait seulement l'upload web GitHub).
- **108 activités sans photo** (illustration à la place).
- **Données vague 2** (≈ 49 activités ajoutées en fin de recherche) : coordonnées approximatives ; prix non vérifiés pour Kronberg, Lintharena, MoMö, Saint-Nicolas Jurassica ; horaires de la Märlistadt non confirmés.
- **Événements** : expirent automatiquement, mais il faut en ajouter de nouveaux régulièrement.
- **`tt.json` / table `TT`** : encore embarquée mais inutilisée (la matrice a priorité) — peut être supprimée.
- Les aperçus Vercel affichent des disques gris (emoji non rendus par le moteur de capture) — pas un bug réel.
- Version artefact vs PWA : l'artefact a ses photos inlinées et les avis dans sa base ; non synchronisé.

## 10. Prévu / idées

1. Notifications du jeudi (« tops du week-end ») — handler `push` déjà dans sw.js ; il manque l'abonnement et un émetteur (ex. Vercel cron + web-push, clés VAPID).
2. Gestion des activités depuis un Google Sheet publié en CSV (`CFG.sheetCsv`, colonne `hidden`).
3. Photos pour les 108 activités restantes (§7).
4. Mise à jour régulière des événements ; vérifier les données vague 2.
5. Découper photos.json en fichiers séparés.
6. Éventuellement versions App Store / Play Store (TWA/Capacitor).

## 11. Pour Claude Code (nouvelle session)

- Lire ce fichier d'abord. Modifier **`src/template.html`** / **`src/data.json`**, jamais `index.html` directement, puis `python3 src/build.py`, tester, committer index.html + src + sw.js ensemble.
- Messages de commit en français, courts.
- Ne jamais réintroduire d'adresse privée ; ne pas saisir de mots de passe/identifiants (Lionel s'occupe des connexions).
