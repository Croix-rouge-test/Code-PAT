import pandas as pd
import os
import sys
import unicodedata
import re

sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *

def  Import_Maraude_manuel(client,df_ref_structure):
  # Import
  query = """
    SELECT *
    FROM `crf-pat.dataset_PAT_2025.Maraude_manuelle`
    """
  df_Maraude_donnees_manuelles = client.query(query).to_dataframe()

    #Rapprochement libelles (Move this block up)
  df_Maraude_donnees_manuelles.columns = [unicodedata.normalize('NFKD', col).encode('ascii', 'ignore').decode('utf-8').strip() for col in df_Maraude_donnees_manuelles.columns]

  #Netoyage de la base
  df_Maraude_donnees_manuelles = df_Maraude_donnees_manuelles[~df_Maraude_donnees_manuelles["Departement"].astype(str).str.contains("Total", case=False, na=False)].copy()

  to_drop = {
      "SAMUSO EQUIPE MOBILE DE GUADELOUPE",
      "SEMISS DE LA DROME",
      "SEMISS DE L'AIN",
  }

  df_Maraude_donnees_manuelles = df_Maraude_donnees_manuelles[
      ~df_Maraude_donnees_manuelles["Structure"].astype(str).str.strip().isin(to_drop)
  ].copy()

  df_Maraude_donnees_manuelles["Structure"] = df_Maraude_donnees_manuelles["Structure"].astype(str).map(normalize_structure)
  df_Maraude_donnees_manuelles = rapprochement_libelles(df_ref_structure, df_Maraude_donnees_manuelles, "Structure")

  #Rename des colonnes :
  df_Maraude_donnees_manuelles = df_Maraude_donnees_manuelles.rename(columns={
      "Nb maraude": "Maraude Nb_maraudes_SIGMA",
      "Nb Personnes differentes": "Maraude Nb_personnes_rencontrees",
      "Nb contacts": "Maraude Nb_contacts",
  })

  df_Maraude_donnees_manuelles.loc[
      df_Maraude_donnees_manuelles["Structure"].astype(str).str.strip() == "UL DE CONCARNEAU AVEN MOROS",
      "n_structure"
  ] = 2315

  df_Maraude_donnees_manuelles.loc[
      df_Maraude_donnees_manuelles["Structure"].astype(str).str.strip() == "UL DE COLOMIERS",
      "n_structure"
  ] = 419


  

  return df_Maraude_donnees_manuelles



def calcul_indic_maraude_manuelles(df_ref_structure, df_Maraude_donnees_manuelles, df_rattachement_court):

  # df_Maraude_donnees_manuelles_2 = df_Maraude_donnees_manuelles.copy()
  # df_Maraude_donnees_manuelles_2['n_structure'] = pd.to_numeric(df_Maraude_donnees_manuelles_2['n_structure'], errors='coerce')
  # df_Maraude_donnees_manuelles_2['n_structure'] = df_Maraude_donnees_manuelles_2['n_structure'].astype(int)

  #rattachement successif
  df_Maraude_donnees_manuelles_2 = apply_rattachement_successif(df_ref_structure, df_Maraude_donnees_manuelles, col="n_structure")

  df_Maraude_donnees_manuelles_2['n_structure'] = df_Maraude_donnees_manuelles_2['n_structure'].astype(int)

  #Rajout structure de ratachement
  df_Maraude_donnees_manuelles_2 = pd.merge(df_Maraude_donnees_manuelles_2, df_rattachement_court, on='n_structure', how="left")

  #Réorganisation de la base

  df_Maraude_donnees_manuelles_DT = df_Maraude_donnees_manuelles_2[['DT_de_rattachement',"Maraude Nb_maraudes_SIGMA", "Maraude Nb_personnes_rencontrees", "Maraude Nb_contacts",]]
  df_Maraude_donnees_manuelles_2 = df_Maraude_donnees_manuelles_2[['n_structure', "Maraude Nb_maraudes_SIGMA", "Maraude Nb_personnes_rencontrees", "Maraude Nb_contacts",]]

  #Calcul maraude manuelle DT
  df_Maraude_donnees_manuelles_DT_2 = (
      df_Maraude_donnees_manuelles_DT
        .groupby("DT_de_rattachement", as_index=False)[
            ["Maraude Nb_maraudes_SIGMA",
            "Maraude Nb_personnes_rencontrees",
            "Maraude Nb_contacts"]
        ]
        .sum()
  )

  #Calcul maraude manuelle structure
  df_Maraude_donnees_manuelles_structure_2 = (
      df_Maraude_donnees_manuelles_2.groupby("n_structure", as_index=False)[[
      "Maraude Nb_maraudes_SIGMA",
      "Maraude Nb_personnes_rencontrees",
      "Maraude Nb_contacts",
  ]].sum())

  return df_Maraude_donnees_manuelles_DT_2, df_Maraude_donnees_manuelles_structure_2

def check_maraude_sums(df, df2):
    cols = [
        "Maraude Nb_maraudes_SIGMA",
        "Maraude Nb_personnes_rencontrees",
        "Maraude Nb_contacts",
    ]
    diff = df[cols].sum(numeric_only=True) - df2[cols].sum(numeric_only=True)

    if (diff == 0).all():
        print("✅ OK — sommes identiques (diff = 0)")
    else:
        diff_ko = diff[diff != 0]
        print("❌ KO — différences sur : " + ", ".join(diff_ko.index.tolist()))
        print(diff_ko)

    return diff