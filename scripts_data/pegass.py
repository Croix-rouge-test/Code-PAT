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


def make_var_name(libelle_activite_benevole):
    # Supprimer les accents
    s = unicodedata.normalize("NFKD", libelle_activite_benevole)
    s = "".join(c for c in s if not unicodedata.combining(c))
    # Minuscules + remplacer tout ce qui n'est pas lettre/chiffre par "_"
    s = s.lower()
    s = re.sub(r"[^0-9a-zA-Z]+", "_", s).strip("_")
    return f"df_{s}"

    
##Definition pour calcul benevoles distincts
def nb_benevoles_distincts_gen(df, filtre=None,
                              col_structure="structure_menant_activite_id",
                              col_user="nivol",
                              out_col="nb_benevoles_distincts"):
    d = df.query(filtre) if filtre else df
    return (d.groupby(col_structure)[col_user]
              .nunique()
              .rename(out_col)
              .to_frame() #transforme la serie en dataframe
              .reset_index())


def nb_benevoles_distincts_DT_gen(df, filtre=None,
                                col_structure="DT_de_rattachement",
                                col_user="nivol",
                                out_col="nb_benevoles_distincts"):
      d = df.query(filtre) if filtre else df
      return (d.groupby(col_structure)[col_user]
                .nunique()
                .rename(out_col)
                .to_frame() #transforme la serie en dataframe
                .reset_index())

                
##Definition pour calcul benevoles distincts
def nb_benevoles_distincts_mois_gen(df, filtre=None,
                              col_structure="structure_menant_activite_id",
                              col_user="nivol",
                              col_mois = "mois_debut_inscription",
                              out_col="nb_benevoles_distincts_mois"):
    d = df.query(filtre) if filtre else df
    return (d.groupby([col_structure, col_mois])[col_user]
              .nunique()
              .rename(out_col)
              .to_frame() #transforme la serie en dataframe
              .reset_index())

##Definition pour calcul benevoles distincts
def nb_benevoles_distincts_mois_DT_gen(df, filtre=None,
                              col_structure="DT_de_rattachement",
                              col_user="nivol",
                              col_mois = "mois_debut_inscription",
                              out_col="nb_benevoles_distincts_mois"):
    d = df.query(filtre) if filtre else df
    return (d.groupby([col_structure, col_mois])[col_user]
              .nunique()
              .rename(out_col)
              .to_frame() #transforme la serie en dataframe
              .reset_index())
              
def clean_pegass(Pegass_inscription,Pegass_activite,Ref_activité_benevole, mapping_df):
  Pegass_inscription = renommer_par_nom_table(Pegass_inscription, "Pegass_inscription", mapping_df)
  #mettre les dates en format date
  Pegass_inscription["debut_inscription"] = pd.to_datetime( Pegass_inscription["debut_inscription"])
  Pegass_inscription["fin_inscription"] = pd.to_datetime( Pegass_inscription["fin_inscription"])

  Pegass_activite = renommer_par_nom_table(Pegass_activite, "Pegass_activite", mapping_df)
  Ref_activité_benevole = renommer_par_nom_table(Ref_activité_benevole, "Ref_activité_benevole", mapping_df)
  return Pegass_inscription, Pegass_activite, Ref_activité_benevole


def fusion_pegass(Pegass_inscription, Pegass_activite, Ref_activité_benevole):

  FILTERS = {
    "filtres_activites_ben_test": {"col": "activite_benevole_id", "values": [1, 2, 3, 4]}, #variables numeric
     "statut_inscription" : {"col": "statut_inscription", "values": [1]},
    "vulne_core": {"col": "Indicateur", "values": ["Indice de vulnérabilité global", "Revenu median"]}, #variables textuelles
  }
  df1 = pd.merge(Pegass_inscription, Pegass_activite, left_on="activite_id", right_on="activite_id", how="left")
  df2 = pd.merge(df1, Ref_activité_benevole, left_on="activite_benevole_id", right_on="activite_benevole_id", how="left")
  df2.to_csv("df2.csv", index=False, encoding="utf-8-sig")
  df2 = df2.rename(columns={"structureMenanActiviteId": "structure_menant_activite_id"}) #renomage temporaire à  supprimer après
  df2 = pd.merge(df2, rattachement_court, left_on="structure_menant_activite_id", right_on="n_structure", how="left").drop(columns=["n_structure"])

  return df2

