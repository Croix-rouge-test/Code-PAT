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

# Clean
def dept_clean(x):
  if x == '2A' or x == '2B':
    return str(x)
  else : return str(int(x))


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
  
  dt_ul_ant_prod['n_structure'] = dt_ul_ant_prod['n_structure'].astype(int)
  dt_ul_ant_res_net['n_structure'] = dt_ul_ant_res_net['n_structure'].astype(int)
  dt_ul_res_net_corr_prod['n_structure'] = dt_ul_res_net_corr_prod['n_structure'].astype(int)
  dt_ul_treso_brute['n_structure'] = dt_ul_treso_brute['n_structure'].astype(int)

  mask = dt_ul_ant_prod['n_structure'].isin(set(df_ref_structure['n_structure'].drop_duplicates().values))
  dt_ul_ant_prod = dt_ul_ant_prod[mask]




  return dt_prod, dt_resnet, dt_resnet_corr_prod, dt_treso_brute, dt_ul_ant_prod, dt_ul_ant_res_net, dt_ul_res_net_corr_prod, dt_ul_treso_brute








def fusion_donnees_financieres(dt_prod, dt_resnet, dt_resnet_corr_prod, dt_treso_brute,dt_ul_ant_prod, dt_ul_ant_res_net, dt_ul_res_net_corr_prod, dt_ul_treso_brute, df_ref_structure):
  # Données par DT
  df_financier_DT = pd.merge(dt_prod, dt_resnet, on="n_dept", how="left")
  df_financier_DT = pd.merge(df_financier_DT, dt_resnet_corr_prod, on="n_dept", how="left")
  df_financier_DT = pd.merge(df_financier_DT, dt_treso_brute, on="n_dept", how="left")




  # Données par structures
  df_financier_DT_UL = pd.merge(dt_ul_ant_prod,dt_ul_ant_res_net, on="n_structure", how="left")
  df_financier_DT_UL = pd.merge(df_financier_DT_UL, dt_ul_res_net_corr_prod, on="n_structure", how="left")
  df_financier_DT_UL = pd.merge(df_financier_DT_UL, dt_ul_treso_brute, on="n_structure", how="left")

  df_financier_DT = pd.merge(df_ref_structure[['DT_de_rattachement','n_dept']].drop_duplicates(), df_financier_DT, on = 'n_dept', how = 'inner')
  df_financier_DT = df_financier_DT.drop_duplicates(['DT_de_rattachement'])

  _ , _ , _, df_financier_DT_UL = apply_rattachement_successif(df_ref_structure, df_financier_DT_UL, col = 'n_structure')

  # masque sur le groupe particulier
  mask = df_financier_DT_UL['n_structure'] == 4381
  df_subset = df_financier_DT_UL.loc[mask].copy()

  # filtrer la ligne UL ou DT pour Treso et Mois_Avance
  mask_dt_ul = df_subset['libelle_structure'].str.contains('DT|UL', case=False, na=False)
  df_dt_ul = df_subset.loc[mask_dt_ul]

  # récupérer la valeur si elle existe, sinon NaN
  treso_non_na = df_dt_ul['Financier TresoBrute_2024'].dropna()
  treso_value = treso_non_na.iloc[0] if not treso_non_na.empty else np.nan

  avance_non_na = df_dt_ul['Financier Mois_AvanceTreso_2024'].dropna()
  avance_value = avance_non_na.iloc[0] if not avance_non_na.empty else np.nan

  # somme pour Prod et ResNet
  prod_sum = df_subset['Financier Prod_2024'].sum()
  resnet_sum = df_subset['Financier ResNet_2024'].sum()

  # recalcul du ratio uniquement si agrégation réelle
  rescorr = resnet_sum / prod_sum if len(df_subset) > 1 and prod_sum != 0 else df_subset['Financier ResCorrProd_2024'].iloc[0]

  # mise à jour du dataframe original
  df_financier_DT_UL.loc[mask, 'Financier Prod_2024'] = prod_sum
  df_financier_DT_UL.loc[mask, 'Financier ResNet_2024'] = resnet_sum
  df_financier_DT_UL.loc[mask, 'Financier ResCorrProd_2024'] = rescorr
  df_financier_DT_UL.loc[mask, 'Financier TresoBrute_2024'] = treso_value
  df_financier_DT_UL.loc[mask, 'Financier Mois_AvanceTreso_2024'] = avance_value

  df_financier_DT_UL = df_financier_DT_UL.drop_duplicates(subset=['n_structure'], keep='first')



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




















































