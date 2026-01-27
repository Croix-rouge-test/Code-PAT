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

def filtres_mobilite(mobilite):
  # Filtres et traitement de données
  mobilite = get_as_dataframe(mobilite.worksheet('Consolidation'), evaluate_formulas=True)
  mobilite = mobilite[(mobilite['Etat'] == 'Actif') & (mobilite['Code structure unifié'] != '') & (mobilite['Code structure unifié'].notna())]
  mobilite = mobilite[["N Département ","Code structure unifié","Nombre Bénéficiaires/an", "Nombre de volontaires total"]].rename(columns = {"N Département ":"n_dept","Code structure unifié": "n_structure", "Nombre Bénéficiaires/an" : "nb_pa", "Nombre de volontaires total" : "nb_bene"})
  mobilite['n_structure'] = mobilite['n_structure'].astype(int)

  def keep_integer(x):
    return re.sub("[^0-9]", "", x)


  mobilite['nb_pa'] = mobilite['nb_pa'].astype(str).apply(keep_integer).str.replace('^$','0',regex = True).astype(int)
  mobilite['nb_bene'] = mobilite['nb_bene'].astype(str).apply(keep_integer).str.replace('^$','0',regex = True).astype(int)

  return mobilite

def indicateurs_mobilite(mobilite):

  # données par structure
  grp_by = mobilite.groupby('n_structure').sum(['nb_pa','nb_bene']).reset_index()

  #checkup 

  indics_mobil = pd.merge(grp_by, mobilite.groupby('n_structure').value_counts().reset_index()[['n_structure','count']], on='n_structure', how = 'left')
  indics_mobil[indics_mobil['count'] > 1]

  # mobilite[mobilite['n_structure'].isin([x for x in indics_mobil[indics_mobil['count'] > 1]['n_structure'].values])]



  return mobilite


