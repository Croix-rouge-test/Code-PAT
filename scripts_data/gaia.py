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


def indicateurs_gaia(df_gaia):
  # Vérification que la colonne est au format datetime
  df_gaia['rattachement_benevole_date_fin'] = pd.to_datetime(df_gaia['rattachement_benevole_date_fin'], errors='coerce')
  df_gaia['rattachement_benevole_date_debut'] = pd.to_datetime(df_gaia['rattachement_benevole_date_debut'], errors='coerce')


  # Filtrage : date nulle ou année = 2025
  df_gaia = df_gaia[
    (
        df_gaia['rattachement_benevole_date_fin'].isna()
        | (df_gaia['rattachement_benevole_date_fin'].dt.year == 2025)
    )
    &
    (
        df_gaia['rattachement_benevole_date_debut'].isna()
        | (df_gaia['rattachement_benevole_date_debut'].dt.year != 2026)
    )
  ]
 
  df_gaia = df_gaia.rename(columns={
    'rattachement_benevole_structure_id_fk': 'n_structure',
    'rattachement_benevole_nivol_id_fk': 'Structure Nb_Benevoles'
  })
 # On compte le nb de volontaires de l'urgence
  nb_benevoles = (df_gaia.groupby('n_structure')['Structure Nb_Benevoles'].nunique())
  return nb_benevoles


def indicateurs_gaia_nvx(df_gaia):
  # Vérification que la colonne est au format datetime
  df_gaia['rattachement_benevole_date_fin'] = pd.to_datetime(df_gaia['rattachement_benevole_date_fin'], errors='coerce')
  df_gaia['rattachement_benevole_date_debut'] = pd.to_datetime(df_gaia['rattachement_benevole_date_debut'], errors='coerce')


  # Filtrage : date debut année = 2025
  df_gaia = df_gaia[
      df_gaia['rattachement_benevole_date_debut'].dt.year == 2025
  ]
 
  df_gaia = df_gaia.rename(columns={
    'rattachement_benevole_structure_id_fk': 'n_structure',
    'rattachement_benevole_nivol_id_fk': 'Structure Nb_nvx_Benevoles_2025'
  })
 # On compte le nb de volontaires de l'urgence
  nb_nvx_benevoles = (df_gaia.groupby('n_structure')['Structure Nb_nvx_Benevoles_2025'].nunique())
  return nb_nvx_benevoles


def indicateurs_gaia_DT(nb_benevoles, rattachement_court):
    # Merge données avec rattachement_court
    df_nb_benevoles = pd.merge(
    nb_benevoles,
    rattachement_court,
    on="n_structure",
    how="left"
    )


    # Groupby sur DT_de_rattachement
    nb_benevoles_DT = (df_nb_benevoles.groupby('DT_de_rattachement')['Structure Nb_Benevoles'].sum())
    return nb_benevoles_DT


def indicateurs_gaia_nvx_DT(nb_nvx_benevoles, rattachement_court):
    # Merge données avec rattachement_court
    df_nb_nvx_benevoles = pd.merge(
    nb_nvx_benevoles,
    rattachement_court,
    on="n_structure",
    how="left"
    )


    # Groupby sur DT_de_rattachement
    nb_nvx_benevoles_DT = (df_nb_nvx_benevoles.groupby('DT_de_rattachement')['Structure Nb_nvx_Benevoles_2025'].sum())
    return nb_nvx_benevoles_DT



