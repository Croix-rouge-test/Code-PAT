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


def clean_impact(client):

  query_ref_impact = """
  SELECT *
  FROM crf-pat.dataset_PAT_2025.crf_impact_ref_indicateur
  """

  query_impact = """
  SELECT *
  FROM crf-pat.dataset_PAT_2025.crf_pat_2025_impact_indicateur_suivi
  """


  df_ref_impact = client.query(query_ref_impact).to_dataframe()
  df_impact = client.query(query_impact).to_dataframe()
  # Vérification que la colonne est au format datetime
  df_impact['impact_date_fin'] = pd.to_datetime(df_impact['impact_date_fin'], errors='coerce')
  df_impact['impact_date_debut'] = pd.to_datetime(df_impact['impact_date_debut'], errors='coerce')

  return df_ref_impact, df_impact


def fusion_impact(df_impact, df_ref_impact):
  #FTILRE SUR ANNEE 2025

  # Filtrage : date nulle ou année = 2025
  df_impact = df_impact[ (df_impact['impact_date_debut'].dt.year == 2025)]
  # left = pd.merge(df1, df2, on="id", how="left")


  # 1) Join avec action sur act_id
  df_IMPACT = pd.merge(
    df_impact,
    df_ref_impact,
    left_on=[
        "impact_indicateur_id_fk",
        "impact_activite_benevole_id_fk"
    ],
    right_on=[
        "impact_indicateur_id_pk",
        "impact_indicateur_activite_benevole_id_fk"
    ],
    how="left"
    )


  return df_IMPACT


def indicateurs_impact_ppc(df_IMPACT):
    # Filtre sur les libellés appropriés
    libelles_Urgences = [10119, 10125, 10126, 10127, 10128, 10129, 10115, 10132, 10133, 10134, 10135, 10136, 10137]
    IMPACT_Urgences = df_IMPACT[df_IMPACT["impact_indicateur_activite_benevole_id_fk"].isin(libelles_Urgences)]


    libelles_ppc = [383, 427, 456, 462, 190, 193, 194, 199, 464, 465]
    IMPACT_Urgences = df_IMPACT[df_IMPACT["impact_indicateur_id_fk"].isin(libelles_ppc)]


    IMPACT_Urgences['impact_reponse'] = (
    IMPACT_Urgences['impact_reponse']
    .str.replace("'", "", regex=False)   # enlève les guillemets simples
    .astype(float)
    .astype(int)
    )


    IMPACT_ppc = (
    IMPACT_Urgences
    .groupby('impact_structure_id_fk')['impact_reponse'].sum().reset_index(name='Dispositifs_d_urgence Nb_personnes_prises_charge'))
   
    return IMPACT_ppc






def indicateurs_impact_agrementAB(df_IMPACT):
    # Filtre sur les libellés appropriés
    libelles_Urgences = [10119, 10125, 10126, 10127, 10128, 10129, 10115, 10132, 10133, 10134, 10135, 10136, 10137]
    IMPACT_Urgences = df_IMPACT[df_IMPACT["impact_indicateur_activite_benevole_id_fk"].isin(libelles_Urgences)]
   
    libelles_agrementAB = [355, 367, 380, 394, 414, 422, 438, 452, 461, 356, 368, 381, 395, 415, 423, 439, 453]
    IMPACT_Urgences = df_IMPACT[df_IMPACT["impact_indicateur_id_fk"].isin(libelles_agrementAB)]
   
    IMPACT_Urgences['impact_reponse'] = (
    IMPACT_Urgences['impact_reponse']
    .str.replace("'", "", regex=False)   # enlève les guillemets simples
    )


    IMPACT_Urgences.loc[:, 'impact_reponse'] = (
    IMPACT_Urgences['impact_reponse']
    .astype(str)
    .str.strip()
    .str.lower()
    .map({'Oui': 1.0, 'Non': 0.0})
    .astype('Int64')   # ou .astype(int) si tu es sûre qu’il n’y a pas de NaN
    )


    IMPACT_agrementAB = (
    IMPACT_Urgences
    .groupby('impact_structure_id_fk')['impact_reponse'].sum().reset_index(name='Dispositifs_d_urgence Nb_agrements'))


    return IMPACT_agrementAB




def indicateurs_impact_agrementDPS(df_IMPACT):
    # Filtre sur les libellés appropriés
    libelles_Urgences = [10119, 10125, 10126, 10127, 10128, 10129, 10115, 10132, 10133, 10134, 10135, 10136, 10137]
    IMPACT_Urgences = df_IMPACT[df_IMPACT["impact_indicateur_activite_benevole_id_fk"].isin(libelles_Urgences)]
   
    libelles_agrementDPS = [417, 425, 441, 455]
    IMPACT_Urgences = df_IMPACT[df_IMPACT["impact_indicateur_id_fk"].isin(libelles_agrementDPS)]
 
    IMPACT_Urgences['impact_reponse'] = (
    IMPACT_Urgences['impact_reponse']
    .str.replace("'", "", regex=False)   # enlève les guillemets simples
    )


    IMPACT_Urgences.loc[:, 'impact_reponse'] = (
    IMPACT_Urgences['impact_reponse']
    .astype(str)
    .str.strip()
    .str.lower()
    .map({'Oui': 1.0, 'Non': 0.0})
    .astype('Int64')   # ou .astype(int) si tu es sûre qu’il n’y a pas de NaN
    )


    IMPACT_agrementDPS = (
    IMPACT_Urgences
    .groupby('impact_structure_id_fk')['impact_reponse'].sum().reset_index(name='Secours Nb_agrements_DPS_2025'))


    return IMPACT_agrementDPS




def indicateurs_IMPACTppc_DT(IMPACT_ppc, rattachement_court):
    # Merge données avec rattachement_court
    df_IMPACT_ppc = pd.merge(
    IMPACT_ppc,
    rattachement_court,
    left_on="impact_structure_id_fk",
    right_on="n_structure",
    how="left"
    )


    # Groupby sur DT_de_rattachement
    IMPACT_ppc_DT = (df_IMPACT_ppc.groupby('DT_de_rattachement')['Dispositifs_d_urgence Nb_personnes_prises_charge'].sum())
    return IMPACT_ppc_DT




def indicateurs_IMPACTagrementAB_DT(IMPACT_agrementAB, rattachement_court):
    # Merge données avec rattachement_court
    df_IMPACT_agrementAB = pd.merge(
    IMPACT_agrementAB,
    rattachement_court,
    left_on="impact_structure_id_fk",
    right_on="n_structure",
    how="left"
    )


    # Groupby sur DT_de_rattachement
    IMPACT_agrementAB_DT = (df_IMPACT_agrementAB.groupby('DT_de_rattachement')['Dispositifs_d_urgence Nb_agrements'].sum())
    return IMPACT_agrementAB_DT




def indicateurs_IMPACTagrementDPS_DT(IMPACT_agrementDPS, rattachement_court):
    # Merge données avec rattachement_court
    df_IMPACT_agrementDPS = pd.merge(
    IMPACT_agrementDPS,
    rattachement_court,
    left_on="impact_structure_id_fk",
    right_on="n_structure",
    how="left"
    )


    # Groupby sur DT_de_rattachement
    IMPACT_agrementDPS_DT = (df_IMPACT_agrementDPS.groupby('DT_de_rattachement')['Secours Nb_agrements_DPS_2025'].sum())
    return IMPACT_agrementDPS_DT















