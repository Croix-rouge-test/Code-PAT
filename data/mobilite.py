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
    AEO_mobile = ["Accès aux droits et Orientation", "Lien social"]
    pattern_aeo = "|".join(map(re.escape, AEO_mobile))

    mobilite = get_as_dataframe(mobilite.worksheet('Consolidation 2026'), evaluate_formulas=True)    #mobilite = mobilite[(mobilite['Etat'] == 'Actif') & (mobilite['Code structure unifié'] != '') & (mobilite['Code structure unifié'].notna()) & (mobilite['Typologie des CRsr/trajets'].isin(AEO_mobile))]

    mobilite = mobilite[
        (mobilite['Etat'] == 'Actif')
        & (mobilite['Code structure unifié'] != '')
        & (mobilite['Code structure unifié'].notna())
        & (
            mobilite['Typologie des CRsr/trajets']
            .fillna('')
            .str.contains(pattern_aeo, case=False, regex=True)
        )
    ]

    mobilite = renommer_par_nom_table(mobilite[["N Département ","Code structure unifié","Nombre Bénéficiaires/an", "Nombre de volontaires total"]], "Mobilité", mapping_df)
    mobilite['n_structure'] = mobilite['n_structure'].astype(int)
 
    mobilite['nb_pa'] = mobilite['nb_pa'].astype(str).apply(keep_integer).str.replace('^$','0',regex = True).astype(int)
    mobilite['nb_bene'] = mobilite['nb_bene'].astype(str).apply(keep_integer).str.replace('^$','0',regex = True).astype(int)
    mobilite = mobilite.drop(['nb_bene'], axis = 1)

    mobilite.loc[mobilite["n_structure"] == 989, "n_structure"] = 4391

    df_ref_structure = df_ref_structure[['n_structure', 'n_structure-ratt', 'DT_de_rattachement']]
    
    mobilite = pd.merge(mobilite, df_ref_structure, on='n_structure', how="inner")

    return mobilite

def indicateurs_mobilite(df_mobilite, df_ref_structure):

    df_ref_structure = df_ref_structure[['n_structure', 'n_structure-ratt', 'DT_de_rattachement']]

    mobilite_struct = df_mobilite[["n_structure-ratt","nb_pa"]].copy()

    mobilite_struct = (
        mobilite_struct.groupby('n_structure-ratt', as_index=False)
        .agg(
            **{
                'AEO Structure_activite_mobile': ('n_structure-ratt', 'nunique'),
                'AEO Nb_PA_dispos_mobiles': ('nb_pa', 'sum'),
                'AEO Nb_activites_mobiles': ('n_structure-ratt', 'size')
            }
        )
    )

    mobilite_struct.rename(columns={'n_structure-ratt': 'n_structure'}, inplace=True)

    mobilite_DT = pd.merge(mobilite_struct, df_ref_structure, on='n_structure', how="left")

    mobilite_DT = (
        mobilite_DT.groupby('DT_de_rattachement', as_index=False)
        .agg(
            **{
                'AEO Structure_activite_mobile': ('AEO Structure_activite_mobile', 'sum'),
                'AEO Nb_PA_dispos_mobiles': ('AEO Nb_PA_dispos_mobiles', 'sum'),
                'AEO Nb_activites_mobiles': ('AEO Nb_activites_mobiles', 'sum')
            }
        )
    )

    return mobilite_DT, mobilite_struct


