import traceback
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from PyPDF2 import PdfReader, PdfWriter
import json
import gspread
from gspread_dataframe import get_as_dataframe
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from PyPDF2 import PdfReader, PdfWriter
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader
import math
import os
import matplotlib.pyplot as plt
from IPython.display import Image, display
import fitz  # PyMuPDF
from PIL import Image as PILImage
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib.ticker as mtick
from matplotlib.patches import Patch
import io
import re
import shutil
import zipfile
from google.colab import drive, files

from google.colab import auth
from google.auth import default
import unicodedata
import re
import torch
from sentence_transformers import SentenceTransformer, util
from functools import reduce


# Mensualisation 

def monthly_parsing(df, year):
  def month_conditions(date):
    months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet' , 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    for i in range(len(months)):
      if date.month == i + 1 :
        return months[i]
  df['Mois'] = df.apply(lambda x: month_conditions(x['date']), axis=1)
  df['Année'] = year
  return df


# Exporter le fichier de sortie en xlsx


def export_to_excel_download(dataframe, file_name='data.xlsx'):
    """
    Exporte un DataFrame en fichier Excel et le télécharge depuis Google Colab.

    Parameters:
        dataframe (pd.DataFrame): Le DataFrame à exporter.
        file_name (str): Le nom du fichier Excel à télécharger (par défaut 'data.xlsx').
    """
    dataframe.to_excel(file_name, index=False)
    files.download(file_name)

# Ouvrir un google sheet

def sheet_to_dataframe(client, url, sheet_index=0, sheet_name=None, header_row=1):
    """
    Ouvre une feuille Google Sheets et crée un DataFrame Pandas à partir de ses données.

    Cette fonction prend en entrée l'URL de la feuille Google Sheets, un client Google Sheets autorisé,
    l'index de la page souhaitée ou le nom de la feuille, et la ligne utilisée comme en-tête. Elle renvoie les données de la
    feuille sous forme de DataFrame Pandas.

    Args:
        url (str): L'URL de la feuille Google Sheets.
        client (gspread.Client): Client Google Sheets autorisé.
        sheet_index (int, optional): L'index de la page à ouvrir dans la feuille. Par défaut, 0 (première page).
        sheet_name (str, optional): Le nom de la feuille à ouvrir. Si fourni, prioritaire sur sheet_index.
        header_row (int, optional): Le numéro de la ligne à utiliser comme en-têtes de colonnes pour le DataFrame.
                                   Par défaut, 1 (la première ligne de données après l'en-tête de feuille).

    Returns:
        pd.DataFrame: Un DataFrame Pandas contenant les données de la feuille avec la première ligne spécifiée
                      comme en-tête des colonnes.
    """

    # Ouvre la feuille Google Sheets à partir de l'URL
    sheet = client.open_by_url(url)

    # Sélectionne la page (worksheet) souhaitée
    if sheet_name:
        worksheet = sheet.worksheet(sheet_name)
    else:
        worksheet = sheet.get_worksheet(sheet_index)

    # Récupère toutes les valeurs de la page
    data = worksheet.get_all_values()

    # Crée le DataFrame en utilisant la ligne spécifiée comme en-tête
    df = pd.DataFrame(data[header_row:], columns=data[header_row - 1])

    print(f"✅ Chargement des données réalisées")
    print(f"    Sheet : {sheet.title}")
    print(f"    Feuille {sheet_index + 1 if not sheet_name else ''} : {worksheet.title} ({len(data) - header_row} lignes et {len(data[header_row - 1])} colonnes)\n")

    return df

# Definition des filtres classiques

# #Fonction filtre simple (on met le nom de la colonne)
# def filtre(df, col, key, filters=FILTERS):
#     values = filters[col][key]
#     return df.loc[df[col].isin(values)].copy()

# #Fonction filtre et remplace
# def filtre_et_remplace(df, col, key, filters=FILTERS):
#   values = filters[col][key]
#   mask = df[col].isin(values)
#   df.drop(df.index[~mask], inplace=True)


