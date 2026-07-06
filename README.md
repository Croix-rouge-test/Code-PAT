# Code-PAT

Projet de traitement et de consolidation des indicateurs PAT.

Le projet s'appuie principalement sur un notebook d'orchestration, des modules Python par domaine de donnees, et des scripts de controle permettant de verifier les sorties consolidees.

## Fichiers centraux

- `main_pipeline.ipynb` : orchestrateur principal du pipeline. C'est la reference actuelle pour l'ordre d'execution.
- `utils.py` : fonctions utilitaires partagees, notamment import/export Google Sheets, normalisation de libelles et rattachements.
- `data/` : modules metier par source ou domaine (`gaia`, `pegass`, `maraude`, `financier`, `manuelles`, etc.).
- `data/main_merge.py` : fusion finale des indicateurs dans les tables consolidees.
- `checks/` : controles de coherence et comparaison des sorties.
- `requirements.txt` : environnement Python fige actuellement utilise.

## Ordre d'execution probable

1. Ouvrir et executer `main_pipeline.ipynb`.
2. Initialiser les imports, les chemins et les authentifications.
3. Charger les referentiels et les donnees sources.
4. Executer les traitements par domaine depuis les modules `data/`.
5. Fusionner les indicateurs avec `data/main_merge.py`.
6. Exporter les resultats consolides.
7. Lancer les controles dans `checks/` si necessaire.

## Secrets et comptes de service

Le dossier `service_account/` contient des informations locales sensibles ou liees aux authentifications. Il ne doit pas etre versionne ni partage publiquement.

Les fichiers de ce dossier sont volontairement ignores par Git via `.gitignore`.

## Note

Le notebook `main_pipeline.ipynb` reste aujourd'hui la source principale de pilotage du projet. Les modules Python servent de briques appelees par ce notebook.
