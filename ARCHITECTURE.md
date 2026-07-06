# Architecture actuelle

Ce document decrit la cartographie actuelle du projet sans modifier la logique metier.

## Vue generale

Le projet est organise autour du notebook `main_pipeline.ipynb`, qui orchestre les chargements, traitements, calculs, fusions et exports. Les fichiers Python sont principalement des modules de fonctions appeles depuis ce notebook.

## Orchestrateur

- `main_pipeline.ipynb` : point d'entree principal et ordre d'execution de reference.
- Le notebook configure les chemins, les authentifications, les dates cibles, les imports, les chargements Google Sheets et BigQuery, puis appelle les fonctions des modules.

## Modules metier

Le dossier `data/` contient les traitements par domaine :

- `gaia.py` : benevoles et indicateurs GAIA.
- `pegass.py` : activites PEGASS et indicateurs associes.
- `nomination.py` : donnees de nomination et referents.
- `impact.py` : indicateurs IMPACT.
- `financier.py` : donnees financieres et indicateurs associes.
- `mobilite.py` : mobilite.
- `manuelles.py` : donnees manuelles et indicateurs derives.
- `maraude.py` : traitements actifs des maraudes.
- `maraude_manuel.py` : traitements maraudes manuelles, actuellement references en commentaires dans le notebook.
- `domifa.py`, `alim.py`, `dps.py`, `adherent.py` : domaines specifiques.
- `base_contact_formations_initiales.py`, `Base_contact_retravail.py`, `Base_contact_session_et_gd_public.py` : traitements Base Contact et formations.
- `Indicateurs_composites.py` : indicateurs composes.
- `main_merge.py` : consolidation et fusion finale.

## Utilitaires

- `utils.py` centralise des helpers partages : Google Sheets, normalisation, rapprochement de libelles, verifications et rattachements.
- Plusieurs modules importent actuellement `utils.py` directement.

## Controles

Le dossier `checks/` contient les scripts de verification :

- `checks/checks.py` : script principal de controle.
- `checks/ref_create.py` : creation de feuille de reference, avec confirmation interactive.
- `checks/core.py` : logique de comparaison, aggregation et export des controles.
- `checks/helpers.py` : helpers de controle.

## Dependances et donnees externes

Le projet depend principalement de :

- Google Sheets via `gspread` et `gspread_dataframe`.
- BigQuery via les bibliotheques Google Cloud.
- `pandas`, `numpy` et bibliotheques scientifiques.
- `sentence_transformers` et un modele local dans `models/` pour le rapprochement de libelles.

## Points de vigilance identifies

- Les imports reposent encore sur des chemins ajoutes via `sys.path.append`.
- Plusieurs valeurs de configuration sont codees dans le notebook ou dans les modules : dates, annees, URLs Google Sheets, noms de datasets BigQuery.
- Certains helpers semblent dupliques entre `utils.py` et `checks/helpers.py`.
- Les fichiers `.pyc`, caches et secrets doivent rester hors suivi Git.

Cette cartographie sert de reference de nettoyage leger. Elle ne constitue pas une refactorisation.
