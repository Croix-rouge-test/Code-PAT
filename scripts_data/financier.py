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


def import_clean_donnees_financieres(client,df_ref_structure, mapping_df):

  query_rattachement_benevole = """
    SELECT *
    FROM `crf-pat.dataset_PAT_2025.donnees_financieres_2025`
    """
  
    #SELECT rattachement_benevole_nivol_id_fk, rattachement_benevole_structure_id_fk
  financier = client.query(query_rattachement_benevole).to_dataframe().rename(columns={'N__Dept':'n_dept','N_structure':'n_structure','Type_structure':'type_structure'})
  df_financier = financier.rename(columns={'Produits_d_exploitation_2025' : 'Financier Prod_2025','Résultat_net_par_structure' : 'Financier ResNet_2025', 'Trésorerie_nette_par_structure' : "Financier TresoBrute_2025", 'Résultat_corrélé_au_Chiffres_d_affaire' : 'Financier ResCorrProd_2025'})
  df_financier = df_financier[['n_structure','Financier Prod_2025', 'Financier ResNet_2025', 'Financier TresoBrute_2025', 'Financier ResCorrProd_2025']].apply(pd.to_numeric, errors='coerce')


  df_financier_DT = financier[(financier['type_structure'] == 'DELEGATION DEPARTEMENTALE - DD') | (financier['type_structure'] == 'DELEGATION TERRITORIALE - DT')]
  df_financier_DT = df_financier_DT.rename(columns={'Produits_d_exploitation_consolidés__DT_' : 'Financier Prod_2025','Résultat_net_consolidé_par_DT' : 'Financier ResNet_2025', 'Trésorerie_nette_consolidée_par_DT' : "Financier TresoBrute_2025"})
  df_financier_DT = df_financier_DT[['n_structure','Financier Prod_2025', 'Financier ResNet_2025', 'Financier TresoBrute_2025']].apply(pd.to_numeric, errors='coerce')
  df_financier_DT['Financier ResCorrProd_2025'] = df_financier_DT['Financier ResNet_2025']/df_financier_DT['Financier Prod_2025']
  

  return df_financier, df_financier_DT, financier



def verifications_financiers(df_financier,df_financier_DT,df_ref_structure, financier):
 
    print('Vérificiations par structure :')
    verifier_colonne_structure(df_financier, "n_structure", df_ref_structure)

    print('')
    financier_struct_verif = financier[['Produits_d_exploitation_2025','Résultat_net_par_structure','Trésorerie_nette_par_structure']].apply(pd.to_numeric, errors='coerce').sum()

    if financier_struct_verif['Produits_d_exploitation_2025'] != df_financier['Financier Prod_2025'].sum():
        print(f"❌ la somme des produits d'exploitation par structure dans le dataframe ({df_financier['Financier Prod_2025'].sum()}) ne correspond pas à la somme des produits d'exploitation par structure dans les données financières ({financier_struct_verif['Produits_d_exploitation_2022']}).")
    elif financier_struct_verif['Résultat_net_par_structure'] != df_financier['Financier ResNet_2025'].sum():
        print(f"❌ la somme des résultats nets par structure dans le dataframe ({df_financier['Financier ResNet_2025'].sum()}) ne correspond pas à la somme des résultats nets par structure dans les données financières ({financier_struct_verif['Résultat_net_par_structure']}).")
    elif financier_struct_verif['Trésorerie_nette_par_structure'] != df_financier['Financier TresoBrute_2025'].sum():
        print(f"❌ la somme des trésoreries nettes par structure dans le dataframe ({df_financier['Financier TresoBrute_2025'].sum()}) ne correspond pas à la somme des trésoreries nettes par structure dans les données financières ({financier_struct_verif['Trésorerie_nette_par_structure']}).")
    else:
        print("✅ les sommes des produits d'exploitation par structure, des résultats nets par structure et des trésoreries nettes par structure dans le dataframe correspondent aux sommes correspondantes dans les données financières.")

    print('')
    print('Vérificiations par DT :')

    verifier_colonne_structure(df_financier_DT, "n_structure", df_ref_structure[df_ref_structure['type_structure'].str.contains('DT')])
    print('')
    financier_DT_verif = financier[['Produits_d_exploitation_consolidés__DT_','Résultat_net_consolidé_par_DT','Trésorerie_nette_consolidée_par_DT']].apply(pd.to_numeric, errors='coerce').sum()

    if financier_DT_verif['Produits_d_exploitation_consolidés__DT_'] != df_financier_DT['Financier Prod_2025'].sum():
        print(f"❌ la somme des produits d'exploitation consolidés par DT dans le dataframe ({df_financier_DT['Financier Prod_2025'].sum()}) ne correspond pas à la somme des produits d'exploitation consolidés par DT dans les données financières ({financier_DT_verif['Produits_d_exploitation_consolidés__DT_']}).")
    elif financier_DT_verif['Résultat_net_consolidé_par_DT'] != df_financier_DT['Financier ResNet_2025'].sum():
        print(f"❌ la somme des résultats nets par structure dans le dataframe ({df_financier_DT['Financier ResNet_2025'].sum()}) ne correspond pas à la somme des résultats nets par structure dans les données financières ({financier_DT_verif['Résultat_net_consolidé_par_DT']}).")
    elif financier_DT_verif['Trésorerie_nette_consolidée_par_DT'] != df_financier_DT['Financier TresoBrute_2025'].sum():
        print(f"❌ la somme des trésoreries nettes par structure dans le dataframe ({df_financier_DT['Financier TresoBrute_2025'].sum()}) ne correspond pas à la somme des trésoreries nettes par structure dans les données financières ({financier_DT_verif['Trésorerie_nette_consolidée_par_DT']}).")
    else:
        print("✅ les sommes des produits d'exploitation consolidés par DT, des résultats nets par structure et des trésoreries nettes par structure dans le dataframe correspondent aux sommes correspondantes dans les données financières.")

    


    








#################################################################
# 
# DPS ET FGP
# 
# ###############################################################





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
  df_financier_FGP_DT = pd.merge(df_ref_structure[df_ref_structure['type_structure'] == "DELEGATION TERRITORIALE - DT"][['DT_de_rattachement','n_dept']].drop_duplicates(), df_financier_FGP_DT, on = 'n_dept', how = 'inner')

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























