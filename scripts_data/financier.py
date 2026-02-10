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




def fusion_donnees_financieres(dt_prod, dt_resnet, dt_resnet_corr_prod, dt_treso_brute,dt_ul_ant_prod, dt_ul_ant_res_net, dt_ul_res_net_corr_prod, dt_ul_treso_brute):
  # Données par DT
  df_financier_DT = pd.merge(dt_prod, dt_resnet, on="n_dept", how="left")
  df_financier_DT = pd.merge(df_financier_DT, dt_resnet_corr_prod, on="n_dept", how="left")
  df_financier_DT = pd.merge(df_financier_DT, dt_treso_brute, on="n_dept", how="left")


  # Données par structures
  df_financier_DT_UL = pd.merge(dt_ul_ant_prod,dt_ul_ant_res_net, on="n_structure", how="left")
  df_financier_DT_UL = pd.merge(df_financier_DT_UL, dt_ul_res_net_corr_prod, on="n_structure", how="left")
  df_financier_DT_UL = pd.merge(df_financier_DT_UL, dt_ul_treso_brute, on="n_structure", how="left")


  # Pas de numéro de structure pour le dataframe contenant les DT, on fera le merge sur le numéro de département
  return df_financier_DT, df_financier_DT_UL


def verifier_n_dept(df_financier_DT,df_ref_structure):
 
  # Doublons
  doublons = df_financier_DT[df_financier_DT.duplicated(subset=['n_dept'])]
  if doublons.shape[0] > 0 :
    print(' ❌ Il y a des doublons :')
    display(df_financier_DT[df_financier_DT.duplicated(subset=['n_dept'])])
  else :
    print(' ✅ Aucun doublon')


  # Taille des données
  if df_financier_DT['n_dept'].shape[0] == 107 :
    print(' ✅ Pas de département manquant')
  else :
    print(' ❌ Il manque des départements : ')
    manquants_financier = set(df_financier_DT['n_dept'])
    manquants_struct = set(df_ref_structure['n_dept'])
    manquants = manquants_financier.union(manquants_struct) - manquants_struct.intersection(manquants_financier)
    print(manquants)


def clean_financier_DPS(financier_DPS):
    # Renommer les colonnes
    financier_DPS.columns.values[0] = 'code_comptable'
    financier_DPS.columns.values[1] = 'libelle'
    financier_DPS.columns.values[3] = 'année'
    financier_DPS.columns.values[4] = 'imputation_comptable'


    # Filtrer sur la bonne année
    df = financier_DPS[financier_DPS['année'] == "2024"]


    # Filtrer sur l'activité DPS
    df = df[df['imputation_comptable'] == "ACTA204"]


    # Extraire le département
    def extraire_et_nettoyer_code_departement(texte):
        code = texte[-3:] # Extraire les 3 derniers caractères
        code = code.lstrip('0') # Supprimer les zéros initiaux
        return code
    df['Code Département'] = df['code_comptable'].apply(extraire_et_nettoyer_code_departement)


    # Suppression de la ligne nationnale
    df = df[df["libelle"] != "TOTAL DELEGATION"]


    # Suppression des doublons (corse)
    df = df.drop_duplicates(subset=['Code Département'], keep='first')


    # Conserver les colonnes utiles
    df = df[["code_comptable","libelle","Code Département","année","imputation_comptable","PRODUITS DES POSTES SECOURS"]]
    return df




def clean_financier_FGP(financier_FGP):




    # Conservation des colonnes utiles
    df = financier_FGP[["Nom Structure","PRODUITS DE FORMATIONS SCOLARITE ET DROITS D INSCRIPTION Réalisé 2024"]]
    return df
   


def clean_financier_FGP_DPS(
    financier_FGP,
    financier_DPS
):
    df_financier_FGP_clean = clean_financier_FGP(financier_FGP)
    df_financier_DPS_clean = clean_financier_DPS(financier_DPS)


    return (
        df_financier_FGP_clean,
        df_financier_DPS_clean,
    )




