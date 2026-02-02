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

def clean_impact(IMPACT_indicateurs, IMPACT_indicateur_value, IMPACT_donnees_activite, IMPACT_abstract_donnees_activite, mapping_df):

  IMPACT_indicateurs = renommer_par_nom_table(IMPACT_indicateurs, "IMPACT_indicateurs", mapping_df)
  IMPACT_indicateur_value = renommer_par_nom_table(IMPACT_indicateur_value, "IMPACT_indicateur_value", mapping_df)
  IMPACT_donnees_activite = renommer_par_nom_table(IMPACT_donnees_activite, "IMPACT_donnees_activite", mapping_df)
  IMPACT_abstract_donnees_activite = renommer_par_nom_table(IMPACT_abstract_donnees_activite, "IMPACT_abstract_donnees_activite", mapping_df)

  return IMPACT_indicateurs, IMPACT_indicateur_value, IMPACT_donnees_activite, IMPACT_abstract_donnees_activite

def fusion_impact(IMPACT_indicateurs, IMPACT_indicateur_value, IMPACT_donnees_activite, IMPACT_abstract_donnees_activite):
  #FTILRE SUR ANNEE 2025

  # Vérification que la colonne est au format datetime
  IMPACT_donnees_activite['date_fin_activite'] = pd.to_datetime(IMPACT_donnees_activite['date_fin_activite'], errors='coerce')
  IMPACT_donnees_activite['date_debut_activite'] = pd.to_datetime(IMPACT_donnees_activite['date_debut_activite'], errors='coerce')

  # Filtrage : date nulle ou année = 2025
  IMPACT_donnees_activite = IMPACT_donnees_activite[ (IMPACT_donnees_activite['date_debut_activite'].dt.year == 2025)]
  # left = pd.merge(df1, df2, on="id", how="left")

  # 1) Join avec action sur act_id
  df_IMPACT = pd.merge(IMPACT_indicateur_value, IMPACT_indicateurs, on="n_indicateurs", how="left")

  # 2) Join avec rattachement_action sur act_id + str_id
  df_IMPACT = pd.merge(df_IMPACT, IMPACT_donnees_activite, on="id_activite", how="left")

  # 3) Join avec contact sur cob_idrp
  df_IMPACT = pd.merge(df_IMPACT, IMPACT_abstract_donnees_activite, on="id_activite", how="left")

  return df_IMPACT

def indicateurs_impact():
  return None
