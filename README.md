# Code-PAT

Projet de traitement et de consolidation des indicateurs PAT.

Le projet s'appuie principalement sur un notebook d'orchestration, des modules Python par domaine de données et des scripts de contrôle permettant de vérifier les sorties consolidées.

## Objectif

Les rapports territoriaux ont besoin d'être alimentés par plusieurs sources de données de formats différents. Le code de ce dépôt GitHub permet de rassembler et d'agréger ces données dans un fichier unique.

## Structure du dépôt

- `main_pipeline.ipynb` : orchestrateur principal du pipeline. C'est la référence actuelle pour l'ordre d'exécution.
- `utils.py` : fonctions utilitaires partagées, notamment import/export Google Sheets, normalisation de libellés et rattachements.
- `data/` : modules métier par source ou domaine (`gaia`, `pegass`, `maraude`, `financier`, `manuelles`, etc.).
- `data/main_merge.py` : fusion finale des indicateurs dans les tables consolidées.
- `checks/` : contrôles de cohérence et comparaison des sorties.
- `requirements.txt` : environnement Python figé actuellement utilisé.
- `models/paraphrase-MiniLM-L6-v2` : modèle de texte issu de Hugging Face, utilisé dans la pipeline.

## Comptes de service

Le dépôt local doit contenir un dossier `service_account/`. Il contient des informations locales sensibles ou liées aux authentifications. Pour obtenir les données relatives aux comptes de service nécessaires à la pipeline, demander aux personnes responsables du projet qui pourront transmettre un dossier contenant les json des comptes de services utilisés, il ne doit pas être versionné ni partagé publiquement.

Les fichiers de ce dossier sont volontairement ignorés par Git via le fichier `service_account/.gitignore`, qui doit rester présent dans le dossier.

## Installation

Actuellement, le code est exécuté et modifié sous Visual Studio Code dans un environnement local. Systèmes pris en charge : Windows (avec Git Bash) et Linux.

- Installer Python 3.14.3.
- Importer le dépôt en local.
- Depuis la racine du dépôt, créer un environnement virtuel Python : `python -m venv .venv`.
- Activer l'environnement sous Git Bash : `source .venv/Scripts/activate`.
- Installer les dépendances : `pip install -r requirements.txt`.

## Exécution du pipeline

1. Ouvrir `main_pipeline.ipynb`.
2. Modifier les variables dans la section `Variables globales` si besoin, notamment la date `TARGET_DATE`, qui est la date où on arrête les données.
3. Exécuter toutes les cellules dans l'ordre.

## Description du fichier de sortie

Le fichier de sortie contient deux feuilles, `DT` et `UL`. Chaque feuille contient, sous forme de colonnes, les indicateurs nécessaires à la création des rapports ; leur nombre peut différer entre les deux feuilles. Les données sont regroupées par DT dans la feuille `DT`, et par UL ou AL dans la feuille `UL`.

## Notes

Le notebook `main_pipeline.ipynb` reste aujourd'hui la source principale de pilotage du projet. Les modules Python servent de briques appelées par ce notebook.

- DT : délégation territoriale.
- UL : unité locale.
- AL : antenne locale.
- PAT : plan d'action territorial (ou plans d'action territoriaux).

## Auteurs

- Clément Souk-Aloun : clement.souk-aloun@croix-rouge.fr
- Ana Capron : ana.capron@croix-rouge.fr
- Sandrine Bonin : sandrine.bonin@croix-rouge.fr
- Clément Dilasser : clement.dilasser@croix-rouge.fr
