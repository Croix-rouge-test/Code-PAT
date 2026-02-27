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
from typing import List, Dict
import pandas as pd


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


def def_Structure_de_rattachement(df_ref_structure):
  rattachement_successif =   df_ref_structure[
        df_ref_structure["type_structure"].isin([ 'IMPLANTATION LOCALE HORS AL - IL'])
    ].copy()
  rattachement_successif = rattachement_successif [[
        "n_structure",
        "type_structure",
        "Structure_de_rattachement"
    ]].copy()

  rattachement_successif["N structure de rattachement"] = (
        rattachement_successif ["Structure_de_rattachement"]
        .astype("string")
        .str.split("-", n=1, expand=True)[0]
        .str.strip()
    )
  rattachement_successif .loc[rattachement_successif ["Structure_de_rattachement"].isna(), "N structure de rattachement"] = pd.NA


  return rattachement_successif

def add_num_structure_rattachement(
    df: pd.DataFrame,
    col_source: str,
    col_out: str = "N structure de rattachement"
) -> pd.DataFrame:
    """
    Crée une colonne col_out = partie avant le 1er '-' dans col_source.
    Exemple: '10 - DT DES ALPES MARITIMES' -> '10'

    - Gère NaN
    - Trim espaces
    - Ne modifie pas le df original (retourne une copie)
    """
    out = df.copy()

    out[col_out] = (
        out[col_source]
        .astype("string")
        .str.split("-", n=1, expand=True)[0]
        .str.strip()
    )

    # Optionnel : remettre <NA> si la source est vide/NA
    out.loc[out[col_source].isna(), col_out] = pd.NA

    return out

def rattache_structure(df1, df_ratt,col):
    # mapping : n_structure -> N structure de rattachement
    mapping = (
        df_ratt.set_index(df_ratt["n_structure"].astype("string"))["N structure de rattachement"]
        .astype("string")
    )

    col = col

    s = df1[col].astype("string")
    s2 = s.map(mapping)

    # si pas trouvé dans le mapping, on garde l'original
    df1[col] = s2.fillna(s)

    # optionnel : repasser en entier nullable
    df1[col] = pd.to_numeric(df1[col], errors="coerce").astype("Int64")

    return df1

    
def apply_rattachement_successif(df_ref_structure, df_maraude, col="maraude_structure_id_fk"):
    # 1) Ajout "N structure de rattachement" dans le ref structure
    df_ref_structure = add_num_structure_rattachement(
        df=df_ref_structure,
        col_source="Structure_de_rattachement",
        col_out="N structure de rattachement"
    )

    # 2) Création du référentiel "rattachement successif"
    rattachement_successif = def_Structure_de_rattachement(df_ref_structure)

    # Vérif : nb de rattachements manquants
    c = rattachement_successif["N structure de rattachement"].isna().sum()

    # 3) Application du rattachement sur le df de travail
    df_maraude = rattache_structure(df_maraude, rattachement_successif, col=col)

    return df_ref_structure , c , rattachement_successif, df_maraude


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

    def safe_merge(left, right):
        # Supprime les colonnes déjà présentes (sauf la clé)
        cols_to_drop = [col for col in right.columns if col in left.columns and col != on]
        right_clean = right.drop(columns=cols_to_drop)

        return left.merge(right_clean, how='left', on=on)

    return reduce(safe_merge, l, df1)

def find_duplicates_in_list_of_dfs(dfs, column):
    """
    Pour chaque DataFrame dans une liste, trouve les doublons dans la colonne spécifiée.

    Args:
        dfs (list of pd.DataFrame): Liste de DataFrames à analyser
        column (str): Nom de la colonne sur laquelle chercher les doublons

    Returns:
        dict: Clé = index du DataFrame, Valeur = DataFrame des doublons
    """
    duplicates_dict = {}

    for i, df in enumerate(dfs):
        if column not in df.columns:
            print(f"⚠️ DataFrame {i} : la colonne '{column}' n'existe pas.")
            continue

        # Trouve les doublons
        df_duplicates = df[df.duplicated(subset=[column], keep=False)]

        if not df_duplicates.empty:
            duplicates_dict[i] = df_duplicates
            print(f"🔹 DataFrame {i} : {len(df_duplicates)} doublons trouvés dans '{column}'")
        else:
            print(f"✅ DataFrame {i} : aucun doublon dans '{column}'")

    return duplicates_dict


