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
  df_gaia['rattachement_benevole_date_fin'] = pd.to_datetime(df_nomination['rattachement_benevole_date_fin'], errors='coerce')
  df_gaia['rattachement_benevole_date_debut'] = pd.to_datetime(df_nomination['rattachement_benevole_date_debut'], errors='coerce')

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
    'rattachement_benevole_structure_id_fk': 'n_structure'
  })
 # On compte le nb de volontaires de l'urgence
  nb_benevoles = (df_gaia.groupby('n_structure')['rattachement_benevole_nivol_id_fk'].nunique())
  return nb_benevoles



