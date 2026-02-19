import traceback
import pandas as pd
from google.colab import auth
from google.auth import default
import unicodedata
import re
import torch
import os
from sentence_transformers import SentenceTransformer, util
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
