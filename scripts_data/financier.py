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
sys.path.append(os.path.abspath("/Code-PAT/scripts_data"))
from utils import *

def import_clean_donnees_financieres(financier,df_ref_structure, mapping_df):

  # Import
  dt_prod = get_as_dataframe(financier.worksheet('DT_Prod'), skiprows=3,evaluate_formulas=True)
  dt_resnet = get_as_dataframe(financier.worksheet('DT_Res Net'), skiprows=3,evaluate_formulas=True)
  dt_resnet_corr_prod = get_as_dataframe(financier.worksheet('DT_Res corrélé Prod'), skiprows=3, evaluate_formulas=True)
  dt_treso_brute = get_as_dataframe(financier.worksheet('DT_Trés brute'), skiprows=3,evaluate_formulas=True)
  dt_ul_ant_prod = get_as_dataframe(financier.worksheet('DT-UL-Ant_Prod'), skiprows=3, evaluate_formulas=True)
  dt_ul_ant_res_net = get_as_dataframe(financier.worksheet('DT-UL-Ant_Res Net'), skiprows=3, evaluate_formulas=True)
  dt_ul_res_net_corr_prod = get_as_dataframe(financier.worksheet('DT-UL-Res corrélé Prod'), skiprows=3, evaluate_formulas=True)
  dt_ul_treso_brute = get_as_dataframe(financier.worksheet('DT-UL_Tréso brute'), skiprows=3, evaluate_formulas=True)

  # Renommer colonnes
  dt_prod = renommer_par_nom_table(dt_prod, "financier_DT", mapping_df)
  dt_resnet = renommer_par_nom_table(dt_resnet, "financier_DT", mapping_df)
  dt_resnet_corr_prod = renommer_par_nom_table(dt_resnet_corr_prod, "financier_DT", mapping_df)
  dt_treso_brute = renommer_par_nom_table(dt_treso_brute, "financier_DT", mapping_df)
  dt_ul_ant_prod = renommer_par_nom_table(dt_ul_ant_prod, "financier_DT_UL", mapping_df)
  dt_ul_ant_res_net = renommer_par_nom_table(dt_ul_ant_res_net, "financier_DT_UL", mapping_df)
  dt_ul_res_net_corr_prod = renommer_par_nom_table(dt_ul_res_net_corr_prod, "financier_DT_UL", mapping_df)
  dt_ul_treso_brute = renommer_par_nom_table(dt_ul_treso_brute, "financier_DT_UL", mapping_df)

  dt_prod = dt_prod[['n_dept','Réalisé 2024 Total Année','libelle_structure']].rename(columns = {'Réalisé 2024 Total Année' : 'Financier Prod_2024'}).iloc[:dt_prod.shape[0]-2]
  dt_prod['libelle_structure'] = 'DT - ' + dt_prod['libelle_structure']
  dt_resnet = dt_resnet[['n_dept','Réalisé 2024 Total Année']].rename(columns = {'Réalisé 2024 Total Année' : 'Financier ResNet_2024'}).iloc[:dt_resnet.shape[0]-2]
  dt_resnet_corr_prod = dt_resnet_corr_prod[['n_dept','Réalisé 2024 Total Année']].rename(columns = {'Réalisé 2024 Total Année' : 'Financier ResCorrProd_2024'}).iloc[:dt_resnet_corr_prod.shape[0]-2]
  dt_treso_brute = dt_treso_brute[['n_dept','Tréso nette au 31/12/2024','Financier Mois_AvanceTreso_2024']].rename(columns = {'Tréso nette au 31/12/2024' : "Financier TresoBrute_2024"}).iloc[:dt_treso_brute.shape[0]-2]

  dt_ul_ant_prod = dt_ul_ant_prod[['n_structure','Réalisé 2024 Total Année','libelle_structure']].rename(columns = {'Réalisé 2024 Total Année' : 'Financier Prod_2024'}).iloc[:dt_ul_ant_prod.shape[0]-1]
  dt_ul_ant_res_net = dt_ul_ant_res_net[['n_structure','Réalisé 2024 Total Année']].rename(columns = {'Réalisé 2024 Total Année' : 'Financier ResNet_2024'}).iloc[:dt_ul_ant_res_net.shape[0]-1]
  dt_ul_res_net_corr_prod = dt_ul_res_net_corr_prod[['n_structure','Réalisé 2024 Total Année']].rename(columns = {'Réalisé 2024 Total Année' : 'Financier ResCorrProd_2024'}).iloc[:dt_ul_res_net_corr_prod.shape[0]-1]
  dt_ul_treso_brute = dt_ul_treso_brute[['n_structure','Tréso nette au 31/12/2024','Financier Mois_AvanceTreso_2024']].rename(columns = {'Tréso nette au 31/12/2024' : "Financier TresoBrute_2024"}).iloc[:dt_ul_treso_brute.shape[0]-1]

  # Clean
  def dept_clean(x):
    if x == '2A' or x == '2B':
      return str(x)
    else : return str(int(x))
  dt_prod['n_dept'] = dt_prod['n_dept'].apply(dept_clean)
  dt_resnet['n_dept'] = dt_resnet['n_dept'].apply(dept_clean)
  dt_resnet_corr_prod['n_dept'] = dt_resnet_corr_prod['n_dept'].apply(dept_clean)
  dt_treso_brute['n_dept'] = dt_treso_brute['n_dept'].apply(dept_clean)

  dt_ul_ant_prod['n_structure'] = dt_ul_ant_prod['n_structure'].astype(int).astype(str)
  dt_ul_ant_res_net['n_structure'] = dt_ul_ant_res_net['n_structure'].astype(int).astype(str)
  dt_ul_res_net_corr_prod['n_structure'] = dt_ul_res_net_corr_prod['n_structure'].astype(int).astype(str)
  dt_ul_treso_brute['n_structure'] = dt_ul_treso_brute['n_structure'].astype(int).astype(str)

  # Normalement le seul doublon est DT de la dordogne Code structure : 3968, on garde la première occurence

  dt_ul_ant_prod = dt_ul_ant_prod.drop_duplicates(subset="n_structure", keep="first")
  dt_ul_ant_res_net = dt_ul_ant_res_net.drop_duplicates(subset="n_structure", keep="first")
  dt_ul_res_net_corr_prod = dt_ul_res_net_corr_prod.drop_duplicates(subset="n_structure", keep="first")
  dt_ul_treso_brute = dt_ul_treso_brute.drop_duplicates(subset="n_structure", keep="first")

  # On garde seulement unités locales et DT
  mask = dt_ul_ant_prod['libelle_structure'].isin(set(df_ref_structure['n_structure'].drop_duplicates()))
  dt_ul_ant_prod = dt_ul_ant_prod[mask]

  return dt_prod, dt_resnet, dt_resnet_corr_prod, dt_treso_brute, dt_ul_ant_prod, dt_ul_ant_res_net, dt_ul_res_net_corr_prod, dt_ul_treso_brute










