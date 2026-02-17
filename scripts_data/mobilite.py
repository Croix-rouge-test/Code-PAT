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

def filtres_mobilite(mobilite,mapping_df, df_ref_structure):
  # Filtres et traitement de données
  mobilite = get_as_dataframe(mobilite.worksheet('Consolidation'), evaluate_formulas=True)
  mobilite = mobilite[(mobilite['Etat'] == 'Actif') & (mobilite['Code structure unifié'] != '') & (mobilite['Code structure unifié'].notna())]
  mobilite = renommer_par_nom_table(mobilite[["N Département ","Code structure unifié","Nombre Bénéficiaires/an", "Nombre de volontaires total"]], "Mobilité", mapping_df)
  mobilite['n_structure'] = mobilite['n_structure'].astype(int)




  mobilite['nb_pa'] = mobilite['nb_pa'].astype(str).apply(keep_integer).str.replace('^$','0',regex = True).astype(int)
  mobilite['nb_bene'] = mobilite['nb_bene'].astype(str).apply(keep_integer).str.replace('^$','0',regex = True).astype(int)
  mobilite = mobilite.drop(['nb_bene'], axis = 1)

  _ , _ , _, df_mobilite = apply_rattachement_successif(df_ref_structure, df_mobilite, col = 'n_structure')

  return mobilite


def indicateurs_mobilite(df_mobilite, df_ref_structure, col_structure):
  """
  Calcul les indicateurs utilisant les données mobilité, certaines colonne seront utilisées plus tard pour des fusions
  """

  mobilite_dt = dt_rattachement(df_mobilite, df_ref_structure)
  mobilite_dt = pd.merge(mobilite_dt, df_ref_structure['n_structure'].drop_duplicates(), on='n_structure', how="inner")
  if col_structure != 'n_structure' :
    mobilite_dt = mobilite_dt.drop(['n_structure'], axis = 1).rename(columns = {col_structure : 'n_structure'})
    mobilite_dt['n_structure'] = mobilite_dt['n_structure'].astype(int)

  mobilite_dt_n_struc = mobilite_dt.groupby('n_structure').size().rename("AEO Structure_activite_mobile")

  mobilite_dt_nb_pa_bene = mobilite_dt.groupby('n_structure').sum(['nb_pa']).rename(columns = {'nb_pa':'AEO Nb_PA_dispos_mobiles'}).reset_index()

  dt_return = pd.merge(mobilite_dt_n_struc, mobilite_dt_nb_pa_bene, on='n_structure', how="left")
  return dt_return



