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


import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *


def clean_OCR(df_OCR):
    cols_OCR = [
        "Année",
        "Statut",
        "Nom du Département",
        "Structure CRf\n(Ville)",
        "Nom Commune de l'établissement"
    ]


    df_OCR[cols_OCR] = df_OCR[cols_OCR].astype(str)


    df_OCR[["N° Département", "Nom du Département"]] = (
        df_OCR["Nom du Département"]
        .str.strip()
        .str.split("-", n=1, expand=True)
    )


    df_OCR["N° Département"] = df_OCR["N° Département"].str.strip()
    df_OCR["Nom du Département"] = df_OCR["Nom du Département"].str.strip()


    return df_OCR


def clean_PST(df_PST):
    df_PST = df_PST.rename(columns={"PST constitué ": "PST constitué"})


    df_PST["N° Département"] = df_PST["Territoire"].str.extract(r"DT\s+(\d+)")
    df_PST["Nom structure DT"] = "DT " + df_PST["Territoire"].str.extract(r"-\s*(.+)")


    cols_PST = [
        "Territoire",
        "PST constitué",
        "N° Département",
        "Nom structure DT"
    ]


    df_PST[cols_PST] = df_PST[cols_PST].astype(str)


    return df_PST


def clean_declenchement(df_declenchement):
    df = df_declenchement.drop(df_declenchement.index[0]).copy()


    df.rename(
        columns={
            'COUNTA of Catégorie': 'Département',
            'Catégorie': 'Etablissements',
            'Unnamed: 2': 'Exercice',
            'Unnamed: 3': 'Fonctionnement',
            'Unnamed: 4': 'Opérations',
            'Unnamed: 5': 'Grand Total'
        },
        inplace=True
    )


    df[['Grand Total', 'Exercice']] = df[['Grand Total', 'Exercice']].fillna(0)


    df["nb_declenchements"] = df["Grand Total"] - df["Exercice"]


    df[["n_dept", "DT"]] = df["Département"].str.split(" - ", expand=True)
    df["DT"] = "DT " + df["DT"]


    return df


def clean_redcall(df_redcall):
    df = df_redcall.drop(columns=["Type", "Coûts", "Devise"])


    cols_to_sum = [
        "Déclenchements",
        "Communications",
        "Messages",
        "Questions",
        "Réponses",
        "Erreurs"
    ]


    df_grouped = (
        df
        .groupby("Nom de la structure", as_index=False)[cols_to_sum]
        .sum()
    )


    df_grouped["Total"] = df_grouped[
        ["Communications", "Messages", "Questions"]
    ].sum(axis=1)


    df_grouped["Utilisation_Redcall"] = (
        df_grouped["Total"]
        .gt(0)
        .map({True: "Oui", False: "Non"})
    )


    return df_grouped


def clean_CAICHUCMCC(df_CAICHUCMCC):
    first_valid_row = df_CAICHUCMCC.dropna(how="all").index[0]


    df_CAICHUCMCC.columns = df_CAICHUCMCC.loc[first_valid_row]
    df_CAICHUCMCC = (
        df_CAICHUCMCC
        .loc[first_valid_row + 1:]
        .reset_index(drop=True)
    )


    df = df_CAICHUCMCC[
        ['Dépt', 'Région', 'Département', 'CAI 2023', 'CHU 2023', 'Lots CMCC 2023']
    ]


    df["Département"] = df["Département"].str.replace(
        "DELEGATION TERRITORIALE",
        "DT",
        regex=False
    )


    codes_a_supprimer = [
        "NAT", "ARA", "BFC", "BRET", "CVDL", "GE",
        "HDF", "IDF", "NAQ", "NORM", "OCC",
        "PACAC", "PDLL", "OM"
    ]


    df = df[~df['Dépt'].isin(codes_a_supprimer)]


    df.loc[df['Dépt'] == 978, 'Département'] = 'DT DE ST MARTIN'


    return df


