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

## récupération des données

def clean_alim(df_alim):
  df_alim=df_alim[["Dispositif","Code U2A","Stucture rattachement",'N° structure']]

  ## préparation BDD alim
  if 'Code U2A' in df_alim.columns:
    # Identifier les doublons dans la colonne 'Code U2A'
    duplicates = df_alim[df_alim['Code U2A'].duplicated(keep=False)]

    # Compter le nombre de doublons
    num_duplicates = duplicates.shape[0]

    if num_duplicates > 0:
          print(f"Il y a {num_duplicates} lignes avec des doublons dans la colonne 'Code U2A'.")
          print("Voici les lignes en doublon (affichant toutes les occurrences des valeurs dupliquées) :")
          display(duplicates.sort_values(by='Code U2A'))
    else:
          print("Aucun doublon trouvé dans la colonne 'Code U2A'.")
  else:
        print("La colonne 'Code U2A' n'existe pas dans le DataFrame df_alim.")
 
  # Création d'une base de données sans doublon
  df_alim_sans_doublons =df_alim.drop_duplicates(subset=['Code U2A'], keep='first')
  print(f"Taille du DataFrame après suppression des doublons : {df_alim_sans_doublons.shape}")
  df_alim_sans_doublons = df_alim_sans_doublons.rename(columns={"N° structure": "n_structure"})
  # Conversion de la colonne n_structure en string pour la cohérence avec df_ref_structure
  df_alim_sans_doublons['n_structure'] = df_alim_sans_doublons['n_structure'].astype(str)
  # Supprimer le '.0' des chaînes si elles proviennent de nombres flottants
  df_alim_sans_doublons['n_structure'] = df_alim_sans_doublons['n_structure'].apply(lambda x: x[:-2] if x.endswith('.0') else x)
  display(df_alim_sans_doublons.head())

    # U2A

  if 'Dispositif' in df_alim_sans_doublons.columns:
      print("Nombre d'occurrences pour chaque type de 'Dispositif':")
      display(df_alim_sans_doublons['Dispositif'].value_counts())
  else:
      print("La colonne 'Dispositif' n'existe pas dans le DataFrame df_alim_sans_doublons.")
  
  df_alim_U2A_sans_doublons = df_alim_sans_doublons.groupby("n_structure").size().reset_index(name="Aide_alimentaire Nb_U2A")
  verifier_colonne_structure(df_alim_U2A_sans_doublons,"n_structure", df_ref_structure)

  df_alim_U2A_DT = dt_rattachement(df_alim_U2A_sans_doublons, df_ref_structure)
  df_alim_U2A_DT = df_alim_U2A_DT.groupby("DT_de_rattachement").size().reset_index(name="Aide_alimentaire Nb_U2A DT")

  # Epicerie sociale
  df_alim_epicerie_sociale= df_alim_sans_doublons[df_alim_sans_doublons['Dispositif'] == 'Epicerie sociale']
  display(df_alim_epicerie_sociale.head())
  df_alim_epicerie_sociale.shape[0]
  df_alim_epicerie_sociale = df_alim_epicerie_sociale.groupby("n_structure").size().reset_index(name="Aide_alimentaire Nb_epiceries_sociales")
  verifier_colonne_structure(df_alim_epicerie_sociale,"n_structure", df_ref_structure)
  
  df_alim_epicerie_sociale_DT = dt_rattachement(df_alim_epicerie_sociale, df_ref_structure)
  df_alim_epicerie_sociale_DT = df_alim_epicerie_sociale_DT.groupby("DT_de_rattachement").size().reset_index(name="Aide_alimentaire Nb_epiceries_sociales DT")
  

  # Accueil Alimentaire
  df_alim_accueil_alimentaire= df_alim_sans_doublons[df_alim_sans_doublons['Dispositif'] .isin(['Accueil alimentaire', 'Accueil Alimentaire'])]
  display (df_alim_accueil_alimentaire.head())
  df_alim_accueil_alimentaire.shape[0]
  df_alim_accueil_alimentaire = df_alim_accueil_alimentaire.groupby("n_structure").size().reset_index(name="Aide_alimentaire Nb_Centre_distribution_alimentaire")
  verifier_colonne_structure(df_alim_accueil_alimentaire, "n_structure", df_ref_structure)
  
  df_alim_accueil_alimentaire_DT = dt_rattachement(df_alim_accueil_alimentaire, df_ref_structure)
  df_alim_accueil_alimentaire_DT = df_accueil_alimentaire_DT.groupby("DT_de_rattachement").size().reset_index(name="Aide_alimentaire Nb_Centre_distribution_alimentaire DT")
  
  # CRsr
  df_alim_crsr= df_alim_sans_doublons[df_alim_sans_doublons['Dispositif'].isin(['Croix-Rouge sur Roues', 'CRSR Accueil alimentaire'])]
  display (df_alim_crsr.head())
  df_alim_crsr.shape[0]
  df_alim_crsr = df_alim_crsr.groupby("n_structure").size().reset_index(name="Aide_alimentaire Nb_crsr")
  verifier_colonne_structure(df_alim_crsr, "n_structure", df_ref_structure)
  
  df_alim_crsr_DT = dt_rattachement(df_alim_crsr, df_ref_structure)
  df_alim_crsr_DT = df_crsr_DT.groupby("DT_de_rattachement").size().reset_index(name="Aide_alimentaire Nb_crsr DT")

  return df_alim_U2A_sans_doublons, df2, df3
  