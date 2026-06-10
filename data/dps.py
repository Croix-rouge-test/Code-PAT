import os
import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *
from functools import reduce
import pandas as pd
import numpy as np

def import_clean_dps(client, df_ref_structure,target_date = '2025-12-31',  project_id="crf-pat"):
    target = pd.Timestamp(target_date)
    year = target.year

    dataset_id = f"dataset_PAT_{year}"

    # ---- Imports ----
    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.crf_pat_{year}_dps_dimensionnement`
    """
    df_dps_dimensionnement = client.query(query).to_dataframe()

    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.crf_pat_{year}_dps_manifestation`
    """
    df_dps_manifestation = client.query(query).to_dataframe()

    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.crf_pat_{year}_dps_ref_type_dispositif`
    """
    df_dps_ref_type_dispositif = client.query(query).to_dataframe()

    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.crf_pat_{year}_dps_ref_type_statut_demande`
    """
    df_dps_ref_type_statut_demande = client.query(query).to_dataframe()

    # Filtre sur l'année et début de l'opération antérieur ou égale à la date cible
    df_dps_dimensionnement['DPS_DIMENSIONNEMENT_DATE_DEBUT'] = pd.to_datetime(df_dps_dimensionnement['DPS_DIMENSIONNEMENT_DATE_DEBUT'], errors='coerce')

    df_dps_dimensionnement = df_dps_dimensionnement[(df_dps_dimensionnement['DPS_DIMENSIONNEMENT_DATE_DEBUT'].dt.year == year) & (df_dps_dimensionnement['DPS_DIMENSIONNEMENT_DATE_DEBUT'] <= target)]

    df_dps_manifestation = df_dps_manifestation.rename(columns = {"DPS_DEMANDE_STRUCTURE_ID":"n_structure"})

    liste_structure_garder = df_ref_structure[df_ref_structure['type_structure'] != 'IMPLANTATION LOCALE HORS AL - IL']['n_structure'].drop_duplicates().tolist()
    
    df_dps_manifestation = apply_rattachement_successif(
        df_ref_structure, df_dps_manifestation, "n_structure"
    )

    # Merge DT_de_rattachement APRÈS le rattachement successif
    df_dps_manifestation = df_dps_manifestation.drop(columns=['DT_de_rattachement'], errors='ignore')

    df_dps_manifestation = df_dps_manifestation[
        df_dps_manifestation['n_structure'].isin(liste_structure_garder)
    ]

    df_dps_manifestation = pd.merge(
        df_dps_manifestation,
        df_ref_structure[['n_structure', 'DT_de_rattachement']].drop_duplicates(),
        on="n_structure",
        how="left"
    )

    return df_dps_dimensionnement, df_dps_manifestation, df_dps_ref_type_dispositif, df_dps_ref_type_statut_demande


def nb_dps(df_dps, target_date, col_grpby):
    """" 
    Calcul les indicateurs suivantes :
    Secours Nb_PAPS_
    Secours Nb_DPS_PE_
    Secours Nb_DPS_ME_
    Secours Nb_DPS_GE_
    """

    target = pd.Timestamp(target_date)
    year = target.year

    # df_res = pd.DataFrame(index=[0])

    indics_mask = [(f"Secours Nb_PAPS_{year}", df_dps['TYPE_DISPOSITIF_LIBELLE'] == "PAPS"),
                    (f"Secours Nb_DPS_PE_{year}", df_dps['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de petite envergure"),
                    (f"Secours Nb_DPS_ME_{year}", df_dps['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de moyenne envergure"),
                    (f"Secours Nb_DPS_GE_{year}", df_dps['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de grande envergure"),
                    (f"Secours Nb_DPS_{year}", (df_dps['TYPE_DISPOSITIF_LIBELLE'] == "PAPS") |
                     (df_dps['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de petite envergure") | 
                     (df_dps['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de moyenne envergure") |
                     (df_dps['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de grande envergure"))]

    df_res = pd.DataFrame()
    frames = []

    for col, mask in indics_mask:
        serie = (
            df_dps[mask]
            .groupby(col_grpby)["DPS_DIMENSIONNEMENT_ID_PK"]
            .nunique()
            .rename(col)
            .reset_index()
        )

        frames.append(serie)

    # Merge successif sur n_structure — aucune structure perdue
    df_res = frames[0][[col_grpby]].copy()
    for frame in frames:
        df_res = df_res.merge(frame, on=col_grpby, how='outer')

    df_res = df_res.fillna(0).astype({col: int for col in df_res.columns if col != col_grpby})
    
    return df_res

def equivalent_poste_secours(df_dps, target_date, col_grpby):
    """" 
    Calcul les indicateurs suivantes :
    Secours Nb_PAPS_ps
    Secours Nb_DPS_PE_ps
    Secours Nb_DPS_ME_ps
    Secours Nb_DPS_GE_ps

    Correspond aux équivalents poste de secours, calculés avec la formule suivante :
    Equivalent poste de secours = ceil(nombre d'heures/4) * nombre d'intervenants secouristes / 4
    """
    target = pd.Timestamp(target_date)
    year = target.year

    df_dps = df_dps.copy()

    s_fin = pd.to_datetime(df_dps['DPS_DIMENSIONNEMENT_HEURE_FIN'].astype(str), format='%H:%M:%S', errors='coerce')
    s_deb = pd.to_datetime(df_dps['DPS_DIMENSIONNEMENT_HEURE_DEBUT'].astype(str), format='%H:%M:%S', errors='coerce')

    def to_seconds(s):
        return (s.dt.hour * 3600
                + s.dt.minute * 60
                + s.dt.second
                + s.dt.microsecond / 1e6)

    diff_seconds = (to_seconds(s_fin) - to_seconds(s_deb)) % (24 * 3600)
    df_dps['nb_heures'] = diff_seconds / 3600.0
    df_dps['nb_is_reel/theorique'] = (
        df_dps['DPS_DIMENSIONNEMENT_ACTEUR_NOMBRE_INTERVENANTS_SECOURISTES']
        + df_dps['DPS_DIMENSIONNEMENT_PUBLIC_NOMBRE_INTERVENANTS_SECOURISTES']) / 4
    
    df_dps['equivalent_poste_secours'] = np.ceil(df_dps['nb_heures'] / 4) * df_dps['nb_is_reel/theorique']

    indics_mask = [
        (f"Secours Nb_PAPS_ps_{year}",   df_dps['TYPE_DISPOSITIF_LIBELLE'] == "PAPS"),
        (f"Secours Nb_DPS_PE_ps_{year}", df_dps['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de petite envergure"),
        (f"Secours Nb_DPS_ME_ps_{year}", df_dps['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de moyenne envergure"),
        (f"Secours Nb_DPS_GE_ps_{year}", df_dps['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de grande envergure"),
        (f"Secours Nb_DPS_ps_{year}",    (df_dps['TYPE_DISPOSITIF_LIBELLE'] == "PAPS") |
                     (df_dps['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de petite envergure") | 
                     (df_dps['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de moyenne envergure") |
                     (df_dps['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de grande envergure"))
    ]

    frames = []

    for col, mask in indics_mask:
        serie = (
            df_dps[mask]
            .groupby(col_grpby)["equivalent_poste_secours"]
            .sum()
            .rename(col)
            .reset_index()
        )
        frames.append(serie)

    df_res = frames[0][[col_grpby]].copy()
    for frame in frames:
        df_res = df_res.merge(frame, on=col_grpby, how='outer')

    df_res = df_res.fillna(0)

    return df_res

def left_merge_all(df_base, list_df, on):
    """
    Merge une liste de dataframes à une dataframe de base, en utilisant un merge à gauche sur une ou plusieurs colonnes spécifiées dans "on".

    """

    df_res = df_base.copy()

    for df in list_df:
        df_res = pd.merge(df_res,
            df,
            how='left',
            on=on
        )

    return df_res

def fusion_finale_dps(df_ref_structure, list_dfs, list_dfs_DT):
    """
    Merge tous les dataframes dps
    """
    df_dps = left_merge_all(df_ref_structure['n_structure'], list_dfs, on='n_structure')
    df_dps_DT = left_merge_all(df_ref_structure['DT_de_rattachement'].drop_duplicates(), list_dfs_DT, on='DT_de_rattachement')
    return df_dps, df_dps_DT

def indicateurs_dps(df_dps_dimensionnement, df_dps_manifestation, df_dps_ref_type_dispositif, df_dps_ref_type_statut_demande, df_ref_structure, target_date):
    """
    Calcul l'ensembles des indicateurs issus de la table DPS
    """

    # Merge des tables pour avoir les libellés des dispositifs et des manifestations ainsi que les numéros de structure
    df_dps = pd.merge(
        df_dps_dimensionnement, df_dps_ref_type_dispositif, left_on="DPS_TYPE_DISPOSITIF_ID_FK", right_on="TYPE_DISPOSITIF_ID_PK", how="inner"
    )

    df_dps = pd.merge(df_dps, df_dps_manifestation, left_on="DPS_MANIFESTATION_ID_FK", right_on="DPS_MANIFESTATION_ID_PK", how="inner")

    df_dps = pd.merge(df_dps, df_dps_ref_type_statut_demande, left_on="DPS_TYPE_STATUT_DEMANDE_ID_FK", right_on="TYPE_STATUT_DEMANDE_ID_PK", how="inner")

    df_dps = df_dps[df_dps['TYPE_STATUT_DEMANDE_LIBELLE'] == "DPS cloture"]

    # Calculs indicateurs

    df_dispositifs = nb_dps(df_dps, target_date, "n_structure")
    df_dispositifs_DT = nb_dps(df_dps, target_date, "DT_de_rattachement")

    df_equivalent_ps = equivalent_poste_secours(df_dps, target_date, "n_structure")
    df_equivalent_ps_DT = equivalent_poste_secours(df_dps, target_date, "DT_de_rattachement")

    df_dps, df_dps_DT = fusion_finale_dps(df_ref_structure[df_ref_structure['type_structure'] != 'IMPLANTATION LOCALE HORS AL - IL'], [df_dispositifs, df_equivalent_ps], [df_dispositifs_DT, df_equivalent_ps_DT])

    df_dps_DT = df_dps_DT[(df_dps_DT['DT_de_rattachement'] != 'NaN') & (df_dps_DT['DT_de_rattachement'].notnull())]

    df_dps_DT = df_dps_DT.rename(columns={'DT_de_rattachement': 'n_structure'})
    df_dps_DT['n_structure'] = df_dps_DT['n_structure'].apply(keep_integer).astype(int)

    return df_dps, df_dps_DT




































############################################
# Code utilisé pour 2025, issu du bilan US #
############################################

# def clean_dps(df_conventions):
#     df = df_conventions[
#         [
#             'DT Annuaire Opé',
#             'Departement',
#             'Nb de vacations de 4h effectuées PAPS',
#             'Nb de vacations de 4h effectuées DPS PE',
#             'Nb de vacations de 4h effectuées DPS ME',
#             'Nb de vacations de 4h effectuées DPS GE'
#         ]
#     ]

#     df["Departement"] = df["Departement"].str.replace(
#         r"DELEGATION DEPARTEMENTALE|DELEGATION TERRITORIALE",
#         "DT",
#         regex=True
#     )

#     df = df.rename(columns={'Code structure': 'n_structure'})

#     return df




# def indicateurs_dps(df_dps, df_ref_structure):
    
#     df = df_dps[
#         [
#             "Departement",
#             "Nb de vacations de 4h effectuées PAPS",
#             "Nb de vacations de 4h effectuées DPS PE",
#             "Nb de vacations de 4h effectuées DPS ME",
#             "Nb de vacations de 4h effectuées DPS GE"
#         ]
#     ].copy()

#     df = rapprochement_libelles(
#         df_ref_structure,
#         df,
#         "Departement"
#     )

#     df = df.rename(
#         columns={
#             "Nb de vacations de 4h effectuées PAPS": "Secours Nb_PAPS_2025",
#             "Nb de vacations de 4h effectuées DPS PE": "Secours Nb_DPS_PE_2025",
#             "Nb de vacations de 4h effectuées DPS ME": "Secours Nb_DPS_ME_2025",
#             "Nb de vacations de 4h effectuées DPS GE": "Secours Nb_DPS_GE_2025"
#         }
#     )

#     # ✅ Somme ligne par ligne
#     df["Secours Nb_DPS_2025"] = df[
#         [
#             "Secours Nb_PAPS_2025",
#             "Secours Nb_DPS_PE_2025",
#             "Secours Nb_DPS_ME_2025",
#             "Secours Nb_DPS_GE_2025"
#         ]
#     ].sum(axis=1)

#     # ✅ PRINT SOMME PAR COLONNE
#     print("\n===== Somme globale par indicateur DPS =====")
#     cols_sum = [
#         "Secours Nb_PAPS_2025",
#         "Secours Nb_DPS_PE_2025",
#         "Secours Nb_DPS_ME_2025",
#         "Secours Nb_DPS_GE_2025",
#         "Secours Nb_DPS_2025"
#     ]

#     totals = df[cols_sum].sum()

#     for col in totals.index:
#         print(f"{col} : {totals[col]}")

#     return df



# def verifications_dps(df_conventions, df_indicateurs_dps):
#   """ Vérifie que les sommes correspondent à la source des données puis à la 
#   sortie du traitement

#   """

#   df_test_conv = df_conventions.copy().fillna(0)
#   columns_to_check = [('Nb de vacations de 4h effectuées PAPS', 'Secours Nb_PAPS_2025'), ('Nb de vacations de 4h effectuées DPS PE', 'Secours Nb_DPS_PE_2025'), ('Nb de vacations de 4h effectuées DPS ME','Secours Nb_DPS_ME_2025'), ('Nb de vacations de 4h effectuées DPS GE', 'Secours Nb_DPS_GE_2025')]

#   acc = 0
#   for col_source, col_res in columns_to_check:
#     if df_test_conv[col_source].sum() != df_indicateurs_dps[col_res].sum():
#       print(f" ❌ PROBL {col_res} : source {df_test_conv[col_source].sum()} ≠ résultat {df_indicateurs_dps[col_res].sum()}")
#     else :
#       print(f"✅ OK {col_res} : {col_source} = {col_res}")
#     acc += df_test_conv[col_source].sum()

#   if acc == df_indicateurs_dps['Secours Nb_PAPS_2025'].sum():
#     print(f" ❌ PROBL Secours Nb_PAPS_2025 : source {acc} ≠ résultat {df_indicateurs_dps['Secours Nb_PAPS_2025'].sum()}")
#   else :
#     print(f"✅ OK Secours Nb_PAPS_2025 : source = Secours Nb_PAPS_2025")