def check_same_col_sum(df_left: pd.DataFrame,
                       df_right: pd.DataFrame,
                       col: str,
                       dropna: bool = True,
                       atol: float = 0.0,
                       rtol: float = 0.0):
    """
    Vérifie que la somme de la colonne `col` est la même dans 2 DataFrames.

    Parameters
    ----------
    df_left, df_right : pd.DataFrame
        DataFrames à comparer
    col : str
        Nom de la colonne (même intitulé dans les 2 df)
    dropna : bool
        Si True, les NaN sont traités comme 0 (via fillna(0))
    atol, rtol : float
        Tolérances absolue et relative (utile si float)

    Returns
    -------
    result : dict
        Résumé des sommes + delta
    ok : bool
        True si égalité (avec tolérances), sinon False
    """
    if col not in df_left.columns:
        raise KeyError(f"Colonne '{col}' absente de df_left")
    if col not in df_right.columns:
        raise KeyError(f"Colonne '{col}' absente de df_right")

    s1 = pd.to_numeric(df_left[col], errors="coerce")
    s2 = pd.to_numeric(df_right[col], errors="coerce")

    if dropna:
        s1 = s1.fillna(0)
        s2 = s2.fillna(0)

    sum1 = float(s1.sum())
    sum2 = float(s2.sum())
    delta = sum1 - sum2

    ok = abs(delta) <= (atol + rtol * abs(sum2))

    result = {
        "col": col,
        "sum_df_left": sum1,
        "sum_df_right": sum2,
        "delta_left_minus_right": delta,
        "atol": atol,
        "rtol": rtol,
        "ok": ok
    }
    return result, ok

def check_sums_against_final(
    df_final: pd.DataFrame,
    list_of_dfs: List[pd.DataFrame],
    key_col: str = "n_structure",
    dropna: bool = True,
    atol: float = 0.0,
    rtol: float = 0.0
) -> List[Dict]:

    report = []

    for i, df in enumerate(list_of_dfs):
        print(f"\n🔎 Vérification DataFrame {i}")

        cols_to_check = [col for col in df.columns if col != key_col]

        for col in cols_to_check:

            if col not in df_final.columns:
                print(f"   ⚠️ Colonne '{col}' absente du df_final → ignorée")
                continue

            try:
                result, ok = check_same_col_sum(
                    df_left=df,
                    df_right=df_final,
                    col=col,
                    dropna=dropna,
                    atol=atol,
                    rtol=rtol
                )

                summary = {
                    "df_index": i,
                    "col": col,
                    "sum_df_individual": result["sum_df_left"],
                    "sum_df_final": result["sum_df_right"],
                    "atol": atol,
                    "rtol": rtol,
                    "ok": ok
                }

                report.append(summary)

                if ok:
                    print(
                        f"   ✅ '{col}' OK | "
                        f"individuel = {summary['sum_df_individual']} | "
                        f"final = {summary['sum_df_final']}"
                    )
                else:
                    print(
                        f"   ❌ '{col}' KO | "
                        f"individuel = {summary['sum_df_individual']} | "
                        f"final = {summary['sum_df_final']}"
                    )

            except Exception as e:
                print(f"   ⚠️ Erreur sur '{col}' : {e}")

    return report