# # def filtre(df, key, filters=FILTERS):
# def filtre(df, key, filters=FILTERS_PEGASS):
#     rule = filters[key]
#     col = rule["col"]
#     values = rule["values"]
#     return df.loc[df[col].isin(values)]


#Fonction filtre date

def filtre_2025(df, date_col="debut_inscription", dayfirst=True):
    s = pd.to_datetime(df[date_col], errors="coerce", dayfirst=dayfirst)
    return df.loc[s.between("2025-01-01 00:00", "2026-01-01 00:00", inclusive="left")]

#Fonction utile pour renommer automatiquement les variables
#Attention pour simplifier la fonction il faut que le nom initial de la Dataframe soit le même avec la colonne "nom tablme du dictionnaire de données :  Pegass_Inscription_rename = renommer_par_nom_table(PEGASS_PegassInscription, "PEGASS_PegassInscription", mapping_df)"

#On récupère la table qui sera la table "dictionnaire de données" = sans doute un url
def renommer_par_nom_table(df, nom_table, mapping_df):
    # On filtre le mapping sur cette table
    mapping_table = mapping_df[mapping_df["nom_table"] == nom_table]
    mapping_dict = dict(zip(mapping_table["nom_variable"], mapping_table["rename"]))
    return df.rename(columns=mapping_dict)

def filtre(df, key, filters=None):
    # Applique un filtre défini dans un dictionnaire de règles :
    # filters = {
    #     "nom_filtre": {"col": "nom_colonne", "values": [...]}
    # }

    # Si filters n'est pas fourni, on utilise le dict global FILTERS_PEGASS.
    # ⚠ Ici, on ne touche à FILTERS_PEGASS qu'au moment de l'APPEL, pas à la définition

    if filters is None:
        filters = globals()["FILTERS_PEGASS"]  # va chercher le dict global au moment de l'appel

    rule = filters[key]
    col = rule["col"]
    values = rule["values"]

    # si values est une seule valeur, on l'encapsule dans une liste
    if not isinstance(values, (list, tuple, set)):
        values = [values]

    return df.loc[df[col].isin(values)]


# Normaliser les libellés des structures

def normalize_structure(structure: str) -> str:
    if structure is None:
        return structure

    # Enlève les accents (UNITÉ -> UNITE, DÉLÉGATION -> DELEGATION, etc.)
    s = unicodedata.normalize("NFD", structure)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")

    # Remplacements (insensible à la casse)
    s = re.sub(r"\bUNITE\s+LOCALE\b", "UL", s, flags=re.IGNORECASE)
    s = re.sub(r"\bDELEGATION\s+TERRITORIALE\b", "DT", s, flags=re.IGNORECASE)

    return s
# Rapprochement libellés quand on a ni les codes 