def clean_conventions(df_conventions):
    df = df_conventions.rename(columns = {'Préfecture': 'Prefecture', 'Tripartite' : 'Tri partite'})
    df = df[
        [
            'DT Annuaire Opé',
            'Departement',
            'Prefecture',
            'Tri partite',
            'Recherche de personnes',
            'SDIS / BMPM / BSPP',
            'SNCF',
            'SAMU',
            'Gendarmerie',
            'CUMP',
            'Communes',
            'Autoroutes',
            'Autres'
        ]
    ]


    df["Departement"] = df["Departement"].str.replace(
        r"DELEGATION DEPARTEMENTALE|DELEGATION TERRITORIALE",
        "DT",
        regex=True
    )


    colonnes_oui_non = [
        'Prefecture',
        'Tri partite',
        'Recherche de personnes',
        'SDIS / BMPM / BSPP',
        'SNCF',
        'SAMU',
        'Gendarmerie',
        'CUMP',
        'Communes',
        'Autoroutes',
        'Autres'
    ]


    colonnes_conv_ope = colonnes_oui_non[1:]


    # df[colonnes_oui_non] = df[colonnes_oui_non].applymap(
    #     lambda x: x[-3:] if isinstance(x, str) else x
    # )


    df['Dispositifs_d_urgence Nb_conventions_operateurs'] = (
        df[colonnes_conv_ope]
        .apply(lambda row: (row == 'Oui').sum(), axis=1)
    )


    return df

def clean_raw_Textile(df_raw_Textile, df_ref_structure):
    # Filtre sur le statut
    df = df_raw_Textile[df_raw_Textile["statut"] == "A jour"]

    # Filtrer sur les bons dispositif
    print("Point d'apport possible : ",df["Type de point apport"].unique())
    df = df[df["Type de point apport"].isin(['Boutique - La Boutique','Vestiaire','Boutique  - Mobile', 'Boutique - Bébé','Boutique - Chez Henry','Boutique - Recylcerie / Meuble','La Boutique'])]
    df = df.rename(columns={'Code structure': 'n_structure'})

    _ , _ , _, df = apply_rattachement_successif(df_ref_structure, df, col = 'n_structure')

    
    return df

def clean_ProdResTextile(df_raw_ProdResTextile):
    df = df_raw_ProdResTextile.iloc[:-1]

    # Renommer les colonnes
    df.columns.values[0] = 'code_comptable'
    df.columns.values[1] = 'libelle'
    df.columns.values[22] = 'Textile Produit_2024'
    df.columns.values[24] = 'Textile Resultat_2024'

    # Conserver les lignes liées aux DT
    df = df[df['code_comptable'].str.contains("DD", na=False)]

# Extraire le département
    def extraire_et_nettoyer_code_departement(texte):
        code = texte[-3:] # Extraire les 3 derniers caractères
        code = code.lstrip('0') # Supprimer les zéros initiaux
        return code

    df['Code Département'] = df['code_comptable'].apply(extraire_et_nettoyer_code_departement)

    return df







def clean_indicateurs_DUO(df_conventions):
    df = df_conventions[
        [
            'DT Annuaire Opé',
            'Departement',
            "Nb opérations d'urgence",
            "Nombre de prises en charge lors de ces opérations d'urgence",
            'Recherche de personnes',
            'SDIS / BMPM / BSPP',
        ]
    ]

    df["Departement"] = df["Departement"].str.replace(
        r"DELEGATION DEPARTEMENTALE|DELEGATION TERRITORIALE",
        "DT",
        regex=True
    )

    return df


def clean_OCR_PST_DEC_RED_CAI_CONV(
    df_OCR,
    df_PST,
    df_declenchement,
    df_redcall,
    df_CAICHUCMCC,
    df_conventions,
    df_raw_Textile,
    df_raw_ProdResTextile,
    df_ref_structure
):
    df_OCR_clean = clean_OCR(df_OCR)
    df_PST_clean = clean_PST(df_PST)
    df_declenchement_clean = clean_declenchement(df_declenchement)
    df_redcall_clean = clean_redcall(df_redcall)
    df_CAICHUCMCC_clean = clean_CAICHUCMCC(df_CAICHUCMCC)
    df_conventions_clean = clean_conventions(df_conventions)
    df_raw_Textile = clean_raw_Textile(df_raw_Textile, df_ref_structure)
    df_raw_ProdResTextile = clean_ProdResTextile(df_raw_ProdResTextile)
    df_duo_clean = clean_indicateurs_DUO(df_conventions)

    return (
        df_OCR_clean,
        df_PST_clean,
        df_declenchement_clean,
        df_redcall_clean,
        df_CAICHUCMCC_clean,
        df_conventions_clean,
        df_raw_Textile,
        df_raw_ProdResTextile,
        df_duo_clean
    )




