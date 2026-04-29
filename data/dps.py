import os
import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *


def clean_dps(df_conventions):
    df = df_conventions[
        [
            'DT Annuaire Opé',
            'Departement',
            'Nb de vacations de 4h effectuées PAPS',
            'Nb de vacations de 4h effectuées DPS PE',
            'Nb de vacations de 4h effectuées DPS ME',
            'Nb de vacations de 4h effectuées DPS GE'
        ]
    ]

    df["Departement"] = df["Departement"].str.replace(
        r"DELEGATION DEPARTEMENTALE|DELEGATION TERRITORIALE",
        "DT",
        regex=True
    )

    df = df.rename(columns={'Code structure': 'n_structure'})

    return df




def indicateurs_dps(df_dps, df_ref_structure):
    
    df = df_dps[
        [
            "Departement",
            "Nb de vacations de 4h effectuées PAPS",
            "Nb de vacations de 4h effectuées DPS PE",
            "Nb de vacations de 4h effectuées DPS ME",
            "Nb de vacations de 4h effectuées DPS GE"
        ]
    ].copy()

    df = rapprochement_libelles(
        df_ref_structure,
        df,
        "Departement"
    )

    df = df.rename(
        columns={
            "Nb de vacations de 4h effectuées PAPS": "Secours Nb_PAPS_2025",
            "Nb de vacations de 4h effectuées DPS PE": "Secours Nb_DPS_PE_2025",
            "Nb de vacations de 4h effectuées DPS ME": "Secours Nb_DPS_ME_2025",
            "Nb de vacations de 4h effectuées DPS GE": "Secours Nb_DPS_GE_2025"
        }
    )

    # ✅ Somme ligne par ligne
    df["Secours Nb_DPS_2025"] = df[
        [
            "Secours Nb_PAPS_2025",
            "Secours Nb_DPS_PE_2025",
            "Secours Nb_DPS_ME_2025",
            "Secours Nb_DPS_GE_2025"
        ]
    ].sum(axis=1)

    # ✅ PRINT SOMME PAR COLONNE
    print("\n===== Somme globale par indicateur DPS =====")
    cols_sum = [
        "Secours Nb_PAPS_2025",
        "Secours Nb_DPS_PE_2025",
        "Secours Nb_DPS_ME_2025",
        "Secours Nb_DPS_GE_2025",
        "Secours Nb_DPS_2025"
    ]

    totals = df[cols_sum].sum()

    for col in totals.index:
        print(f"{col} : {totals[col]}")

    return df



def verifications_dps(df_conventions, df_indicateurs_dps):
  """ Vérifie que les sommes correspondent à la source des données puis à la 
  sortie du traitement

  """

  df_test_conv = df_conventions.copy().fillna(0)
  columns_to_check = [('Nb de vacations de 4h effectuées PAPS', 'Secours Nb_PAPS_2025'), ('Nb de vacations de 4h effectuées DPS PE', 'Secours Nb_DPS_PE_2025'), ('Nb de vacations de 4h effectuées DPS ME','Secours Nb_DPS_ME_2025'), ('Nb de vacations de 4h effectuées DPS GE', 'Secours Nb_DPS_GE_2025')]

  acc = 0
  for col_source, col_res in columns_to_check:
    if df_test_conv[col_source].sum() != df_indicateurs_dps[col_res].sum():
      print(f" ❌ PROBL {col_res} : source {df_test_conv[col_source].sum()} ≠ résultat {df_indicateurs_dps[col_res].sum()}")
    else :
      print(f"✅ OK {col_res} : {col_source} = {col_res}")
    acc += df_test_conv[col_source].sum()

  if acc == df_indicateurs_dps['Secours Nb_PAPS_2025'].sum():
    print(f" ❌ PROBL Secours Nb_PAPS_2025 : source {acc} ≠ résultat {df_indicateurs_dps['Secours Nb_PAPS_2025'].sum()}")
  else :
    print(f"✅ OK Secours Nb_PAPS_2025 : source = Secours Nb_PAPS_2025")