def rapprochement_libelles(df_ref, df_traiter, colonne_analyser, seuil_alerte=0.80, embeddings_file='reference_embeddings.pt', silent=True):
    # Ensure df_ref['nom_structure'] is string type and handle potential NaNs
    df_ref['nom_structure'] = df_ref['nom_structure'].fillna('').astype(str)

    # Charger le modèle pré-entraîné
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # Obtenir les embeddings des libellés de référence
    reference_labels = df_ref['nom_structure'].tolist()

    # Always compute reference_embeddings from the current reference_labels to prevent mismatch
    reference_embeddings = model.encode(reference_labels, convert_to_tensor=True)

    # Dictionnaire pour mémoriser les rapprochements déjà calculés
    memo_similarities = {}

    # Fonction pour trouver le libellé de référence le plus similaire
    def find_most_similar(label, reference_embeddings, reference_labels):
        if label in memo_similarities:
            return memo_similarities[label]
        else:
            label_embedding = model.encode(label, convert_to_tensor=True)
            cosine_scores = util.pytorch_cos_sim(label_embedding, reference_embeddings)[0]
            top_result = torch.argmax(cosine_scores)
            result = (reference_labels[top_result], cosine_scores[top_result].item())
            memo_similarities[label] = result
            return result

    # Ajouter les colonnes N_structure et Libelle au DataFrame à traiter
    df_traiter['n_structure'] = None
    df_traiter['nom_structure'] = None

    # Rapprocher chaque libellé et mettre à jour le DataFrame
    for index, row in df_traiter.iterrows():

        label_to_match = row[colonne_analyser]

        # Simplifications et corrections des libellés
        label_to_match_rework = re.sub(r'unité locale', 'UL', str(label_to_match), flags=re.IGNORECASE)
        label_to_match_rework = re.sub(r'direction territoriale', 'DT', label_to_match_rework, flags=re.IGNORECASE)
        label_to_match_rework = re.sub(r'antenne', 'AL', label_to_match_rework, flags=re.IGNORECASE)
        label_to_match_rework = re.sub(r'unite locale', 'UL', label_to_match_rework, flags=re.IGNORECASE)

        # Trouver le libellé de référence le plus proche
        most_similar_label, score = find_most_similar(label_to_match_rework, reference_embeddings, reference_labels)
        matching_code = df_ref[df_ref['nom_structure'] == most_similar_label]['n_structure'].values[0]

        # Condition sur le score
        if score > seuil_alerte:
            if not silent:
                print(f"✅ {label_to_match} -> {most_similar_label} (Score: {score:.2f})")
            df_traiter.at[index, 'n_structure'] = matching_code
            df_traiter.at[index, 'nom_structure'] = most_similar_label
        else:
            if not silent:
                print(f"⚠️ {label_to_match} -> {most_similar_label} (Score: {score:.2f})")
            df_traiter.at[index, 'n_structure'] = ""
            df_traiter.at[index, 'nom_structure'] = ""

    return df_traiter

# Sauvegarder les données dans un sheet

def save_dataframe_to_sheet(spreadsheet_id, client, df, sheet_name=None):
    """
    Sauvegarde un DataFrame dans une feuille Google Sheets.

    Args:
        spreadsheet_id (str): L'identifiant du Google Sheets.
        client (gspread.Client): Client Google Sheets autorisé.
        df (pd.DataFrame): DataFrame Pandas à sauvegarder.
        sheet_name (str, optional): Nom de la feuille cible.
                                     Si elle n'existe pas, elle sera créée.
                                     Si None, la première feuille sera utilisée.
    """

    if df is None or df.empty:
        raise ValueError("Le DataFrame est vide ou invalide.")

    # 1️⃣ Ouvre le spreadsheet
    spreadsheet = client.open_by_key(spreadsheet_id)

    # 2️⃣ Sélectionne ou crée la feuille
    if sheet_name:
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            print(f"📄 Feuille existante '{sheet_name}' sélectionnée.")
        except Exception:
            print(f"➕ La feuille '{sheet_name}' n'existe pas. Création en cours...")
            worksheet = spreadsheet.add_worksheet(
                title=sheet_name,
                rows=str(len(df) + 100),
                cols=str(len(df.columns) + 10)
            )
            print(f"✅ Feuille '{sheet_name}' créée.")
    else:
        worksheet = spreadsheet.get_worksheet(0)
        print(f"📄 Première feuille sélectionnée : '{worksheet.title}'")

    # 3️⃣ Nettoie la feuille
    worksheet.clear()
    print(f"🗑️ Les anciennes données ont été supprimées de la feuille '{worksheet.title}'")

    # 4️⃣ Conversion en string (sécurité format)
    df_to_save = df.copy().astype(str)

    # 5️⃣ Écriture des données
    worksheet.update(
        [df_to_save.columns.values.tolist()] + df_to_save.values.tolist()
    )

    # 6️⃣ Confirmation
    print(f"💾 Données sauvegardées dans '{spreadsheet.title}' → feuille '{worksheet.title}'")
    print(f"    Nombre de lignes : {len(df_to_save)}")
    print(f"    Nombre de colonnes : {len(df_to_save.columns)}")


# Vérifications