def indicateurs_OCR_nb_deployees(df_OCR, df_ref_structure):
    df = df_OCR.copy()


    df = df[df["Statut"].isin(["En cours", "Projet"])]
    df = df[df["Année"] == "2025-2026"]


    df = df[
        ["Année", "Statut", "Nom du Département", "N° Département", "Structure CRf\n(Ville)"]
    ]


    df = rapprochement_libelles(
        df_ref_structure,
        df,
        "Structure CRf\n(Ville)"
    )


    mask = df["n_structure"] == ""
    mapping_dict = (
        df_ref_structure[
            df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"
        ]
        .set_index("n_dept")["n_structure"]
        .to_dict()
    )


    df.loc[mask, "n_structure"] = df.loc[mask, "N° Département"].map(mapping_dict)


    df = df["n_structure"].value_counts().reset_index()
    df = df.rename(columns={"count": "OCR Nb_deployees"})


    return df


def indicateurs_PST(df_PST, df_ref_structure):
    df = df_PST.copy()


    df = df[
        ["Territoire", "PST constitué", "Nom structure DT", "N° Département"]
    ]


    df = rapprochement_libelles(
        df_ref_structure,
        df,
        "Nom structure DT"
    )


    mask = df["n_structure"].isna() | (df["n_structure"] == "")


    df["N° Département"] = df["N° Département"].astype(str)
    df_ref_structure["n_dept"] = df_ref_structure["n_dept"].astype(str)


    mapping_dict = (
        df_ref_structure[
            df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"
        ]
        .set_index("n_dept")["n_structure"]
        .to_dict()
    )


    df.loc[mask, "n_structure"] = df.loc[mask, "N° Département"].map(mapping_dict)


    df["PST constitué"] = (
        df["PST constitué"]
        .astype(str)
        .str.strip()
        .str.lower()
    )


    def statut_pst(valeur):
        if valeur == "oui":
            return "Oui"
        elif valeur == "en cours":
            return "En cours"
        else:
            return "Non"


    df["Dispositifs_d_urgence PST"] = df["PST constitué"].apply(statut_pst)


    df.loc[
        df["Territoire"] == "DT  42 - Loire",
        ["n_structure", "nom_structure"]
    ] = [47, "DT DE LA LOIRE"]


    return df


def indicateurs_declenchements(df_declenchement2, df_ref_structure):
    df = df_declenchement2.copy()


    df["DT"] = df["DT"].astype(str)
    df["n_dept"] = df["n_dept"].astype(str)


    df = rapprochement_libelles(df_ref_structure, df, "DT")


    mask = df["n_structure"] == ""
    mapping_dict = (
        df_ref_structure[
            df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"
        ]
        .set_index("n_dept")["n_structure"]
        .to_dict()
    )


    df.loc[mask, "n_structure"] = df.loc[mask, "n_dept"].map(mapping_dict)


    df = df.dropna(subset=["n_structure"])


    df.loc[
        df["Département"] == "42 - Loire",
        ["n_structure", "nom_structure"]
    ] = [47, "DT DE LA LOIRE"]


    df = df.rename(
        columns={"nb_declenchements": "Dispositifs_d_urgence Nb_declenchements"}
    )


    return df


def indicateurs_redcall(df_RC_grouped, df_ref_structure):
    df = df_RC_grouped[
        ["Nom de la structure", "Utilisation_Redcall"]
    ]
    df = df[~df["Nom de la structure"].isin(["ANNUAIRE NATIONAL", "REGION OCCITANIE"])]
    df['Nom de la structure'] = df['Nom de la structure'].replace('UNITE LOCALE DU BRIONNAIS', 'UNITE LOCALE DE LA CLAYETTE - MARCIGNY')
    df = df[df['Nom de la structure'] != 'INSTANCES NATIONALES']
    df["Utilisation_Redcall"] = df["Utilisation_Redcall"].astype(str)
    df = rapprochement_libelles(df_ref_structure, df, "Nom de la structure")

    _ , _ , _, df = apply_rattachement_successif(df_ref_structure, df, col = 'n_structure')

    df = df.groupby("n_structure", as_index=False).agg(
        Utilisation_Redcall=("Utilisation_Redcall", lambda s: "Oui" if (s == "Oui").any() else "")
    )

    df = df.rename(columns = {"Utilisation_Redcall" : "Dispositifs_d_urgence Utilisation_RedCall"})

    return df


def indicateurs_CAICHUCMCC(df_CAICHUCMCC2, df_ref_structure):
    df = rapprochement_libelles(
        df_ref_structure,
        df_CAICHUCMCC2,
        "Département"
    )


    df = df.rename(
        columns={
            "CAI 2023": "Dispositifs_d_urgence Nb_lots_CAI",
            "CHU 2023": "Dispositifs_d_urgence Nb_lots_CHU",
            "Lots CMCC 2023": "Dispositifs_d_urgence Nb_lots_CMCC"
        }
    )


    return df


