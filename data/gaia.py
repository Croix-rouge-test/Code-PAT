import pandas as pd
import os
import re
import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *

def import_table_GAIA_date_fixe(client, target_date="2025-12-31", project_id="crf-pat"):
    """
    Charge la table GAIA nécessaires et renvoie le DataFrame importé.
    """
    target = pd.Timestamp(target_date)
    year = target.year

    dataset_id = f"dataset_PAT_{year}"

    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.crf_pat_{year}_rattachement_benevole`
    """

    df_rattachement_benevole = client.query(query).to_dataframe()
    df_rattachement_benevole["rattachement_benevole_date_fin"] = pd.to_datetime(df_rattachement_benevole["rattachement_benevole_date_fin"])

    df_rattachement_benevole["rattachement_benevole_date_debut"] = pd.to_datetime(
    df_rattachement_benevole["rattachement_benevole_date_debut"],
    errors="coerce"
    )

    df_rattachement_benevole = (
        df_rattachement_benevole
        .sort_values("rattachement_benevole_date_debut", ascending=False)
        .drop_duplicates(subset="rattachement_benevole_nivol_id_fk", keep="first")
        .copy()
    )

    df_rattachement_benevole = df_rattachement_benevole.drop_duplicates("rattachement_benevole_nivol_id_fk")

    target = pd.Timestamp(target_date)
    df_rattachement_benevole = df_rattachement_benevole.loc[
        (df_rattachement_benevole["rattachement_benevole_date_fin"].isna()
        | (df_rattachement_benevole["rattachement_benevole_date_fin"] >= target)) & (df_rattachement_benevole["rattachement_benevole_date_debut"]  <= target)
    ]
    
    df_rattachement_benevole = df_rattachement_benevole[["rattachement_benevole_nivol_id_fk"]]
    return df_rattachement_benevole

def clean_gaia(client, df_ref_structure, target_date="2025-12-31"):

  target = pd.Timestamp(target_date)
  year = target.year
  dataset_id = f"dataset_PAT_{year}"
  
  query_gaia = f"""
  SELECT *
  FROM crf-pat.{dataset_id}.crf_pat_{year}_rattachement_benevole
  """
  df_gaia_rattachement_benevole = client.query(query_gaia).to_dataframe()
  # Vérification que la colonne est au format datetime
  df_gaia_rattachement_benevole['rattachement_benevole_date_fin'] = pd.to_datetime(df_gaia_rattachement_benevole['rattachement_benevole_date_fin'], errors='coerce')
  df_gaia_rattachement_benevole['rattachement_benevole_date_debut'] = pd.to_datetime(df_gaia_rattachement_benevole['rattachement_benevole_date_debut'], errors='coerce')

  _ , _ , _, df_gaia_rattachement_benevole = apply_rattachement_successif(df_ref_structure, df_gaia_rattachement_benevole, col = 'rattachement_benevole_structure_id_fk')

  return df_gaia_rattachement_benevole



def indicateurs_gaia(df_gaia, target_date="2025-12-31"):

  # Filtrage : date nulle ou année = 2025
  df_gaia_rattachement_benevole = df_gaia.copy()

  df_gaia_rattachement_benevole["rattachement_benevole_date_debut"] = pd.to_datetime(
      df_gaia_rattachement_benevole["rattachement_benevole_date_debut"],
      errors="coerce"
  )

  df_gaia_rattachement_benevole = (
      df_gaia_rattachement_benevole
      .sort_values("rattachement_benevole_date_debut", ascending=False)
      .drop_duplicates(subset=["rattachement_benevole_nivol_id_fk"], keep="first")
      .reset_index(drop=True)
  )
  df_gaia_rattachement_benevole["rattachement_benevole_date_fin"] = pd.to_datetime(
    df_gaia_rattachement_benevole["rattachement_benevole_date_fin"], errors="coerce", dayfirst=True
  )

  # Filtre : date_fin = NaT OU = 31/12/2025
  target = pd.Timestamp(target_date)
  df_gaia_rattachement_benevole = df_gaia_rattachement_benevole.loc[
      (df_gaia_rattachement_benevole["rattachement_benevole_date_fin"].isna()
      | (df_gaia_rattachement_benevole["rattachement_benevole_date_fin"] >= target)) & (df_gaia_rattachement_benevole["rattachement_benevole_date_debut"]  <= target)
  ]
 
  df_gaia_rattachement_benevole = df_gaia_rattachement_benevole.rename(columns={
    'rattachement_benevole_structure_id_fk': 'n_structure',
    'rattachement_benevole_nivol_id_fk': 'Structure Nb_Benevoles'
  })
 # On compte le nb de volontaires de l'urgence
  nb_benevoles = (df_gaia_rattachement_benevole.groupby('n_structure')['Structure Nb_Benevoles'].nunique()).reset_index()
  
  print(f"Nombre de structures agrégées : {len(nb_benevoles)}")

  # Somme totale nationale
  total_benevoles = nb_benevoles['Structure Nb_Benevoles'].sum()
  print(f"Nombre total de bénévoles uniques : {total_benevoles}")
   
  return nb_benevoles










def indicateurs_gaia_nvx(df_gaia, target_date="2025-12-31"):
  # Conversion en datetime
  df_gaia['rattachement_benevole_date_fin'] = pd.to_datetime(
      df_gaia['rattachement_benevole_date_fin'], errors='coerce'
  )
  df_gaia['rattachement_benevole_date_debut'] = pd.to_datetime(
      df_gaia['rattachement_benevole_date_debut'], errors='coerce'
  )

  # garder uniquement les bénévoles dont la première apparition est en 2025
  first_dates = df_gaia.groupby('rattachement_benevole_nivol_id_fk')[
      'rattachement_benevole_date_debut'
  ].min()

  nivols_2025_only = first_dates[first_dates.dt.year == 2025].index

  df_gaia = df_gaia[
      df_gaia['rattachement_benevole_nivol_id_fk'].isin(nivols_2025_only)
  ]

  df_gaia = df_gaia[
      df_gaia['rattachement_benevole_date_debut'].dt.year == 2025
  ]

  target = pd.Timestamp(target_date)
  df_gaia = df_gaia.loc[
      (df_gaia["rattachement_benevole_date_fin"].isna()
      | (df_gaia["rattachement_benevole_date_fin"] >= target)) & (df_gaia["rattachement_benevole_date_debut"]  <= target)
  ]

  # Renommage
  df_gaia = df_gaia.rename(columns={
      'rattachement_benevole_structure_id_fk': 'n_structure',
      'rattachement_benevole_nivol_id_fk': 'Structure Nb_nvx_Benevoles_2025'
  })

  # Agrégation
  nb_nvx_benevoles = (
      df_gaia.groupby('n_structure')['Structure Nb_nvx_Benevoles_2025']
      .nunique()
      .reset_index()
  )

  print(f"Nombre de structures agrégées : {len(nb_nvx_benevoles)}")

  # Total national
  total_nvx_benevoles = nb_nvx_benevoles['Structure Nb_nvx_Benevoles_2025'].sum()
  print(f"Nombre total de nouveaux bénévoles uniques : {total_nvx_benevoles}")
  
  return nb_nvx_benevoles










def indicateurs_gaia_DT(nb_benevoles, rattachement_court):
    # Merge données avec rattachement_court
    df_nb_benevoles = pd.merge(
    nb_benevoles,
    rattachement_court,
    on="n_structure",
    how="left"
    )


    # Groupby sur DT_de_rattachement
    nb_benevoles_DT = (df_nb_benevoles.groupby('DT_de_rattachement')['Structure Nb_Benevoles'].sum()).reset_index()
    
    print(f"Nombre de structures agrégées : {len(nb_benevoles_DT)}")

    # Somme totale nationale
    total_benevoles_DT = nb_benevoles_DT['Structure Nb_Benevoles'].sum()
    print(f"Nombre total de bénévoles uniques DT : {total_benevoles_DT}")

    return nb_benevoles_DT








def indicateurs_gaia_nvx_DT(nb_nvx_benevoles, rattachement_court):
    # Merge données avec rattachement_court
    df_nb_nvx_benevoles = pd.merge(
    nb_nvx_benevoles,
    rattachement_court,
    on="n_structure",
    how="left"
    )


    # Groupby sur DT_de_rattachement
    nb_nvx_benevoles_DT = (df_nb_nvx_benevoles.groupby('DT_de_rattachement')['Structure Nb_nvx_Benevoles_2025'].sum()).reset_index()
    
    print(f"Nombre de structures agrégées : {len(nb_nvx_benevoles_DT)}")

    # Somme totale nationale
    total_nvx_benevoles_DT = nb_nvx_benevoles_DT['Structure Nb_nvx_Benevoles_2025'].sum()
    print(f"Nombre total de nouveaux bénévoles uniques DT : {total_nvx_benevoles_DT}")
    
    return nb_nvx_benevoles_DT


def taux_nvx_benevoles(nb_benevoles, nb_nvx_benevoles, nb_benevoles_DT, nb_nvx_benevoles_DT, year):

    """Calcul du taux de nouveaux bénévoles par DT et au niveau national et merge les autres indicateurs dans un unique dataframe"""

    # Merge des deux DataFrames sur DT_de_rattachement
    df_merge = pd.merge(
        nb_benevoles_DT,
        nb_nvx_benevoles_DT,
        on="n_structure",
        how="outer"
    )

    # Calcul du taux de nouveaux bénévoles
    df_merge["Structure Taux_nvx_Benevoles"] = (df_merge[f"Structure Nb_nvx_Benevoles_{year}"] / df_merge["Structure Nb_Benevoles"]) * 100

    # Merge des deux DataFrames sur DT_de_rattachement
    df_merge_DT = pd.merge(
        nb_benevoles_DT,
        nb_nvx_benevoles_DT,
        on="DT_de_rattachement",
        how="outer"
    )

    # Calcul du taux de nouveaux bénévoles
    df_merge_DT["Structure Taux_nvx_Benevoles"] = (df_merge_DT[f"Structure Nb_nvx_Benevoles_{year}"] / df_merge_DT["Structure Nb_Benevoles"]) * 100

    return df_merge, df_merge_DT

def calcul_indicateurs_gaia(df_gaia_rattachement_benevole,rattachement_court,year):
    nb_benevoles = indicateurs_gaia(df_gaia_rattachement_benevole)
    nb_nvx_benevoles = indicateurs_gaia_nvx(df_gaia_rattachement_benevole)
    nb_benevoles_DT = indicateurs_gaia_DT(nb_benevoles,rattachement_court)
    nb_nvx_benevoles_DT = indicateurs_gaia_nvx_DT(nb_nvx_benevoles, rattachement_court)
    df_indicateurs_gaia,df_indicateurs_gaia_DT = taux_nvx_benevoles(nb_benevoles, nb_nvx_benevoles, nb_benevoles_DT, nb_nvx_benevoles_DT, year)
    return df_indicateurs_gaia, df_indicateurs_gaia_DT