def traitement_all_data(liste_df_a_fusionner_toutes_structures, liste_df_a_fusionner_DT, df_ref_structure,df_ref_structure_DT):
  colonnes_indicateurs = ['n_structure',
    "Financier Prod_2024",
    "Financier ResNet_2024",
    "Financier ResCorrProd_2024",
    "Financier TresoBrute_2024",
    "Financier Mois_AvanceTreso_2024",
    "Structure Nb_Benevoles",
    "Structure Nb_nvx_Benevoles_2025",
    "Structure Nb_Adherents",
    "Structure Nb_formes_TCAS_2025",
    "Structure Nb_formes_CRB_2025",
    "Structure Taux_formation_CRB",
    "Structure Nb_nvx_formes_CRB_2025",
    "Structure Nb_formateurs_CRB_2025",
    "Dispositifs_d_urgence Structures_menant_activite_TCAU",
    "Dispositifs_d_urgence Structures_menant_activite_PSP",
    "Dispositifs_d_urgence Structures_menant_activite_GQS",
    "Dispositifs_d_urgence Nb_conventions_prefecture",
    "Dispositifs_d_urgence Nb_conventions_operateurs",
    "Dispositifs_d_urgence Nb_agrements",
    "Dispositifs_d_urgence Nb_declenchements",
    "Dispositifs_d_urgence Nb_operations",
    "Dispositifs_d_urgence Nb_personnes_prises_charge",
    "Dispositifs_d_urgence Nb_lots_CAI",
    "Dispositifs_d_urgence Nb_lots_CHU",
    "Dispositifs_d_urgence Nb_lots_CMCC",
    "Dispositifs_d_urgence Utilisation_RedCall",
    "Dispositifs_d_urgence Utilisation_Minutis",
    "Dispositifs_d_urgence Nb_exercices",
    "Dispositifs_d_urgence PST",
    "Dispositifs_d_urgence Nb_formes_TCAU_2025",
    "Dispositifs_d_urgence Nb_formes_TCEO_2025",
    "Dispositifs_d_urgence Nb_formes_IPSP_2025",
    "Dispositifs_d_urgence Nb_formes_IRR_2025",
    "Dispositifs_d_urgence Nb_formes_GQS_2025",
    "Dispositifs_d_urgence Taux_formation_TCAU_2025",
    "Dispositifs_d_urgence Taux_formation_IPSP_2025",
    "Dispositifs_d_urgence Taux_formation_GQS_2025",
    "Dispositifs_d_urgence Taux_formation_TCEO_2025",
    "Dispositifs_d_urgence Taux_formation_IRR_2025",
    "Formation_grand_public Nb_FPSC",
    "Formation_grand_public Structures_menant_activite",
    "Formation_grand_public Produits_2025",
    "Dispositifs_d_urgence Nb_formes_PSP_2025",
    "Formation_grand_public Nb_sessions_PSE",
    "Formation_grand_public Nb_sessions_CI",
    "Formation_grand_public Nb_sessions_FPSE",
    "Formation_grand_public Nb_formes_PSC_2025",
    "Formation_grand_public Nb_sessions_PSC_2025",
    "Formation_grand_public Nb_FPSC",
    "Formation_grand_public Nb_formes_GQS_2025",
    "Formation_grand_public Nb_sessions_GQS_2025",
    "Formation_grand_public Nb_AGQS",
    "Formation_grand_public Nb_formes_IPSEN_2025",
    "Formation_grand_public Nb_sessions_IPSEN_2025",
    "Formation_grand_public Nb_FIPSEN",
    "Formation_grand_public Nb_formes_IPS_2025",
    "Formation_grand_public Nb_sessions_IPS_2025",
    "Formation_grand_public Nb_formes_PREVIC_2025",
    "Formation_grand_public Nb_sessions_PREVIC_2025",
    "Formation_grand_public Activite_Conso_Etat",
    "Formation_grand_public Activite_Conso_Non_Etat",
    "OCR Structures_menant_activite",
    "OCR Nb_deployees",
    "OCR Nb_referents",
    "nb_Maraude_Pegass",
    "Maraude Nb_maraudes_SIGMA",
    "Maraudes Structures_menant_activite",
    "Maraude Nb_benevoles_actifs",
    "Maraude Nb_benevoles_actifs_formes",
    "Maraude Nb_SOLIDAR",
    "Maraude Nb_SOLIDAR2020",
    "Maraude Nb_contacts",
    "Maraude Nb_personnes_rencontrees",
    "Secours Produits_DPS_2025",
    "Secours Structures_menant_activite",
    "Secours Nb_DPS_2025",
    "Secours Nb_agrements_DPS_2025",
    "Secours Taux_IS_actifs",
    "Secours Nb_PAPS_2025",
    "Secours Nb_DPS_PE_2025",
    "Secours Nb_DPS_ME_2025",
    "Secours Nb_DPS_GE_2025",
    "Secours Nb_PSE1",
    "Secours Nb_PSE2",
    "Secours Nb_CI",
    "Secours Taux_recy26_PSE1",
    "Secours Taux_recy26_PSE2",
    "Secours Taux_recy26_CI",
    "Secours Taux_ren25_PSE1",
    "Secours Taux_ren25_PSE2",
    "Secours Taux_ren25_CI",
    "Secours Nb_sessions_PSE",
    "Secours Nb_sessions_CI",
    "Secours Nb_sessions_FPSE",
    "AEO Structures_menant_activite",
    "AEO Structure_activite_fixe",
    "AEO Structure_activite_mobile",
    "AEO Nb_benevoles_actifs",
    "AEO Nb_responsables",
    "AEO Nb_AAD",
    "AEO Nb_FAAD",
    "AEO Nb_PA_AEO_AAD",
    "AEO Nb_personnes_domiciliees_crf",
    "AEO Nb_PA_dispos_mobiles",
    "Aide_alimentaire Nb_U2A",
    "Aide_alimentaire Nb_Centre_distribution_alimentaire",
    "Aide_alimentaire Nb_epiceries_sociales",
    "Aide_alimentaire Nb_crsr",
    "Textile Nb_dispositifs",
    "Textile Produit_2025",
    "Textile Resultat_2025"
  ]

  mask = df_ref_structure['n_structure'].to_list()

  print("TRAITEMENT DES INDICATEURS POUR TOUTES LES STRUCTURES")
  print('')
  for i,df in enumerate(liste_df_a_fusionner_toutes_structures):

    # Transformation des Series en DataFrame
    if type(liste_df_a_fusionner_toutes_structures[i]) != type(df_ref_structure):
      liste_df_a_fusionner_toutes_structures[i] = liste_df_a_fusionner_toutes_structures[i].to_frame()
    if len(liste_df_a_fusionner_toutes_structures[i].columns) < 2:
      liste_df_a_fusionner_toutes_structures[i] = liste_df_a_fusionner_toutes_structures[i].reset_index()

    # Uniformisation des types pour la clé n_structure
    
    if liste_df_a_fusionner_toutes_structures[i]['n_structure'].dtype != df_ref_structure['n_structure'].dtype:
      liste_df_a_fusionner_toutes_structures[i]['n_structure'] = liste_df_a_fusionner_toutes_structures[i]['n_structure'].astype(int)
    cleaned_dfs = []

    # Colonnes à supprimer
    cols_to_drop = [col for col in liste_df_a_fusionner_toutes_structures[i].columns if col not in colonnes_indicateurs]

    if cols_to_drop:
        print(f"🧹 DataFrame {i} : suppression des colonnes {cols_to_drop}")

    df_clean = liste_df_a_fusionner_toutes_structures[i].drop(columns=cols_to_drop)

    liste_df_a_fusionner_toutes_structures[i] = df_clean

    # Filtre des n_structure
    
    liste_df_a_fusionner_toutes_structures[i] = liste_df_a_fusionner_toutes_structures[i][liste_df_a_fusionner_toutes_structures[i]['n_structure'].isin(mask)]
  duplicates = find_duplicates_in_list_of_dfs(liste_df_a_fusionner_toutes_structures, column='n_structure')

  all_data  = merge_left_on_df1(df_ref_structure, liste_df_a_fusionner_toutes_structures, on = 'n_structure')

  
  print("TRAITEMENT DES INDICATEURS POUR LES DTs")
  print('')
  for i,df in enumerate(liste_df_a_fusionner_DT):

    # Transformation des Series en DataFrame
    if type(liste_df_a_fusionner_DT[i]) != type(df_ref_structure):
      liste_df_a_fusionner_DT[i] = liste_df_a_fusionner_DT[i].to_frame()
    if len(liste_df_a_fusionner_DT[i].columns) < 2:
      liste_df_a_fusionner_DT[i] = liste_df_a_fusionner_DT[i].reset_index()

    # Uniformisation des types pour la clé n_structure
    if 'n_structure' not in liste_df_a_fusionner_DT[i].columns:
      if 'DT_de_rattachement' in liste_df_a_fusionner_DT[i].columns:
        liste_df_a_fusionner_DT[i] = liste_df_a_fusionner_DT[i].rename(columns={'DT_de_rattachement': 'n_structure'})

    # Garder seulement les nombres
    if liste_df_a_fusionner_DT[i]['n_structure'].dtype == 'object':
      contient_lettres = liste_df_a_fusionner_DT[i]['n_structure'].astype(str).str.contains(r'[A-Za-z]', na=False).any()
      if contient_lettres:
        liste_df_a_fusionner_DT[i]['n_structure'] = liste_df_a_fusionner_DT[i]['n_structure'].apply(keep_integer).astype(int)
    
    if liste_df_a_fusionner_DT[i]['n_structure'].dtype != df_ref_structure['n_structure'].dtype:
      liste_df_a_fusionner_DT[i]['n_structure'] = liste_df_a_fusionner_DT[i]['n_structure'].astype(int)


    # Colonnes à supprimer
    cols_to_drop = [col for col in liste_df_a_fusionner_DT[i].columns if col not in colonnes_indicateurs]

    if cols_to_drop:
        print(f"🧹 DataFrame {i} : suppression des colonnes {cols_to_drop}")

    df_clean = liste_df_a_fusionner_DT[i].drop(columns=cols_to_drop)

   
    liste_df_a_fusionner_DT[i] = df_clean

    # Filtre des n_structure
    liste_df_a_fusionner_DT[i] = liste_df_a_fusionner_DT[i][liste_df_a_fusionner_DT[i]['n_structure'].isin(mask)]

  duplicates = find_duplicates_in_list_of_dfs(liste_df_a_fusionner_DT, column='n_structure')
  all_data_DT  = merge_left_on_df1(df_ref_structure_DT, liste_df_a_fusionner_DT, on = 'n_structure')
  


  return all_data, all_data_DT, liste_df_a_fusionner_toutes_structures, liste_df_a_fusionner_DT


