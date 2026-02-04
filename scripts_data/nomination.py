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

#def clean_nomination(NOMINATION_nomination, NOMINATION_attribution_nomination, mapping_df):
#  NOMINATION_nomination = renommer_par_nom_table(NOMINATION_nomination, "nomination", mapping_df)
#  NOMINATION_attribution_nomination = renommer_par_nom_table(NOMINATION_attribution_nomination, "attribution_nomination", mapping_df)
#  return NOMINATION_nomination, NOMINATION_attribution_nomination

def fusion_nomination(df_nomination, df_ref_nomination):
  #FTILRE SUR ANNEE NULLE OU FIN EN 2025

  # Vérification que la colonne est au format datetime
  df_nomination['nomination_date_fin_nomination'] = pd.to_datetime(df_nomination['nomination_date_fin_nomination'], errors='coerce')
  df_nomination['nomination_date_debut_nomination'] = pd.to_datetime(df_nomination['nomination_date_debut_nomination'], errors='coerce')

  # Filtrage : date nulle ou année = 2025
  df_nomination = df_nomination[
      df_nomination['nomination_date_fin_nomination'].isna() | (df_nomination['nomination_date_fin_nomination'].dt.year == 2025)
  ]

  df_NOMINATION = pd.merge(
     df_nomination,
     df_ref_nomination,
     left_on="nomination_nomination_id_fk",
     right_on="nomination_id_pk",
     how="left"
      )

  return df_NOMINATION


def indicateurs_nomination_AEO(df_NOMINATION, annee=2025):
    # Filtre sur les libellés appropriés
    libelles_AEO = ["RTAAD", "RLAAD"]
    referents_AEO = df_NOMINATION[
        df_NOMINATION["nomination_libcourt"].isin(libelles_AEO)
    ]

    # On compte le nb de RTAEO & RLAEO
    referents_AEO = (referents_AEO.groupby('nomination_structure_id_fk')['nomination_nivol_id_fk'].nunique())
    return referents_AEO


def indicateurs_nomination_OCR(df_NOMINATION, annee=2025):
    # Filtre sur les libellés appropriés
    libelles_OCR = ["RTOCR", "RLOCR"]
    referents_OCR = df_NOMINATION[
        df_NOMINATION["nomination_libcourt"].isin(libelles_OCR)
    ]
    # On compte le nb de RTAEO & RLAEO
    referents_OCR = (referents_OCR.groupby('nomination_structure_id_fk')['nomination_nivol_id_fk'].nunique())
    return referents_OCR



def indicateurs_nomination(df_NOMINATION, annee=2025):
    referents_AEO_mois = indicateurs_nomination_AEO(df_NOMINATION, annee)
    referents_OCR_mois = indicateurs_nomination_OCR(df_NOMINATION, annee)

    return referents_AEO_mois, referents_OCR_mois





