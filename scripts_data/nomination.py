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


import pandas as pd

def _indicateurs_referents_par_mois(
    df_nomination,
    libelle_nomination,
    annee=2025
):
    # Filtre sur le libellé
    df = df_nomination[
        df_nomination["libelle_nomination"] == libelle_nomination
    ].copy()

    # Génération des mois
    mois = pd.date_range(
        start=f"{annee}-01-01",
        end=f"{annee}-12-01",
        freq="MS"
    )

    resultats = []

    for m in mois:
        debut_mois = m
        fin_mois = m + pd.offsets.MonthEnd(1)

        actifs = df[
            (df["date_debut_nomination"] <= fin_mois) &
            (df["date_fin_nomination"] >= debut_mois)
        ]

        comptage = (
            actifs
            .groupby("structure_id")
            .size()
            .reset_index(name="nb")
        )

        comptage["mois"] = m.strftime("%Y-%m")
        resultats.append(comptage)

    df_mois = pd.concat(resultats)

    df_pivot = (
        df_mois
        .pivot(
            index="structure_id",
            columns="mois",
            values="nb"
        )
        .fillna(0)
        .astype(int)
    )

    return df_pivot

def indicateurs_nomination_AEO(df_NOMINATION, annee=2025):
    return _indicateurs_referents_par_mois(
        df_nomination=df_NOMINATION,
        libelle_nomination="RTAEO",
        annee=annee
    )

def indicateurs_nomination_OCR(df_NOMINATION, annee=2025):
    return _indicateurs_referents_par_mois(
        df_nomination=df_NOMINATION,
        libelle_nomination="RTOCR",
        annee=annee
    )

def indicateurs_nomination(df_NOMINATION, annee=2025):
    referents_AEO_mois = indicateurs_nomination_AEO(df_NOMINATION, annee)
    referents_OCR_mois = indicateurs_nomination_OCR(df_NOMINATION, annee)

    return referents_AEO_mois, referents_OCR_mois





