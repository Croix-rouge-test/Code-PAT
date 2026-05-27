from gspread_dataframe import get_as_dataframe
import pandas as pd
import os
import numpy as np
import re
import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *

def filtres_mobilite(mobilite,mapping_df, df_ref_structure):
  # Filtres et traitement de données
  mobilite = get_as_dataframe(mobilite.worksheet('Consolidation 2025'), evaluate_formulas=True)
  mobilite = mobilite[(mobilite['Etat'] == 'Actif') & (mobilite['Code structure unifié'] != '') & (mobilite['Code structure unifié'].notna())]
  mobilite = renommer_par_nom_table(mobilite[["N Département ","Code structure unifié","Nombre Bénéficiaires/an", "Nombre de volontaires total"]], "Mobilité", mapping_df)
  mobilite['n_structure'] = mobilite['n_structure'].astype(int)




  mobilite['nb_pa'] = mobilite['nb_pa'].astype(str).apply(keep_integer).str.replace('^$','0',regex = True).astype(int)
  mobilite['nb_bene'] = mobilite['nb_bene'].astype(str).apply(keep_integer).str.replace('^$','0',regex = True).astype(int)
  mobilite = mobilite.drop(['nb_bene'], axis = 1)

  mobilite = apply_rattachement_successif(df_ref_structure, mobilite, col = 'n_structure')

  return mobilite


def indicateurs_mobilite(df_mobilite, df_ref_structure, col_structure):
    mobilite_dt = dt_rattachement(df_mobilite, df_ref_structure).copy()
    mobilite_dt = pd.merge(mobilite_dt, df_ref_structure['n_structure'].drop_duplicates(), on='n_structure', how="inner")

    # structure d'origine pour compter les structures distinctes
    mobilite_dt['n_structure_origine'] = pd.to_numeric(
        mobilite_dt['n_structure'], errors='coerce'
    )

    if col_structure != 'n_structure':
        mobilite_dt[col_structure] = (
            mobilite_dt[col_structure]
            .astype(str)
            .str.strip()
            .replace('', np.nan)
        )

        mobilite_dt[col_structure] = pd.to_numeric(
            mobilite_dt[col_structure], errors='coerce'
        )

        mobilite_dt = mobilite_dt[mobilite_dt[col_structure].notna()].copy()
        mobilite_dt['n_structure'] = mobilite_dt[col_structure].astype(int)

    else:
        mobilite_dt['n_structure'] = pd.to_numeric(
            mobilite_dt['n_structure'], errors='coerce'
        )
        mobilite_dt = mobilite_dt[mobilite_dt['n_structure'].notna()].copy()
        mobilite_dt['n_structure'] = mobilite_dt['n_structure'].astype(int)

    mobilite_dt['n_structure_origine'] = mobilite_dt['n_structure_origine'].astype(int)

    dt_return = (
        mobilite_dt.groupby('n_structure', as_index=False)
        .agg(
            **{
                'AEO Structure_activite_mobile': ('n_structure_origine', 'nunique'),
                'AEO Nb_PA_dispos_mobiles': ('nb_pa', 'sum')
            }
        )
    )

    return dt_return




