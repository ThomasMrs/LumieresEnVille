# Lumières en Ville — Service Web : modifications à réaliser

> Document de suivi des écarts entre le **serveur (Service Web Python/FastAPI/sqlite3)**
> et le **cahier des charges** (§3, §4, §7.4, §8, §10).
> Périmètre : **partie serveur uniquement**.

**Légende statut :** ⬜ À faire · 🟦 En cours · ✅ Fait

---

## Sommaire

- [P1 — Indispensable](#p1--indispensable-bloquant-pour-la-note-web)
- [P2 — Important](#p2--important)
- [P3 — Bonus](#p3--bonus)
- [Corrections techniques](#corrections-techniques-bugs)
- [Récapitulatif / checklist](#récapitulatif--checklist-de-livraison)

---

## P1 — Indispensable (bloquant pour la note Web)

### 1. Séparer la couche « stockage » de la couche « règles de gestion » ⬜
- **Réf. CdC :** §7.4.1 (architecture 3 tiers : IHM / règles de gestion / stockage) et §7.4.5 (« Séparer clairement les règles de gestion des fonctions de stockage »).
- **Constat :** tout le SQL (`ajouter_*`, `lire_*`, `modifier_*`, `supprimer_*`) est mélangé dans les fichiers de `routes/`. `gestion.py` ne contient que la validation.
- **Où :** `routes/*.py`, `gestion.py`.
- **À faire :**
  - Créer une couche stockage dédiée, p. ex. `stockage/` (un module par entité : `stockage/semaphore.py`, `stockage/robot.py`, …) **ou** un `stockage.py` regroupant les accès DB.
  - Y déplacer **toutes** les fonctions qui font du `sqlite3` (connexion, INSERT/SELECT/UPDATE/DELETE).
  - Les fichiers `routes/*.py` ne contiennent plus que : définition des routes + appels à `gestion` (validation) + appels à `stockage` (lecture/écriture).
  - Factoriser l'ouverture/fermeture de connexion (helper `get_conn()`).

### 2. Gérer les « objets reconnus / autorisés » ⬜
- **Réf. CdC :** §3 (« Les objets reconnus et autorisés peuvent communiquer »), §7.4.3 (« API permettant aux objets reconnus d'interagir »), §7.4.4 (« Liste des contrôleurs, robots et sémaphores autorisés à se connecter »).
- **Constat :** la table `team` a `ip` et `allowed`, mais **aucune vérification** n'est faite ; aucune notion de **contrôleur**.
- **Où :** `database.py`, nouvelle dépendance de routes / middleware.
- **À faire :**
  - Définir clairement la liste des objets autorisés (par IP et/ou par identifiant) : contrôleurs, robots, sémaphores.
  - Ajouter une vérification d'autorisation sur les routes sensibles (dépendance FastAPI `Depends(...)` ou middleware) : refuser (403) si l'appelant n'est pas autorisé.
  - Exposer un endpoint de consultation de la liste des objets autorisés.

### 3. Permettre au sémaphore de signaler le symbole affiché ⬜
- **Réf. CdC :** §3 (« Sémaphores → Service Web : disponibilité, **affichage en cours, symbole affiché** »).
- **Constat :** la table `semaphore` (`id, name, state, duration, type, coord_x, coord_y`) n'a **pas de champ** pour le symbole en cours.
- **Où :** `database.py` (table `semaphore`), `routes/semaphores.py`.
- **À faire :**
  - Ajouter une colonne, p. ex. `current_shape_id TEXT` (FK vers `shape`) et/ou `displaying INTEGER`.
  - Mettre à jour `add/update_semaphore` et les fonctions de stockage associées.

### 4. Endpoint d'action « déclencher l'affichage » ⬜
- **Réf. CdC :** §3 (« Robots → Sémaphores via Service Web : déclenchement de l'affichage demandé lorsque le robot arrive près du sémaphore »).
- **Constat :** aucun endpoint dédié ; il faut bricoler avec `update_semaphore`.
- **Où :** `routes/semaphores.py` (ou `routes/missions.py`).
- **À faire :**
  - Créer un endpoint type `POST /api/semaphore/{id}/display` (paramètres : `shape_id`, éventuellement `mission_id`).
  - Logique : vérifier autorisation + existence, passer le sémaphore en `Occupied`, renseigner `current_shape_id`, et faire évoluer l'état de la mission (`Done` / `Pending_*`).

### 5. README serveur (installation, lancement, test) ⬜
- **Réf. CdC :** §4, §10.1 (« Le README contient les instructions d'installation, de lancement et de test »).
- **Constat :** pas de `README.md` dans `serveur/`. Le README racine est **obsolète** : routes inexistantes (`/list_node`, `/add_node`), états de mission faux (`Pending | In progress | Done` au lieu de `Awaiting / Pending_robot / Pending_semaphore / Done`), et il **omet** segment / config / grille / shape / health.
- **Où :** `serveur/README.md` (à créer) + corriger le README racine.
- **À faire :**
  - Installation : créer venv + `pip install -r requirements.txt`.
  - Lancement : `python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000` (+ Swagger `/docs`).
  - Architecture 3 tiers, description des tables et des routes **à jour**.
  - Comment lancer les tests + comment initialiser la base.

---

## P2 — Important

### 6. Écrire de vrais tests unitaires ⬜
- **Réf. CdC :** §7.4.5 (« Coder directement des tests unitaires… lorsque pertinent »), §8 (« Présence de tests… des principaux flux »).
- **Constat :** `tests/test.py` n'est qu'un **script de peuplement** (aucune assertion, pas de framework).
- **Où :** `tests/`.
- **À faire :**
  - Ajouter des tests avec assertions (idéalement `unittest`, présent dans la stdlib — éviter `pytest` si on veut rester « sans module supplémentaire »).
  - Couvrir les flux principaux : création mission complète, validation des coordonnées/états/types, autorisation, déclenchement d'affichage.
  - Utiliser une base de test isolée (ne pas polluer `lumieres.db`).

### 7. Nettoyer les dépendances non autorisées ⬜
- **Réf. CdC :** §7.4.2 (« fastapi et uvicorn de base uniquement, sans module supplémentaire ; sqlite3 ; uuid »).
- **Constat :** `requirements.txt` contient `requests` (inutilisé côté serveur) et `python-multipart` (requis par l'upload CSV via `UploadFile`).
- **Où :** `requirements.txt`, `main.py` (route `/ihm/add_shape_csv`).
- **À faire :**
  - Retirer `requests` (non utilisé).
  - Pour `python-multipart` : soit le justifier explicitement dans le rapport, soit remplacer l'upload de fichier par une saisie texte (collage de la matrice CSV dans un champ `<textarea>`) afin de rester strictement dans les modules autorisés.

### 8. Compléter le paramétrage attendu ⬜
- **Réf. CdC :** §7.4.4.
- **Constat / à faire :**
  - **Liste des autres services Web** (synchronisation éventuelle) : ni table ni endpoint → créer une table `service_web` (id, name, url, …) + routes de consultation.
  - **Taille des routes** et **vitesse d'avancement sur les routes** : les `segment` n'ont ni longueur ni vitesse → ajouter `length` (et/ou `speed`) à la table `segment`, ou un paramètre global dans `config`.

### 9. Endpoint « mission disponible pour un robot » ⬜
- **Réf. CdC :** §8.1 (« Un robot disponible peut récupérer une mission »).
- **Constat :** pas d'endpoint dédié ; le robot doit lire toute la liste et filtrer.
- **Où :** `routes/missions.py`.
- **À faire :** `GET /api/missions/available` → missions à l'état `Awaiting` sans `robot_id`, optionnellement filtrées par `team`.

### 10. Horodatage / calculs centralisés côté serveur ⬜
- **Réf. CdC :** §3 (« les informations… et l'horodatage sont pris en charge par les API du service Web »).
- **Constat :** les missions stockent `start_date` / `time` mais le serveur ne calcule rien.
- **Où :** `routes/missions.py`.
- **À faire :** générer l'horodatage serveur (date de prise en charge, de fin), exposer des informations calculées (durée réelle, etc.).

---

## P3 — Bonus

> À n'engager **que si le socle P1/P2 est totalement opérationnel** (cf. §2.3 et §10.2 du CdC).

### 11. Interface graphique de suivi statistique ⬜ (+3 pts, §7.4.7)
- Page Web affichant la **moyenne** et l'**écart-type** de réalisation des missions **par robot** et **par sémaphore**.

### 12. Calcul des informations de circulation ⬜ (§3, §7.3.3)
- Logique serveur empêchant deux robots d'emprunter la **même portion de route (segment)** simultanément (réservation/verrou de segment).

---

## Corrections techniques (bugs)

### B1. Bug d'injection HTML/CSS dans `main.py` ⬜
- **Constat :** `page_html()` fait `html.replace("", f"<style>{css}</style>")` et `html.replace("", message)`. Remplacer une **chaîne vide** insère le contenu entre **chaque** caractère → injection incorrecte.
- **Où :** `main.py`, fonction `page_html()`.
- **À faire :** utiliser un vrai marqueur dans `index.html` (ex. `</head>` pour le CSS, un placeholder `<!--MESSAGE-->` pour le message) et remplacer ce marqueur.

### B2. Incohérence type de sémaphore IHM ⬜
- **Constat :** `static/index.html` propose `type = "HELICE"` (majuscules) alors que la validation `valider_type_semaphore` n'accepte que `Ascii | Tracant | Helice` → l'ajout via l'IHM échoue (400).
- **Où :** `static/index.html`.
- **À faire :** aligner les valeurs (liste déroulante `Ascii / Tracant / Helice`).

---

## Récapitulatif / checklist de livraison

| #  | Priorité | Modification                                              | Réf. CdC          | Statut |
|----|----------|----------------------------------------------------------|-------------------|--------|
| 1  | P1       | Séparer stockage / règles de gestion                     | §7.4.1, §7.4.5    | ⬜     |
| 2  | P1       | Autorisation des objets reconnus (contrôleurs/robots/sémaphores) | §3, §7.4.3-4 | ⬜     |
| 3  | P1       | Champ « symbole affiché » sur le sémaphore               | §3                | ⬜     |
| 4  | P1       | Endpoint déclenchement d'affichage                       | §3                | ⬜     |
| 5  | P1       | README serveur (install/lancement/test) + MAJ README racine | §4, §10.1      | ⬜     |
| 6  | P2       | Vrais tests unitaires                                    | §7.4.5, §8        | ⬜     |
| 7  | P2       | Nettoyer dépendances non autorisées                      | §7.4.2            | ⬜     |
| 8  | P2       | Paramétrage : autres services Web + taille/vitesse routes| §7.4.4            | ⬜     |
| 9  | P2       | Endpoint « mission disponible »                          | §8.1              | ⬜     |
| 10 | P2       | Horodatage / calculs centralisés                         | §3                | ⬜     |
| 11 | P3       | IHM statistiques (moyenne / écart-type)                  | §7.4.7            | ⬜     |
| 12 | P3       | Gestion des conflits de circulation (segments)           | §3, §7.3.3        | ⬜     |
| B1 | Bug      | Injection HTML/CSS `page_html()`                         | —                 | ⬜     |
| B2 | Bug      | Type sémaphore IHM (`HELICE` vs `Helice`)                | —                 | ⬜     |

---

*Document généré le 2026-06-13 à partir de l'analyse du code serveur et du cahier des charges « Lumières en Ville ».*