def indicateur_financier_DPS(financier_DPS, df_ref_structure):
    # Filtrer sur la bonne année
  df_Secours_ProduitsDPS = financier_DPS[financier_DPS['annee'] == 2024]




  # Filtrer sur l'activité DPS
  df_Secours_ProduitsDPS = df_Secours_ProduitsDPS[df_Secours_ProduitsDPS['imputation_comptable'] == "ACTA204"]




  # Extraire le département
  def extraire_et_nettoyer_code_departement(texte):
      code = texte[-3:] # Extraire les 3 derniers caractères
      code = code.lstrip('0') # Supprimer les zéros initiaux
      return code
  df_Secours_ProduitsDPS['Code Département'] = df_Secours_ProduitsDPS['code_comptable'].apply(extraire_et_nettoyer_code_departement)




  # Suppression de la ligne nationnale
  df_Secours_ProduitsDPS = df_Secours_ProduitsDPS[df_Secours_ProduitsDPS["libelle"] != "TOTAL DELEGATION"]




  # Suppression des doublons (corse)
  df_Secours_ProduitsDPS = df_Secours_ProduitsDPS.drop_duplicates(subset=['Code Département'], keep='first')




  # Conserver les colonnes utiles
  df_Secours_ProduitsDPS = df_Secours_ProduitsDPS[["code_comptable","libelle","Code Département","annee","imputation_comptable","PRODUITS DES POSTES SECOURS"]]



  # Mapping sur le département
  mapping_dict = df_ref_structure[df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"].set_index('n_dept')['n_structure'].to_dict()
  df_Secours_ProduitsDPS['n_structure'] = df_Secours_ProduitsDPS['Code Département'].map(mapping_dict)
  verifier_mapping(df_Secours_ProduitsDPS, "n_structure", "libelle" ,df_ref_structure)




  # Transformation des str en int
  financier_DPS['PRODUITS DES POSTES SECOURS'] = (
      financier_DPS['PRODUITS DES POSTES SECOURS']
          .astype(str)
          .str.replace("€", "", regex=False)
          .str.replace("\u202f", "", regex=False)  # espace insécable fin
          .str.replace(" ", "", regex=False)
          .replace("nan", 0)
          .replace("", 0)
          .pipe(pd.to_numeric, errors="coerce")
          .fillna(0)
          .astype(int)
  )




  # Conserver les colonnes utiles
  df_Secours_ProduitsDPS = df_Secours_ProduitsDPS[["n_structure","PRODUITS DES POSTES SECOURS"]]




  # Modification du nom de colonne
  df_Secours_ProduitsDPS = df_Secours_ProduitsDPS.rename(columns={"PRODUITS DES POSTES SECOURS":"Secours Produits_DPS_2025"})




  return df_Secours_ProduitsDPS
















def indicateur_financier_FGP(financier_FGP, df_ref_structure):
  mapping_dict = df_ref_structure[df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"].set_index('n_dept')['n_structure'].to_dict()

  # Suppression de la ligne nationnale
  df_financier_FGP_DT = financier_FGP[financier_FGP["Nom Structure"] != "Total"]
  df_financier_FGP_DT = df_financier_FGP_DT[df_financier_FGP_DT["N° Structure"] != "Source: Smartview-Mise à jour 24 mars 2025"]
  df_financier_FGP_DT = df_financier_FGP_DT.dropna(subset=["Nom Structure"])
  df_financier_FGP_DT = df_financier_FGP_DT.rename(columns={"N° Structure": "n_dept"})
  df_financier_FGP_DT = df_financier_FGP_DT.iloc[:df_financier_FGP_DT.shape[0]-2]
  df_financier_FGP_DT["n_dept"] = df_financier_FGP_DT["n_dept"].astype('str')

  df_ref_structure["n_dept"] = df_ref_structure["n_dept"].astype('str')

    
  df_financier_FGP_DT["Nom Structure"] = "DT " + df_financier_FGP_DT["Nom Structure"].astype(str)
  df_financier_FGP_DT['n_dept'] = df_financier_FGP_DT['n_dept'].apply(dept_clean)
  df_financier_FGP_DT = pd.merge(df_ref_structure[['DT_de_rattachement','n_dept']].drop_duplicates(), df_financier_FGP_DT, on = 'n_dept', how = 'inner')

  df_financier_FGP_DT = df_financier_FGP_DT.drop_duplicates(['DT_de_rattachement'])
  # financier_FGP = rapprochement_libelles(
  #     df_ref_structure,
  #     financier_FGP,
  #     "Nom Structure"
  # )
  df_financier_FGP_DT = df_financier_FGP_DT.rename(columns={
    'Réalisé 2024 Total Année': 'Formation_grand_public CA_2024' ,
    'DT_de_rattachement' : 'n_structure'
  })
  # Conserver les colonnes utiles

  df_financier_FGP_DT = df_financier_FGP_DT[["n_structure",'n_dept',"Formation_grand_public CA_2024"]]
  df_financier_FGP_DT = df_financier_FGP_DT.rename(columns = {'Formation_grand_public CA_2024' : 'Formation_grand_public Produits_2025'})


  #verifier_mapping(financier_FGP, "n_structure", "Nom Structure" ,df_ref_structure)
  return df_financier_FGP_DT














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
    financier_FGP_DT = (df_financier_FGP.groupby('DT_de_rattachement')['Formation_grand_public Produits_2025'].sum())
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
    financier_DPS_DT = (df_financier_DPS.groupby('DT_de_rattachement')['Secours Produits_DPS_2025'].sum())
    return financier_DPS_DT























