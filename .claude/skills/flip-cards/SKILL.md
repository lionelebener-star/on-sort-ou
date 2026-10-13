---
name: flip-cards
description: Cartes interactives en HTML/CSS/JS sans framework, comme dans l'app « On sort où ?! » (go.vamox.ch). Chaque carte se retourne en 3D au toucher pour montrer les détails au verso. Une étoile ☆/★ ajoute la carte aux favoris (mémorisés dans le navigateur), un rond ✓ la marque comme « visitée », et un petit bouton « ★ N », visible seulement s'il y a des favoris, affiche uniquement les favoris. Les textes sont en FR/DE/ES, l'app respecte « réduire les animations » et se navigue au clavier. À utiliser quand l'utilisateur veut des cartes qui se retournent, des favoris, une liste de cartes avec recto/verso, une wishlist, ou reproduire « les cartes de On sort où ». Use for flip cards, favourites/bookmarks, star button, card grid with front/back details.
---

# Flip cards + favoris

Recette des cartes de l'app « On sort où ?! ». Elle fonctionne dans n'importe quelle page HTML statique : PWA, artefact Claude, site Vercel. Il n'y a aucune dépendance.

**Implémentation de référence complète, testée :** `assets/flip-cards-demo.html`. Lis-la d'abord, puis copie ou adapte ses blocs (ils sont balisés `/* ===== … ===== */`). Elle s'ouvre telle quelle dans un navigateur.

## Ce que l'utilisateur obtient

1. **Grille de cartes** responsive : 1 colonne sur téléphone (ou Galaxy Fold fermé), 2 sur tablette, 3 sur grand écran. Le nombre de colonnes dépend de la largeur de `#main` (container queries), pas de celle de l'écran.
2. **Recto** : photo (ou emoji sur fond coloré), badge (ex. « 🚗 20 min »), titre, description coupée à 3 lignes, indication « Plus d'infos ↻ ».
3. **Toucher la carte** (ailleurs que sur un bouton ou un lien) : la carte se retourne en 3D (0,6 s) et sa hauteur s'anime vers celle du verso.
4. **Verso** : description complète, étiquettes, tableau de détails (`<dl>`), liens, « ↩ Retour ». Toucher à nouveau ramène le recto.
5. **Étoile ☆ → ★** sur la photo : ajoute ou retire le favori, avec une animation « tampon ». C'est sauvegardé dans `localStorage`.
6. **Rond ✓ « visité »** à côté de l'étoile (facultatif).
7. **Bouton discret « ★ N »** dans la barre du haut : caché tant qu'il n'y a pas de favori. Il bascule en mode « Mes favoris (N) », avec un bouton « ✕ Fermer ». Si on retire une étoile dans ce mode, la carte disparaît de la liste.
8. **Version « fiche »** sans retournement (`card(x,true)`), pour une modale ou une popup. Elle montre tout d'un coup.

## Points techniques importants (pièges déjà rencontrés)

- **Structure** : `article.card.fc` (porte `perspective`) > `.fl` (tourne, `transform-style:preserve-3d`) > `.face.fr` + `.face.bk`. La **bordure et l'ombre (`.b`) vont sur chaque face**, pas sur l'article. Sinon le cadre ne tourne pas avec la carte.
- **Ne pas mettre `overflow:hidden` sur l'article ni sur `.fl`** : ça aplatit la 3D. Le `overflow:hidden` va sur les faces.
- **Hauteur** : la face visible est dans le flux et donne la hauteur, l'autre est en `position:absolute; inset:0`. La classe `.flip` intervertit les deux, et `flipCard()` anime la hauteur de l'ancienne à la nouvelle valeur (WAAPI). Ne pas empiler les deux faces dans la même case de grille : le recto hériterait de la hauteur du verso et aurait un grand vide.
- **Face cachée en `visibility:hidden`** (avec `transition: visibility 0s .3s`, pour qu'elle disparaisse à mi-rotation). Sans ça, les liens du verso restent cliquables à travers le recto, car `backface-visibility` ne bloque pas les clics.
- **Clics** : un seul écouteur sur `document` (délégation). Les `button` sont traités en premier et font `return`. Les liens `a` ne retournent pas la carte. Le reste de la carte retourne la carte. L'étoile et le ✓ ne retournent donc jamais la carte.
- **`arr.map(x=>card(x))`, jamais `arr.map(card)`** : `map` passe l'index comme 2ᵉ argument, et `card(x,1)` deviendrait la version « fiche ».
- **Mettre à jour toutes les étoiles** d'un même id (`querySelectorAll('[data-f="id"]')`), car la même activité peut être affichée à deux endroits (liste et modale).
- **`localStorage` toujours dans un try/catch** (navigation privée, aperçu artefact). Préfixer les clés (`fc-fav`, ou `vx-fav` dans On sort où).
- **Accessibilité** : `tabindex="0"` et `aria-expanded` sur la carte. Entrée ou Espace la retournent. `aria-pressed` sur l'étoile et le ✓. `@media (prefers-reduced-motion:reduce)` supprime la rotation, et `RM` désactive les animations JS.
- **i18n** : tous les textes passent par `t(clé)` avec repli sur FR. Les champs de données suivent la forme `champ_fr/_de/_es`, lus via `tx(x,"champ")`.
- **Échapper le contenu** (`esc()`) si les données ne viennent pas de toi (Google Sheet, formulaire).

## Comment l'intégrer dans un autre projet

1. Repérer comment le projet rend ses éléments (template string, React, etc.) et sa palette (variables CSS).
2. Copier les blocs CSS **RETOURNEMENT 3D**, **BOUTONS RONDS** et **CARTE**, puis renommer les variables (`--ink`, `--yel`…) vers celles du projet.
3. Adapter `card(x,pop)` aux champs des données du projet (titre, description, photo, détails, liens).
4. Ajouter `FAV`, `ls`, `drawFav()`, `flipCard()`, `stamp()` et l'écouteur de clics. S'il existe déjà un écouteur global, y ajouter les cas `data-f` et `favBtn`/`favOff` **avant** le cas général.
5. Ajouter le bouton `#favBtn` (caché par défaut) dans l'en-tête, et le mode `S.fav` dans la fonction qui filtre la liste.
6. Ajouter les clés de texte (`fav, favs, favNone, favClose, flip, back`) dans chaque langue.
7. **Tester** dans un navigateur au format téléphone (390×844) et tablette (900 px). Vérifier : étoile → bouton « ★ 1 » visible ; toucher la carte → `.flip` ajouté et liens du verso visibles ; re-toucher → recto ; mode favoris → seules les cartes étoilées ; console sans erreur. Avec Playwright, viser `.fr h2` pour cliquer (le titre existe sur les deux faces).

## Variantes possibles

- Partager les favoris : encoder la liste dans l'URL (`?fav=id1,id2`) pour l'envoyer à quelqu'un.
- Synchroniser entre appareils : remplacer `ls` par un stockage serveur (Google Sheet, base d'un artefact Claude).
- Sans « visité » : supprimer le bouton `.vis` et décaler `.fav` à `right:10px`.