def indicateurs_conventions(df_conventions, df_ref_structure):
    df = df_conventions[
        ["Departement", "Prefecture", "Dispositifs_d_urgence Nb_conventions_operateurs"]
    ].copy()


    df = rapprochement_libelles(
        df_ref_structure,
        df,
        "Departement"
    )


    df = df.rename(
        columns={
            "Prefecture": "Dispositifs_d_urgence Nb_conventions_prefecture"
        }
    )


    return df

def indicateurs_raw_Textile(df_raw_Textile):
   # Agréger sur le Code structure
   df = df_raw_Textile.groupby("n_structure").size().reset_index(name="Textile Nb_dispositifs")

   return df

def indicateurs_ProdResTextile(df_raw_ProdResTextile, df_ref_structure):
    # Mapping sur le département
    mapping_dict = df_ref_structure[df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"].set_index('n_dept')['n_structure'].to_dict()
    df_raw_ProdResTextile['n_structure'] = df_raw_ProdResTextile['Code Département'].map(mapping_dict)
    verifier_mapping(df_raw_ProdResTextile, "n_structure", "libelle" ,df_ref_structure)

# Conservation des colonnes utiles
    df = df_raw_ProdResTextile[["n_structure","Textile Produit_2024", "Textile Resultat_2024"]]

# Suppression des espaces et "-"
    df['Textile Produit_2024'] = df['Textile Produit_2024'].str.replace(r"\s+", "", regex=True)
    df['Textile Produit_2024'] = df['Textile Produit_2024'].str.replace("-", "")
    df['Textile Resultat_2024'] = df['Textile Resultat_2024'].str.replace(r"\s+", "", regex=True)
    df['Textile Resultat_2024'] = df['Textile Resultat_2024'].str.replace("-", "")
    df = df.rename(columns = {'Textile Produit_2024' : 'Textile Produit_2025', 'Textile Resultat_2024' : 'Textile Resultat_2025'})

    return df



def indicateurs_DUO(df_conventions, df_ref_structure):
    df = df_conventions[
        ["Departement", "Nb opérations d'urgence", "Nombre de prises en charge lors de ces opérations d'urgence",]
    ].copy()

    df = rapprochement_libelles(
        df_ref_structure,
        df,
        "Departement"
    )

    df = df.rename(
        columns={
            "Nb opérations d'urgence": "Dispositifs_d_urgence Nb_operations",
            "Nombre de prises en charge lors de ces opérations d'urgence": "Dispositifs_d_urgence Nb_personnes_prises_charge",
        }
    )

    return df

def indicateurs_OCR_PST_DEC_RED_CAI_CONV(
    df_OCR,
    df_PST,
    df_declenchement2,
    df_RC_grouped,
    df_CAICHUCMCC2,
    df_conventions,
    df_raw_Textile,
    df_raw_ProdResTextile,
    df_DUO_clean,
    df_ref_structure
):
    df_OCR_Nb_deployees = indicateurs_OCR_nb_deployees(df_OCR, df_ref_structure)
    df_Dispositifs_d_urgence_PST = indicateurs_PST(df_PST, df_ref_structure)
    df_declenchement3 = indicateurs_declenchements(df_declenchement2, df_ref_structure)
    df_redcall2 = indicateurs_redcall(df_RC_grouped, df_ref_structure)
    df_CAICHUCMCC_VF = indicateurs_CAICHUCMCC(df_CAICHUCMCC2, df_ref_structure)
    df_conventions2 = indicateurs_conventions(df_conventions, df_ref_structure)
    df_raw_Textile = indicateurs_raw_Textile(df_raw_Textile)
    df_raw_ProdResTextile = indicateurs_ProdResTextile(df_raw_ProdResTextile , df_ref_structure)

    df_DUO = indicateurs_DUO(df_conventions, df_ref_structure)

    return (
        df_OCR_Nb_deployees,
        df_Dispositifs_d_urgence_PST,
        df_declenchement3,
        df_redcall2,
        df_CAICHUCMCC_VF,
        df_conventions2,
        df_raw_Textile,
        df_raw_ProdResTextile,
        df_DUO
    )




def indicateurs_OCR_DT(df_OCR_Nb_deployees, rattachement_court):
    df_OCR_Nb_deployees['n_structure'] = df_OCR_Nb_deployees['n_structure'].astype(int)
    # Merge données avec rattachement_court
    OCR_Nb_deployees = pd.merge(
    df_OCR_Nb_deployees,
    rattachement_court,
    on="n_structure",
    how="left"
    )




    # Groupby sur DT_de_rattachement
    Nb_OCR_DT = (OCR_Nb_deployees.groupby('DT_de_rattachement')['OCR Nb_deployees'].sum())
    return Nb_OCR_DT






def indicateurs_redcall_DT(df_redcall2, rattachement_court):
    df_redcall2['n_structure'] = df_redcall2['n_structure'].astype(int)
    # Merge données avec rattachement_court
    redcall = pd.merge(df_redcall2, rattachement_court, on="n_structure", how="left")


    # Groupby sur DT_de_rattachement
    RedCall_DT = (redcall.groupby('DT_de_rattachement')['Dispositifs_d_urgence Utilisation_RedCall'].max())
    return RedCall_DT






def OCR_RedCall_DT(df_OCR_Nb_deployees, df_redcall2, rattachement_court):
    Nb_OCR_DT = indicateurs_OCR_DT(df_OCR_Nb_deployees, rattachement_court)
    RedCall_DT = indicateurs_redcall_DT(df_redcall2, rattachement_court)


    return (
        Nb_OCR_DT,
        RedCall_DT,
    )

def Textile_DT(df_raw_Textile, rattachement_court):
    df_raw_Textile['n_structure'] = df_raw_Textile['n_structure'].astype('float64')
    # Merge données avec rattachement_court
    textile = pd.merge(df_raw_Textile, rattachement_court, on="n_structure", how="left")

    # Groupby sur DT_de_rattachement
    Textile_DT = (textile.groupby('DT_de_rattachement')['Textile Nb_dispositifs'].sum())
    return Textile_DT


def Textile_financier_DT(df_raw_ProdResTextile, rattachement_court):
    df_raw_ProdResTextile['n_structure'] = df_raw_ProdResTextile['n_structure'].astype('float64')
    # Merge données avec rattachement_court
    textile_financier = pd.merge(df_raw_ProdResTextile, rattachement_court, left_on="n_structure", right_on="n_structure", how="left")

    # Groupby sur DT_de_rattachement
    Textile_financier__DT = (
    textile_financier
        .groupby('DT_de_rattachement')[['Textile Produit_2025', 'Textile Resultat_2025']]
        .sum()
        .reset_index()
    )

    return Textile_financier__DT



def TEXTILE_DT(df_raw_Textile, df_raw_ProdResTextile, rattachement_court):
    df_Textile_DT = Textile_DT(df_raw_Textile, rattachement_court)
    df_Textile_financier__DT = Textile_financier_DT(df_raw_ProdResTextile, rattachement_court)


    return (
        df_Textile_DT,
        df_Textile_financier__DT,
    )

def verif_textile(df_raw_Textile_c, df_raw_ProdResTextile_c, df_raw_Textile, df_Textile_DT,df_raw_ProdResTextile, df_Textile_financier_DT, df_ref_structure,rattachement_court):
  df_t = df_raw_Textile_c[df_raw_Textile_c["statut"] == "A jour"]
  df_t = df_t[df_t["Type de point apport"].isin(['Boutique - La Boutique','Vestiaire','Boutique  - Mobile', 'Boutique - Bébé','Boutique - Chez Henry','Boutique - Recylcerie / Meuble','La Boutique'])]



  if df_Textile_DT.reset_index()['Textile Nb_dispositifs'].sum() == df_t.shape[0]:
    print('✅ df_Textile_DT est bien calculé (suomme de l indicateur == au nombre de lignes des données)')
  else:
    print('❌ df_Textile_DT n\'est pas bien calculé (suomme de l indicateur != au nombre de lignes des données), différence :', df_Textile_DT.reset_index()['Textile Nb_dispositifs'].sum() - df_raw_Textile_c.shape[0])

  if df_raw_Textile['Textile Nb_dispositifs'].sum() == df_t.shape[0]:
    print('✅ df_Textile_DT est bien calculé (suomme de l indicateur == au nombre de lignes des données)')
  else:
    print('❌ df_Textile_DT n\'est pas bien calculé (suomme de l indicateur != au nombre de lignes des données), différence :', df_Textile_DT.reset_index()['Textile Nb_dispositifs'].sum() - df_raw_Textile_c.shape[0])

  verifier_colonne_structure(df_raw_Textile, "n_structure", df_ref_structure)
  verifier_colonne_structure(df_raw_ProdResTextile, "n_structure", df_ref_structure)
  verifier_colonne_structure(df_Textile_DT.reset_index(), "DT_de_rattachement", rattachement_court)
  verifier_colonne_structure(df_Textile_financier_DT, "DT_de_rattachement", rattachement_court)