def indicateurs_pegass(df2):
  # NOMBRE DE BENEVOLES PAR ACTIVITE BENEVOLES
  # Fonction filtre encore plus sophistiqué

  FILTERS_PEGASS = {
      "filtres_activites_ben_test": {"col": "activite_benevole_id", "values": [1, 2, 3, 4]}, #variables numeric
      "statut_inscription" : {"col": "statut_inscription", "values": [1]},
      "vulne_core": {"col": "Indicateur", "values": ["Indice de vulnérabilité global", "Revenu median"]}, #variables textuelles
  }
  df2 = filtre_2025(df2,date_col="debut_inscription" )

  df2 = filtre(df2,"statut_inscription")

  df2 = filtre(df2,"filtres_activites_ben_test")
  df2['debut_inscription'] = pd.to_datetime(df2['debut_inscription'])
  df2["mois_debut_inscription"] = df2["debut_inscription"].dt.month
  # On compte le nb de NivolS unniques par Structure
  Nb_benevoles_distincts = (df2.groupby('structure_menant_activite_id')['nivol'].nunique()).rename("nb_benevoles_distincts")
  # A voir si on peut pas remplacer reset_index par .rename()
  activite_ben_cible = "Distribution alimentaire"  # l'intitulé que l'on souhaite

  Nb_benevoles_Distribution_alimentaire = (
      df2[df2['libelle_activite_benevole'] == activite_ben_cible]  # filtre sur l’intitulé
        .nunique()
        .reset_index(name='nb_benevoles_distincts')
  )

    # 2) Indicateur avec filtre
  activite_ben_cible = "Distribution alimentaire"
  Nb_benevoles_Distribution_alimentaire1 = nb_benevoles_distincts_gen(
      df2,
      filtre=f"libelle_activite_benevole == @activite_ben_cible"
  )

  ##Automatisation en créant une boucle

  #Il faut prendre activite_id pour le numero d'activité mais là je teste direct avec le libellé
  liste_activite_ben= [
      "Distribution alimentaire",
      "Épicerie sociale",
      "Colis alimentaire",
      "Aide d'urgence",
      "Autre dispositif"
  ]

  for activite in liste_activite_ben:
    df_tmp = (
        df2[df2['libelle_activite_benevole'] == activite]
          .groupby('structure_menant_activite_id')['nivol']
          .nunique()
          .reset_index(name='nb_benevoles_distincts')
    )

    var_name = make_var_name(activite)
    globals()[var_name] = df_tmp  # crée une variable df_<nom_simplifié>

    print(f"Créé : {var_name} (libelle_activite_benevole = {activite})")

    ##Definition pour calcul benevoles distincts
  
  # 2) Indicateur avec filtre
  activite_ben_cible = "Distribution alimentaire"
  Nb_benevoles_Distribution_alimentaire2 = nb_benevoles_distincts_gen(
      df2,
      filtre=f"libelle_activite_benevole == @activite_ben_cible"
  )

    # 2) Indicateur avec filtre
  activite_ben_cible = "Distribution alimentaire"
  Nb_benevoles_Distribution_alimentaire3 = nb_benevoles_distincts_mois_gen(
      df2,
      filtre=f"libelle_activite_benevole == @activite_ben_cible"
  )

  # 2) Indicateur avec filtre
  activite_ben_cible = "Distribution alimentaire"
  Nb_benevoles_Distribution_alimentaire4 = nb_benevoles_distincts_mois_DT_gen(
      df2,
      filtre=f"libelle_activite_benevole == @activite_ben_cible"
  )

  return Nb_benevoles_distincts, Nb_benevoles_Distribution_alimentaire, Nb_benevoles_Distribution_alimentaire1, Nb_benevoles_Distribution_alimentaire2, Nb_benevoles_Distribution_alimentaire3, Nb_benevoles_Distribution_alimentaire4