def ajouter_colonnes_taux(df: pd.DataFrame, denominateur: str) -> pd.DataFrame:
    """
    Ajoute des colonnes calculées comme (colonne / denominateur).

    Les noms des nouvelles colonnes sont définis en dur dans la fonction.
    """
    colonnes = ["Dispositifs_d_urgence Nb_formes_TCAU_2025","Dispositifs_d_urgence Nb_formes_TCEO_2025",
    "Dispositifs_d_urgence Nb_formes_PSP_2025", "Dispositifs_d_urgence Nb_formes_IRR_2025", "Dispositifs_d_urgence Nb_formes_GQS_2025",
    "Structure Nb_formes_CRB_2025"]
    # ⚠️ noms hardcodés (modifie-les ici selon ton besoin)
    mapping_noms = {
        "Dispositifs_d_urgence Nb_formes_TCAU_2025": "Dispositifs_d_urgence Taux_formation_TCAU_2025",
        "Dispositifs_d_urgence Nb_formes_TCEO_2025": "Dispositifs_d_urgence Taux_formation_TCEO_2025",
        "Dispositifs_d_urgence Nb_formes_PSP_2025": "Dispositifs_d_urgence Taux_formation_PSP_2025",
        "Dispositifs_d_urgence Nb_formes_IRR_2025" : "Dispositifs_d_urgence Taux_formation_IRR_2025",
        "Dispositifs_d_urgence Nb_formes_GQS_2025" : "Dispositifs_d_urgence Taux_formation_GQS_2025",
        "Structure Nb_formes_CRB_2025" : "Structure Taux_formation_CRB"
    }

    for col in colonnes:
        if col not in df.columns:
            raise ValueError(f"Colonne absente du dataframe : {col}")
        if denominateur not in df.columns:
            raise ValueError(f"Colonne denominateur absente : {denominateur}")

        if col not in mapping_noms:
            raise ValueError(f"Aucun nom hardcodé prévu pour {col}")

        nouveau_nom = mapping_noms[col]
        df[nouveau_nom] = df[col] / df[denominateur]

    return df