def indicateur_financier_DPS(financier_DPS, df_ref_structure):
    # Mapping sur le département
    mapping_dict = df_ref_structure[df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"].set_index('n_dept')['n_structure'].to_dict()
    financier_DPS['n_structure'] = financier_DPS['Code Département'].map(mapping_dict)
    #verifier_mapping(financier_DPS, "n_structure", "libelle" ,df_ref_structure)


    # Transformation des str en int
    financier_DPS['PRODUITS DES POSTES SECOURS'] = financier_DPS['PRODUITS DES POSTES SECOURS'].str.replace("€", "").str.replace("\u202f", "").str.replace(" ", "").replace("",0).astype(int)


    # Conserver les colonnes utiles
    financier_DPS = financier_DPS[["n_structure","PRODUITS DES POSTES SECOURS"]]


    # Modification du nom de colonne
    financier_DPS = financier_DPS.rename(columns={"PRODUITS DES POSTES SECOURS":"Secours Produits_DPS_2024"})
   
    return financier_DPS




def indicateur_financier_FGP(financier_FGP, df_ref_structure):
    # Recherche des correspondances vis à vis du référentiel structure
    df = rapprochement_libelles(df_ref_structure, financier_FGP, "Nom Structure")


    # Correction des écarts
    index_to_correct = df[df['Nom Structure'] == "PACA CORSE"].index[0]
    df.at[index_to_correct, 'n_structure'] = "3732"


    index_to_correct = df[df['Nom Structure'] == "GRAND EST"].index[0]
    df.at[index_to_correct, 'n_structure'] = "4455"


    # Conservation des colonnes utiles
    df = df[["PRODUITS DE FORMATIONS SCOLARITE ET DROITS D INSCRIPTION Réalisé 2024","N_structure"]]


    # Modification du nom des colonnes
    df = df.rename(columns={'PRODUITS DE FORMATIONS SCOLARITE ET DROITS D INSCRIPTION Réalisé 2024': 'Formation_grand_public CA_2024'})


    # Modification des données pour obtenir des int
    df['Formation_grand_public CA_2024'] = df['Formation_grand_public CA_2024'].str.replace(',', '').str.replace(' €', '').str.replace(' ', '').astype(int)


def indicateur_financier_FGP_DPS(
    financier_FGP,
    financier_DPS
):
    df_financier_FGP_indicateur = indicateur_financier_FGP(financier_FGP)
    df_financier_DPS_indicateur = indicateur_financier_DPS(financier_DPS)


    return (
        df_financier_FGP_indicateur,
        df_financier_DPS_indicateur,
    )




def financier_FGP_DT(df_financier_FGP_indicateur, rattachement_court):
    df_financier_FGP_indicateur['n_structure'] = df_financier_FGP_indicateur['n_structure'].astype('float64')
    # Merge données avec rattachement_court
    df_financier_FGP = pd.merge(
    df_financier_FGP_indicateur,
    rattachement_court,
    on="n_structure",
    how="left"
    )


    # Groupby sur DT_de_rattachement
    financier_FGP_DT = (df_financier_FGP.groupby('DT_de_rattachement')['Formation_grand_public CA_2024'].sum())
    return financier_FGP_DT




def financier_DPS_DT(df_financier_DPS_indicateur, rattachement_court):
    df_financier_DPS_indicateur['n_structure'] = df_financier_DPS_indicateur['n_structure'].astype('float64')
    # Merge données avec rattachement_court
    df_financier_DPS = pd.merge(
    df_financier_DPS_indicateur,
    rattachement_court,
    on="n_structure",
    how="left"
    )


    # Groupby sur DT_de_rattachement
    financier_DPS_DT = (df_financier_DPS.groupby('DT_de_rattachement')['Secours Produits_DPS_2024'].sum())
    return financier_DPS_DT









