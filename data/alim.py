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

from google.auth import default
import unicodedata
import re
import torch
from sentence_transformers import SentenceTransformer, util
import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *

### dans la section alim du code,, le dossier est ajouté mais pas l'appel à cette fonction et le return pour les 4 indicateurs alim et leur déclinaisoon DT, il n'y a pas de merge de ces indicateurs
## récupération des données
def clean_alim(df_alim):
  df_alim=df_alim[["Dispositif","Code U2A","Stucture rattachement",'N° structure']]

  ## préparation BDD alim
  if 'Code U2A' in df_alim.columns:
    # Identifier les doublons dans la colonne 'Code U2A'
    duplicates = df_alim[df_alim['Code U2A'].duplicated(keep=False)]

  #   # Compter le nombre de doublons
  #   num_duplicates = duplicates.shape[0]

  #   if num_duplicates > 0:
  #         print(f"Il y a {num_duplicates} lignes avec des doublons dans la colonne 'Code U2A'.")
  #         print("Voici les lignes en doublon (affichant toutes les occurrences des valeurs dupliquées) :")
  #         display(duplicates.sort_values(by='Code U2A'))
  #   else:
  #         print("Aucun doublon trouvé dans la colonne 'Code U2A'.")
  # else:
  #       print("La colonne 'Code U2A' n'existe pas dans le DataFrame df_alim.")
 
  # Création d'une base de données sans doublons
  df_alim_sans_doublons =df_alim.drop_duplicates(subset=['Code U2A'], keep='first')
  # print(f"Taille du DataFrame après suppression des doublons : {df_alim_sans_doublons.shape}")
  df_alim_sans_doublons = df_alim_sans_doublons.rename(columns={"N° structure": "n_structure"})
  # Conversion de la colonne n_structure en string pour la cohérence avec df_ref_structure
  df_alim_sans_doublons['n_structure'] = df_alim_sans_doublons['n_structure'].astype(str)
  # Supprimer le '.0' des chaînes si elles proviennent de nombres flottants
  df_alim_sans_doublons['n_structure'] = df_alim_sans_doublons['n_structure'].apply(lambda x: x[:-2] if x.endswith('.0') else x)
  df_alim_sans_doublons['n_structure'] = df_alim_sans_doublons['n_structure'].astype(int)

  return df_alim_sans_doublons

def indicateurs_alim(df_alim_sans_doublons, df_ref_structure):
    # U2A
  # if 'Dispositif' in df_alim_sans_doublons.columns:
  #     print("Nombre d'occurrences pour chaque type de 'Dispositif':")
  #     display(df_alim_sans_doublons['Dispositif'].value_counts())
  # else:
  #     print("La colonne 'Dispositif' n'existe pas dans le DataFrame df_alim_sans_doublons.")
  
  df_alim_U2A_sans_doublons = df_alim_sans_doublons.groupby("n_structure").size().reset_index(name="Aide_alimentaire Nb_U2A")

  # Epicerie sociale
  df_alim_epicerie_sociale= df_alim_sans_doublons[df_alim_sans_doublons['Dispositif'] == 'Epicerie sociale']
  df_alim_epicerie_sociale.shape[0]
  df_alim_epicerie_sociale = df_alim_epicerie_sociale.groupby("n_structure").size().reset_index(name="Aide_alimentaire Nb_epiceries_sociales")

  # Accueil Alimentaire
  df_alim_accueil_alimentaire= df_alim_sans_doublons[df_alim_sans_doublons['Dispositif'] .isin(['Accueil alimentaire', 'Accueil Alimentaire'])]
  df_alim_accueil_alimentaire.shape[0]
  df_alim_accueil_alimentaire = df_alim_accueil_alimentaire.groupby("n_structure").size().reset_index(name="Aide_alimentaire Nb_Centre_distribution_alimentaire")
  
  # CRsr
  df_alim_crsr= df_alim_sans_doublons[df_alim_sans_doublons['Dispositif'].isin(['Croix-Rouge sur Roues', 'CRSR Accueil alimentaire'])]
  df_alim_crsr.shape[0]
  df_alim_crsr = df_alim_crsr.groupby("n_structure").size().reset_index(name="Aide_alimentaire Nb_crsr")

  return (
    df_alim_U2A_sans_doublons, 
    df_alim_epicerie_sociale, 
    df_alim_accueil_alimentaire, 
    df_alim_crsr,
  )


def indicateurs_alim_DT(
    df_alim_U2A_sans_doublons, 
    df_alim_epicerie_sociale, 
    df_alim_accueil_alimentaire, 
    df_alim_crsr, 
    rattachement_court
):
    """
    Merge + groupby DT pour tous les DataFrames alimentation et retourne les 4 DataFrames modifiés.
    """

    # --- U2A ---
    df_alim_U2A_DT = df_alim_U2A_sans_doublons.copy()
    df_alim_U2A_DT["n_structure"] = df_alim_U2A_DT["n_structure"].astype("float64")
    df_alim_U2A_DT = pd.merge(
        df_alim_U2A_DT,
        rattachement_court,
        on="n_structure",
        how="left"
    )
    df_alim_U2A_DT = df_alim_U2A_DT.groupby("DT_de_rattachement", as_index=False)["Aide_alimentaire Nb_U2A"].sum()

    # --- Epicerie sociale ---
    df_alim_epicerie_sociale_DT = df_alim_epicerie_sociale.copy()
    df_alim_epicerie_sociale_DT["n_structure"] = df_alim_epicerie_sociale_DT["n_structure"].astype("float64")
    df_alim_epicerie_sociale_DT = pd.merge(
        df_alim_epicerie_sociale_DT,
        rattachement_court,
        on="n_structure",
        how="left"
    )
    df_alim_epicerie_sociale_DT = df_alim_epicerie_sociale_DT.groupby("DT_de_rattachement", as_index=False)["Aide_alimentaire Nb_epiceries_sociales"].sum()

    # --- Accueil alimentaire ---
    df_alim_accueil_alimentaire_DT = df_alim_accueil_alimentaire.copy()
    df_alim_accueil_alimentaire_DT["n_structure"] = df_alim_accueil_alimentaire_DT["n_structure"].astype("float64")
    df_alim_accueil_alimentaire_DT = pd.merge(
        df_alim_accueil_alimentaire_DT,
        rattachement_court,
        on="n_structure",
        how="left"
    )
    df_alim_accueil_alimentaire_DT = df_alim_accueil_alimentaire_DT.groupby("DT_de_rattachement", as_index=False)["Aide_alimentaire Nb_Centre_distribution_alimentaire"].sum()

    # --- CRSR ---
    df_alim_crsr_DT = df_alim_crsr.copy()
    df_alim_crsr_DT["n_structure"] = df_alim_crsr_DT["n_structure"].astype("float64")
    df_alim_crsr_DT = pd.merge(
        df_alim_crsr_DT,
        rattachement_court,
        on="n_structure",
        how="left"
    )
    df_alim_crsr_DT = df_alim_crsr_DT.groupby("DT_de_rattachement", as_index=False)["Aide_alimentaire Nb_crsr"].sum()

    return df_alim_U2A_DT, df_alim_epicerie_sociale_DT, df_alim_accueil_alimentaire_DT, df_alim_crsr_DT

