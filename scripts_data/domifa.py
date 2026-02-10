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

# Clean

def clean_domifa(client):
  # Import
  query = """
  SELECT *
  FROM `crf-pat.dataset_PAT_2025.Domifa`
  """
  df_domiciliation = client.query(query).to_dataframe()

  query = """
  SELECT *
  FROM `crf-pat.dataset_PAT_2025.Ref_structure`
  """

  df_ref_structure = client.query(query).to_dataframe()

  query = """
  SELECT *
  FROM `crf-pat.dataset_PAT_2025.rattachement_court`
  """

  df_rattachement_court = client.query(query).to_dataframe()

  # Preparation ref structure
  ref_structure1 = df_ref_structure[(df_ref_structure['type_structure'] == "UNITE LOCALE - UL") | (df_ref_structure['type_structure'] == 'DELEGATION TERRITORIALE - DT')]
  #CLEAN et preparation base
  df_domiciliation["Structure"] = df_domiciliation["Structure"].astype(str).map(normalize_structure)

  df_domiciliation["Structure"] = df_domiciliation["Structure"].replace({
      "UL TERRES DU MEiDOC": "UL TERRES DU MEDOC",
      "UL DE PARIS I ET II": "UL DE PARIS 1ER ET 2EME",
      "UL DE POITIERS": "UL DU GRAND POITIERS",
  })

  df_domiciliation.columns = ["Structure", "AEO Nb_personnes_domiciliees_crf"]

  #Rapprochement libelles
  df_domiciliation = rapprochement_libelles(ref_structure1, df_domiciliation, "Structure")

  return df_domiciliation, df_rattachement_court

# Fusion


#Calcul Structure



#Calcul DT

def NB_personnes_domiciliees_DT(df, filtre=None,
                              col_structure="DT_de_rattachement",
                              col_user="AEO Nb_personnes_domiciliees_crf",
                              out_col="AEO Nb_personnes_domiciliees_crf"):
    d = df.query(filtre) if filtre else df
    return (d.groupby(col_structure)[col_user]
              .sum()
              .rename(out_col)
              .to_frame() #transforme la serie en dataframe
              .reset_index())

def indicateurs_domifa(df_domiciliation):
  #Calcul par structure
  df_personnes_domiciliees_struct = df_domiciliation[['n_structure'	, 'DT_de_rattachement', 'AEO Nb_personnes_domiciliees_crf']]
  #Calcul DT
  df_personnes_domiciliees_DT = NB_personnes_domiciliees_DT(df_personnes_domiciliees_struct)

  return df_personnes_domiciliees_struct, df_personnes_domiciliees_DT


  # Vérifications 

def verificiation_domifa(df_personnes_domiciliees_struct,df_personnes_domiciliees_DT,ref_structure1):
  #1. Vérification des NaN ou valeurs vides
  #2. Vérification des doublons (uniquement les codes)
  #3Vérification des codes absents du référentiel
  verifier_colonne_structure(df_personnes_domiciliees_struct, "n_structure", ref_structure1)
  verifier_colonne_structure(df_personnes_domiciliees_DT, "DT_de_rattachement", df_rattachement_court)

  verifier_mapping(df_personnes_domiciliees_struct, "n_structure", "Structure", ref_structure1)

  #Vérification qu'on a bien la même somme de personnes domiciliées entre le fichier de base et le fichier df_personnes_domiciliees_struct
  check_sum_equal(
      df_personnes_domiciliees_struct, "AEO Nb_personnes_domiciliees_crf",
      df_domiciliation, "AEO Nb_personnes_domiciliees_crf",
      label_left="table struct", label_right="table source"
  )



  #Vérification qu'on a bien la même somme de personnes domiciliées entre le fichier de base et le fichier df_personnes_domiciliees_DT
  check_sum_equal(
      df_personnes_domiciliees_DT, "AEO Nb_personnes_domiciliees_crf",
      df_domiciliation, "AEO Nb_personnes_domiciliees_crf",
      label_left="table struct", label_right="table source"
  )