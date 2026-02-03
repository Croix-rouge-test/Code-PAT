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

def clean_gaia(GAIA_action, GAIA_rattachement_action, GAIA_contact, GAIA_structure, GAIA_act_str, mapping_df):
  GAIA_action = renommer_par_nom_table(GAIA_action, "GAIA_action", mapping_df)
  GAIA_rattachement_action = renommer_par_nom_table(GAIA_rattachement_action, "GAIA_rattachement_action", mapping_df)
  GAIA_contact = renommer_par_nom_table(GAIA_contact, "GAIA_contact", mapping_df)
  GAIA_structure = renommer_par_nom_table(GAIA_structure, "GAIA_structure", mapping_df)
  GAIA_act_str = renommer_par_nom_table(GAIA_act_str, "GAIA_act_str", mapping_df)
  return GAIA_action, GAIA_rattachement_action, GAIA_contact, GAIA_structure, GAIA_act_str

def fusion_gaia(GAIA_action, GAIA_rattachement_action, GAIA_contact, GAIA_structure, GAIA_act_str):
  #FTILRE SUR ANNEE NULLE OU FIN EN 2025

  # Vérification que la colonne est au format datetime
  GAIA_act_str['date_fin_activite_struct'] = pd.to_datetime(GAIA_act_str['date_fin_activite_struct'], errors='coerce')

  # Filtrage : date nulle ou année = 2025
  GAIA_act_str = GAIA_act_str[
      GAIA_act_str['date_fin_activite_struct'].isna() | (GAIA_act_str['date_fin_activite_struct'].dt.year == 2025)
  ]
  # left = pd.merge(df1, df2, on="id", how="left")

  # 1) Join avec action sur act_id
  df_GAIA = pd.merge(GAIA_rattachement_action, GAIA_action, on="n_action_ben", how="left")

  # 2) Join avec rattachement_action sur act_id + str_id
  df_GAIA = pd.merge(df_GAIA, GAIA_act_str, on="n_action_ben", how="left")

  # 3) Join avec contact sur cob_idrp
  df_GAIA = pd.merge(df_GAIA, GAIA_structure, on="id_structure", how="left")

  return df_GAIA

def indicateurs_gaia(df_GAIA):
  # Filtre sur le libelle approprié
  df_urgence = df_GAIA[df_GAIA["libelle_action_ben"] == "Urgences et autres opérations"]
  # On compte le nb de volontaires de l'urgence
  NbBeneDecla_GAIA = (df_urgence.groupby('n_structure_x')['id_gaia'].nunique())
  return NbBeneDecla_GAIA



