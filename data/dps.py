import os
import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *

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
    df_dps_dimensionnement['DPS_DIMENSIONNEMENT_DATE_DEBUT'] = pd.to_datetime(df_dps_dimensionnement['DPS_DIMENSIONNEMENT_DATE_DEBUT'])
    df_dps_dimensionnement = df_dps_dimensionnement[df_dps_dimensionnement['DPS_DIMENSIONNEMENT_DATE_DEBUT'].dt.year == year & (df_dps_dimensionnement['DPS_DIMENSIONNEMENT_DATE_DEBUT'] <= target)]

    df_dps_manifestation = apply_rattachement_successif(df_ref_structure, df_dps_manifestation, "DPS_DEMANDE_STRUCTURE_ID")

    df_dps_manifestation['DPS_MANIFESTATION_DATE_DEBUT'] = pd.merge(df_dps_manifestation, df_ref_structure[['n_structure','DT_de_rattachement']].drop_duplicates(), left_on="DPS_DEMANDE_STRUCTURE_ID", right_on="n_structure", how="left")

    df_dps_manifestation = df_dps_manifestation.rename(columns = {"DPS_DEMANDE_STRUCTURE_ID":"n_structure"})

    return df_dps_dimensionnement, df_dps_manifestation, df_dps_ref_type_dispositif, df_dps_ref_type_statut_demande


def nb_dispositifs_dps(df_dps_dimensionnement, target_date, col_grpby):
    """" 
    Calcul les indicateurs suivantes :
    Secours Nb_PAPS_
    Secours Nb_DPS_PE_
    Secours Nb_DPS_ME_
    Secours Nb_DPS_GE_
    """

    target = pd.Timestamp(target_date)
    year = target.year

    df_res = pd.DataFrame(index=[0])

    indics_mask = [(f"Secours Nb_PAPS_{year}", df_dps_dimensionnement['TYPE_DISPOSITIF_LIBELLE'] == "PAPS"),
                    (f"Secours Nb_DPS_PE_{year}", df_dps_dimensionnement['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de petite envergure"),
                    (f"Secours Nb_DPS_ME_{year}", df_dps_dimensionnement['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de moyenne envergure"),
                    (f"Secours Nb_DPS_GE_{year}", df_dps_dimensionnement['TYPE_DISPOSITIF_LIBELLE'] == "Dispositif de grande envergure")]


    for col, mask in indics_mask:
        df_res[col] = df_dps_dimensionnement.loc[mask, "DPS_DIMENSIONNEMENT_ID_PK"].groupby(col_grpby)["DPS_DIMENSIONNEMENT_ID_PK"].nunique()
    
    return df_res


def indicateurs_dps(df_dps_dimensionnement, df_dps_manifestation, df_dps_ref_type_dispositif, df_dps_ref_type_statut_demande, target_date):

    # Merge des tables pour avoir les libellés des dispositifs et des manifestations ainsi que les numéros de structure
    df_dps = pd.merge(
        df_dps_dimensionnement, df_dps_ref_type_dispositif, left_on="DPS_TYPE_DISPOSITIF_ID_FK", right_on="TYPE_DISPOSITIF_ID_PK", how="left"
    )

    df_dps = pd.merge(df_dps, df_dps_manifestation, left_on="DPS_MANIFESTATION_ID_FK", right_on="DPS_MANIFESTATION_ID_PK", how="left")

    df_dps = pd.merge(df_dps, df_dps_ref_type_statut_demande, left_on="DPS_TYPE_STATUT_DEMANDE_ID_FK", right_on="TYPE_STATUT_DEMANDE_ID_PK", how="left")

    # Calculs indicateurs

    df_dispositifs = nb_dispositifs_dps(df_dps, target_date, "n_structure")
    df_dispositifs_DT = nb_dispositifs_dps(df_dps, target_date, "DT_de_rattachement")

    return df_dispositifs, df_dispositifs_DT




































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