def verifier_colonne_structure(df, col_code_structure, df_ref_structure):
    """
    Vérifie la validité d'une colonne de codes structure :
    - Présence de NaN ou de chaînes vides
    - Doublons
    - Existence dans le référentiel
    """
    print(f"\n🔎 Vérification de la colonne '{col_code_structure}'")

    # 1. Vérification des NaN ou valeurs vides
    lignes_vides = df[df[col_code_structure].isna() | (df[col_code_structure] == "")]
    if not lignes_vides.empty:
        print(f"   ❌ {len(lignes_vides)} valeur(s) manquante(s) ou vide(s) détectée(s).")
    else:
        print("   ✅ Aucun NaN ou valeur vide détecté.")

    # 2. Vérification des doublons (uniquement les codes)
    doublons_series = df[col_code_structure][df[col_code_structure].duplicated(keep=False)]
    if not doublons_series.empty:
        codes_doublons = sorted(doublons_series.value_counts().index.tolist())
        print(f"   ❌ {len(codes_doublons)} code(s) en doublon : {codes_doublons}")
    else:
        print("   ✅ Aucun doublon détecté.")

    # 3. Vérification des codes absents du référentiel
    codes_dans_df = set(df[col_code_structure].dropna().unique())
    codes_dans_ref = set(df_ref_structure[col_code_structure].dropna().unique())
    codes_manquants = codes_dans_df - codes_dans_ref

    if codes_manquants:
        print(f"   ❌ {len(codes_manquants)} code(s) non trouvés dans le référentiel : {sorted(codes_manquants)}")
    else:
        print("   ✅ Tous les codes sont présents dans le référentiel.")


def verifier_mapping(df, col_code_structure, col_libele, df_ref_structure):
    """
    Vérifie la validité d'une colonne de codes structure :
    - Présence de NaN ou de chaînes vides (affiche les libellés correspondants)
    - Doublons (affiche les codes)
    - Existence dans le référentiel (affiche les codes manquants)
    """
    print(f"\n🔎 Vérification de la colonne '{col_libele}' et mapping associé '{col_code_structure}'")

    lignes_vides = df[df[col_code_structure].isna() | (df[col_code_structure] == "")]
    if not lignes_vides.empty:
        print(f"   ❌ {len(lignes_vides)} Valeurs non mappées. Libellés associés :")
        print(sorted(lignes_vides[col_libele].dropna().unique().tolist()))
    else:
        print("   ✅ Mapping réalisé avec succès.")

# Vérification qu'on a bien la même somme entre le fichier source et le fichier de sortie

def check_sum_equal(df_left, col_left, df_right, col_right, label_left="DF1", label_right="DF2", raise_on_fail=True):
    """
    Compare la somme de df_left[col_left] et df_right[col_right].
    - Coerce en numérique (NaN -> 0)
    - Affiche OK si égal, sinon affiche l'écart et lève une erreur si raise_on_fail=True
    """
    s_left = pd.to_numeric(df_left[col_left], errors="coerce").fillna(0).sum()
    s_right = pd.to_numeric(df_right[col_right], errors="coerce").fillna(0).sum()

    if s_left != s_right:
        msg = (
            f"Incohérence ❌ : somme {label_left}[{col_left}]={s_left} "
            f"vs {label_right}[{col_right}]={s_right} (écart={s_left - s_right})"
        )
        if raise_on_fail:
            raise ValueError(msg)
        else:
            print(msg)
            return False

    print(f"OK ✅ : sommes égales ({s_left}) entre {label_left}[{col_left}] et {label_right}[{col_right}]")
    return True

def keep_integer(x):
  """
  En utilisant avec .apply() sur une colonne d'un dataframe,
  permet de garder uniquement la partie avec des nombres du str.
  Input doit être un str.
  """
  return re.sub("[^0-9]", "", x)
  
def dt_rattachement(df, df_ref_structure):
  """
  Permet d'associer les structures du dataframe avec la DT de rattachement, 
  utile pour le merge avec toutes les données par DT. 
  """
  df_return = pd.merge(df, df_ref_structure[['n_structure','DT_de_rattachement']], on="n_structure", how="left")
  df_return['DT_de_rattachement'] = df_return['DT_de_rattachement'].astype(str).apply(keep_integer)
  return df_return

def merge_left_on_df1(df1, l, on):
  return reduce(lambda left, right: left.merge(right, how='left', on=on), l, df1)
