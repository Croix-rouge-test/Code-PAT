import pandas as pd
import os
import re
import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *


def clean_nomination(client, df_ref_structure):
  query_ref_nomination = """
  SELECT *
  FROM crf-pat.dataset_PAT_2025.crf_nomination_ref_nomination
  """

  query_nomination = """
  SELECT *
  FROM crf-pat.dataset_PAT_2026.crf_pat_2026_nomination
  """
  df_ref_nomination = client.query(query_ref_nomination).to_dataframe()
  df_nomination = client.query(query_nomination).to_dataframe()
  # Vérification que la colonne est au format datetime
  df_nomination['nomination_date_fin_nomination'] = pd.to_datetime(df_nomination['nomination_date_fin_nomination'], errors='coerce')
  df_nomination['nomination_date_debut_nomination'] = pd.to_datetime(df_nomination['nomination_date_debut_nomination'], errors='coerce')
  _ , _ , _, df_nomination = apply_rattachement_successif(df_ref_structure, df_nomination, col = 'nomination_structure_id_fk')
  return df_ref_nomination, df_nomination


def fusion_nomination(df_nomination, df_ref_nomination, target_year=2025):
  #FTILRE SUR ANNEE NULLE OU FIN EN target_year


  # Filtrage : date nulle ou année = target_year
  df_nomination = df_nomination[
      df_nomination['nomination_date_fin_nomination'].isna() | (df_nomination['nomination_date_fin_nomination'].dt.year == target_year)
  ]


  df_NOMINATION = pd.merge(
     df_nomination,
     df_ref_nomination,
     left_on="nomination_nomination_id_fk",
     right_on="nomination_id_pk",
     how="left"
      )


  return df_NOMINATION




def indicateurs_nomination_AEO(df_NOMINATION,df_nivols_gaia, annee=2026):
    # Filtre sur les libellés appropriés
    libelles_AEO = ["RTAAD", "RLAAD", "RLACOR", "RLACORA"]
    referents_AEO = df_NOMINATION[
        df_NOMINATION["nomination_libcourt"].isin(libelles_AEO)
    ]

    liste_nivols_date_fixe = df_nivols_gaia['rattachement_benevole_nivol_id_fk'].drop_duplicates().tolist()
    referents_AEO = referents_AEO[referents_AEO['nomination_nivol_id_fk'].isin(liste_nivols_date_fixe)]

    # On compte le nb de RTAEO & RLAEO
    referents_AEO = (referents_AEO.groupby('nomination_structure_id_fk')['nomination_nivol_id_fk'].nunique().reset_index(name='AEO Nb_responsables'))
    referents_AEO = referents_AEO.rename(columns ={'nomination_structure_id_fk': 'n_structure'})
   
    print(f"Nombre de structures agrégées : {len(referents_AEO)}")

    # Somme totale nationale
    total_responsables = referents_AEO['AEO Nb_responsables'].sum()
    print(f"Nombre total de responsables AEO : {total_responsables}")
    
    return referents_AEO




def indicateurs_nomination_OCR(df_NOMINATION, df_nivols_gaia, annee=2026):
    # Filtre sur les libellés appropriés
    libelles_OCR = ["RTOCR", "RLOCR"]
    referents_OCR = df_NOMINATION[
        df_NOMINATION["nomination_libcourt"].isin(libelles_OCR)
    ]

    liste_nivols_date_fixe = df_nivols_gaia['rattachement_benevole_nivol_id_fk'].drop_duplicates().tolist()
    referents_OCR = referents_OCR[referents_OCR['nomination_nivol_id_fk'].isin(liste_nivols_date_fixe)]
    # On compte le nb de RTAEO & RLAEO
    referents_OCR = (referents_OCR.groupby('nomination_structure_id_fk')['nomination_nivol_id_fk'].nunique().reset_index(name='OCR Nb_referents'))
    referents_OCR = referents_OCR.rename(columns ={'nomination_structure_id_fk': 'n_structure'})

    print(f"Nombre de structures agrégées : {len(referents_OCR)}")

    # Somme totale nationale
    total_responsables = referents_OCR['OCR Nb_referents'].sum()
    print(f"Nombre total de responsables OCR : {total_responsables}")
    
    return referents_OCR




def indicateurs_nominationAEO_DT(referents_AEO, rattachement_court):
    # Merge données avec rattachement_court
    df_referents_AEO = pd.merge(
    referents_AEO,
    rattachement_court,
    on="n_structure",
    how="left"
    )

    # Groupby sur DT_de_rattachement
    referents_AEO_DT = (df_referents_AEO.groupby('DT_de_rattachement')['AEO Nb_responsables'].sum()).reset_index()
    
    print(f"Nombre de structures agrégées : {len(referents_AEO_DT)}")

    # Somme totale nationale
    total_responsables = referents_AEO_DT['AEO Nb_responsables'].sum()
    print(f"Nombre total de responsables AEO DT : {total_responsables}")

    return referents_AEO_DT




def indicateurs_nominationOCR_DT(referents_OCR, rattachement_court):
    # Merge données avec rattachement_court
    df_referents_OCR = pd.merge(
    referents_OCR,
    rattachement_court,
    on="n_structure",
    how="left"
    )


    # Groupby sur DT_de_rattachement
    referents_OCR_DT = (df_referents_OCR.groupby('DT_de_rattachement')['OCR Nb_referents'].sum()).reset_index()
    
    print(f"Nombre de structures agrégées : {len(referents_OCR_DT)}")

    # Somme totale nationale
    total_responsables = referents_OCR_DT['OCR Nb_referents'].sum()
    print(f"Nombre total de responsables OCR DT : {total_responsables}")

    return referents_OCR_DT