def ajouter_colonne_somme(df: pd.DataFrame, col1: str, col2: str) -> pd.DataFrame:
  
    # nom hardcodé de la nouvelle colonne
    nom_nouvelle_colonne = "AEO Nb_PA_AEO_AAD"
    
    df[nom_nouvelle_colonne] = df[col1] + df[col2]
    return df

def vision_conso(df_alldata, df_alldata_DT):
  # sélection des colonnes pour vision consolidée FPG

  formations_certifiantes = [
      'Formation_grand_public Nb_formes_PSC_2025',
      'Formation_grand_public Nb_formes_GQS_2025',
      'Formation_grand_public Nb_sessions_PSC_2025',
      'Formation_grand_public Nb_sessions_GQS_2025'
  ]

  df_alldata['Formation_grand_public Activite_Conso_Etat'] = (
      df_alldata[formations_certifiantes]
      .fillna(0)
      .sum(axis=1)
      .gt(0)
      .map({True: 'Action menée', False: 'Non menée'})
  )



  formations_non_certifiantes = [
      'Formation_grand_public Nb_formes_IPSEN_2025',
      'Formation_grand_public Nb_formes_IPS_2025',
      'Formation_grand_public Nb_formes_PREVIC_2025',
      'Formation_grand_public Nb_sessions_IPSEN_2025',
      'Formation_grand_public Nb_sessions_IPS_2025',
      'Formation_grand_public Nb_sessions_PREVIC_2025'
  ]

  df_alldata['Formation_grand_public Activite_Conso_Non_Etat'] = (
      df_alldata[formations_non_certifiantes]
      .fillna(0)
      .sum(axis=1)
      .gt(0)
      .map({True: 'Action menée', False: 'Non menée'})
  )



  # df_alldata['vision_territoriale_activite_DPS'] = (
  #     df_alldata['Secours Nb_DPS_2025']
  #     .fillna(0)
  #     .sum(axis=1)
  #     .gt(0)
  #     .map({True: 'Action menée', False: 'Non menée'})
  # )


  formations_secours = [
      'Secours Nb_PSE1',
      'Secours Nb_PSE2',
      'Secours Nb_CI'
  ]

  # df_alldata['vision_territoriale_formation_DPS'] = (
  #     df_alldata['formations_secours']
  #     .fillna(0)
  #     .sum(axis=1)
  #     .gt(0)
  #     .map({True: 'Action menée', False: 'Non menée'})
  # )




  # Ajout du 'Action non menée' sur les autres colonnes

  colonnes_non_menee = [
      'OCR Nb_deployees',
      'Maraude Nb_maraudes_SIGMA',
      # 'Secours Nb_DPS_2025',
      'Textile Nb_dispositifs',
      'Aide_alimentaire Nb_U2A'
  ]

  df_alldata[colonnes_non_menee] = df_alldata[colonnes_non_menee].astype(str)
  df_alldata[colonnes_non_menee] = (
      df_alldata[colonnes_non_menee]
      .fillna('Non menée')
  )



  # Nb de structures menant l'activité

  colonnes_nb_structure = [
    (('OCR Nb_deployees',), 'OCR Structures_menant_activite'),
    (('Secours Nb_DPS_2025','Secours Nb_PAPS_2025','Secours Nb_DPS_PE_2025','Secours Nb_DPS_ME_2025','Secours Nb_DPS_GE_2025'), 'Secours Structures_menant_activite'),
    (('Secours Nb_PSE1','Secours Nb_PSE2','Secours Nb_CI'), 'Secours Structures_menant_activite_formes'),
    (('Formation_grand_public Nb_sessions_PSE','Formation_grand_public Nb_sessions_CI','Formation_grand_public Nb_sessions_FPSE'), 'Secours Structures_menant_activite_sessions'),
    (('nb_Maraude_Pegass',), 'Maraudes Structures_menant_activite'),
    (('Dispositifs_d_urgence Nb_formes_TCAU_2025',), 'Dispositifs_d_urgence Structures_menant_activite_TCAU'),
    (('Dispositifs_d_urgence Nb_formes_PSP_2025',), 'Dispositifs_d_urgence Structures_menant_activite_PSP'),
    (('Dispositifs_d_urgence Nb_formes_GQS_2025',), 'Dispositifs_d_urgence Structures_menant_activite_GQS'),

  ]
  colonnes_actions = [col_output for _, col_output in colonnes_nb_structure]

  for cols_input, col_output in colonnes_nb_structure:
      
      # garantir un tuple même si une seule colonne
      if isinstance(cols_input, str):
          cols_input = (cols_input,)
      
      # conversion numérique
      df_alldata[list(cols_input)] = df_alldata[list(cols_input)].apply(
          pd.to_numeric, errors='coerce'
      )
      
      # 1 si au moins une valeur > 0
      df_alldata[col_output] = (df_alldata[list(cols_input)] > 0).any(axis=1).astype(int)

  df_grouped = (
    df_alldata[['DT_de_rattachement'] + colonnes_actions]
    .groupby('DT_de_rattachement')[colonnes_actions]
    .sum()
    .reset_index()
  )



  for _, col_output in colonnes_nb_structure:
    df_alldata[col_output] = df_alldata[col_output].map({
        1: 'Action menée',
        0: 'Action non menée'
    })
 

  df_grouped = df_grouped[colonnes_actions + ['DT_de_rattachement']]

  df_alldata_DT = pd.merge(df_alldata_DT, df_grouped, on='DT_de_rattachement', how='left')

  #Partie structure menant activite AEO

  df_alldata["AEO Structure_activite_mobile"] = df_alldata["AEO Structure_activite_mobile"].astype(object)
  df_alldata.loc[df_alldata["AEO Structure_activite_mobile"].notna(), ["AEO Structure_activite_mobile"]] = "Activité AEO/AAD en dispositif mobile"
  
  
  fixe = df_alldata["AEO Structure_activite_fixe"]
  mobile = df_alldata["AEO Structure_activite_mobile"]
  
  df_alldata["AEO Structures_menant_activite"] = (
      fixe.fillna("").astype(str).str.strip()
      + " | " +
      mobile.fillna("").astype(str).str.strip()
  ).str.strip(" |")
  
  df_alldata["AEO Structures_menant_activite"] =df_alldata["AEO Structures_menant_activite"].replace('Activités AEO/AAD menée en fixe | Activité AEO/AAD en dispositif mobile',"Activité AEO/AAD en site fixe et en dispositif mobile")
  
  df_alldata["AEO Structures_menant_activite"] =df_alldata["AEO Structures_menant_activite"].replace('Activités AEO/AAD menée en fixe',"Activité AEO/AAD en site fixe")
  
  df_alldata["AEO Structures_menant_activite"] =df_alldata["AEO Structures_menant_activite"].replace('','Activité AEO/AAD non menée')

  df_grouped = (
      df_alldata[['DT_de_rattachement',"AEO Structures_menant_activite"]]
      .groupby('DT_de_rattachement')["AEO Structures_menant_activite"]
      .apply(lambda x: (x != "Activité AEO/AAD non menée").sum())
      .reset_index()
  )

  df_alldata_DT = pd.merge(df_alldata_DT, df_grouped, on='DT_de_rattachement', how='left')  




  # Structures menant activité

  df_alldata['Formation_grand_public Activite_Conso_Etat'] = df_alldata['Formation_grand_public Activite_Conso_Etat'].fillna('')
  df_alldata['Formation_grand_public Activite_Conso_Non_Etat'] = df_alldata['Formation_grand_public Activite_Conso_Non_Etat'].fillna('')
  df_alldata['Formation_grand_public Structures_menant_activite'] = df_alldata[['Formation_grand_public Activite_Conso_Etat', 'Formation_grand_public Activite_Conso_Non_Etat']].apply(
      lambda row: 1
      if (row['Formation_grand_public Activite_Conso_Etat'] == "Action menée") or (row['Formation_grand_public Activite_Conso_Non_Etat'] == "Action menée")
      else 0 ,
      axis=1
  )

  df_grouped = (
      df_alldata[['DT_de_rattachement','Formation_grand_public Structures_menant_activite']]
      .groupby('DT_de_rattachement')['Formation_grand_public Structures_menant_activite']
      .sum()
      .reset_index()
  )
  df_alldata['Formation_grand_public Structures_menant_activite'] = df_alldata['Formation_grand_public Structures_menant_activite'].map({1: 'Action menée', 0: 'Action non menée'})

  df_alldata_DT = pd.merge(df_alldata_DT, df_grouped, on='DT_de_rattachement', how='left')  

  return df_alldata, df_alldata_DT
  

