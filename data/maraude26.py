from gspread_dataframe import get_as_dataframe
import pandas as pd
import os
import numpy as np
import re
import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *

def import_maraude(client, target_date="2025-12-31"):
    """
    Charge les données Maraude + rattachement_court depuis BigQuery.
    """

    target = pd.Timestamp(target_date)
    year = target.year
    query = f"""
    SELECT *
    FROM `crf-pat.dataset_PAT_{year}.crf_pat_{year}_maraude`
    """
    df_maraude = client.query(query).to_dataframe()

    df_maraude["maraude_date_debut"] = pd.to_datetime(df_maraude["maraude_date_debut"], errors="coerce")

    df_maraude = df_maraude[df_maraude["maraude_date_debut"].dt.year == year]

    query = f"""
    SELECT *
    FROM `crf-pat.dataset_PAT_{year}.crf_pat_{year}_maraude_beneficiaire`
    """
    df_maraude_beneficiaire = client.query(query).to_dataframe()

    df_maraude_filtre = df_maraude.copy()
    df_maraude_filtre =df_maraude_filtre[
    (df_maraude["maraude_date_debut"] > pd.Timestamp("2025-12-31")) &
    (df_maraude["maraude_date_debut"] <= pd.Timestamp(target)) &
    (df_maraude["maraude_statut"] == "FINISHED") &
    (df_maraude["maraude_rencontre_contact_realise"] == "Oui") &
    (df_maraude["maraude_rencontre_beneficiaire_id_fk"].notna())].copy()

    return  df_maraude, df_maraude_beneficiaire, df_maraude_filtre




def prep_nb_maraudes_sigma(df, filtre_annee_fn=None):
    cols_keep = [
        "maraude_id_fk",
        "maraude_structure_id_fk",
        "maraude_statut",
        "maraude_date_debut",
        "maraude_date_fin",
    ]

    missing = [c for c in cols_keep if c not in df.columns]
    if missing:
        print("Colonnes manquantes:", missing)

    d = df.loc[:, [c for c in cols_keep if c in df.columns]].copy()
    d = d.drop_duplicates()
    d = d.loc[d["maraude_statut"] == "FINISHED"].copy()

    return d


def prep_nb_personnes_rencontrees_sigma(df, filtre_annee_fn=None):
    cols_keep = [
        "maraude_id_fk",
        "maraude_structure_id_fk",
        "maraude_statut",
        "maraude_date_debut",
        "maraude_date_fin",
        "maraude_rencontre_beneficiaire_id_fk",
        "maraude_rencontre_contact_realise",
        "maraude_rencontre_typologie",
        "maraude_rencontre_nb_hommes",
        "maraude_rencontre_nb_femmes",
        "maraude_rencontre_nb_transgenres",
        "maraude_rencontre_nb_mineurs",
        "maraude_rencontre_nb_inconnus",
    ]

    missing = [c for c in cols_keep if c not in df.columns]
    if missing:
        print("Colonnes manquantes:", missing)

    d = df.loc[:, [c for c in cols_keep if c in df.columns]].copy()
    d = d.drop_duplicates()
    d = d.loc[d["maraude_statut"] == "FINISHED"].copy()
    d = d.loc[d["maraude_rencontre_contact_realise"] == "Oui"].copy()

    return d


def clean_maraudes(df_maraude):
    """
    Retourne les 2 tables "prep" (maraudes finies / contacts finies).
    """
    df_nb_personnes_rencontrees_sigma = prep_nb_personnes_rencontrees_sigma(df_maraude)
    df_Nb_maraudes_SIGMA_prep = prep_nb_maraudes_sigma(df_maraude)
    return df_nb_personnes_rencontrees_sigma, df_Nb_maraudes_SIGMA_prep


# ---------------------------------------------------------------------
# Calculs (helpers)
# ---------------------------------------------------------------------
def add_nb_personnes(df,
                     out_col="nb personnes",
                     cols=None,
                     col_typologie="maraude_rencontre_typologie"):
#on conserve ton +1 si typologie == "individu".
  
    if cols is None:
        cols = [
            "maraude_rencontre_nb_hommes",
            "maraude_rencontre_nb_femmes",
            "maraude_rencontre_nb_transgenres",
            "maraude_rencontre_nb_mineurs",
            "maraude_rencontre_nb_inconnus",
        ]

    d = df.copy()
    missing = [c for c in cols + [col_typologie] if c not in d.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes pour calculer '{out_col}': {missing}")

    d[cols] = d[cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    d[out_col] = d[cols].sum(axis=1)



    # +1 si typologie == "individu"
    d[out_col] += (d[col_typologie].astype(str).str.strip().str.lower() == "individu").astype(int)

    return d

# -------------------------------------------------------------------
# 0) Copie de travail pour ne pas modifier les DataFrames source
# -------------------------------------------------------------------
def maraude_retraitement(df_maraude_beneficiaire, df_maraude, df_maraude_filtre): 

    df_benef = df_maraude_beneficiaire.copy()



    # -------------------------------------------------------------------
    # 1) Préparation des variables
    # -------------------------------------------------------------------
    df_maraude["maraude_date_debut"] = pd.to_datetime(
        df_maraude["maraude_date_debut"],
        errors="coerce"
    )

    df_maraude["maraude_rencontre_typologie_norm"] = (
        df_maraude["maraude_rencontre_typologie"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # -------------------------------------------------------------------
    # 2) Filtres
    # -------------------------------------------------------------------
    df_maraude_filtre = df_maraude[
        (df_maraude["maraude_date_debut"] >= pd.Timestamp("2026-01-01")) &
        (df_maraude["maraude_date_debut"] <= pd.Timestamp("2026-05-31")) &
        (df_maraude["maraude_statut"] == "FINISHED") &
        (df_maraude["maraude_rencontre_contact_realise"] == "Oui") &
        (df_maraude["maraude_rencontre_typologie_norm"].isin(["famille", "individu"])) &
        (df_maraude["maraude_rencontre_beneficiaire_id_fk"].notna())
    ].copy()

    # -------------------------------------------------------------------
    # 3) Jointure
    # -------------------------------------------------------------------
    df_jointure = df_maraude_filtre.merge(
        df_benef[["beneficiaire_id_pk", "beneficiaire_identification_id"]],
        how="inner",
        left_on="maraude_rencontre_beneficiaire_id_fk",
        right_on="beneficiaire_id_pk"
    )

    # Exclusion des bénéficiaires sans identifiant
    df_jointure = df_jointure[
        df_jointure["beneficiaire_identification_id"].notna()
    ].copy()

    # -------------------------------------------------------------------
    # 4) Création de nombre_personnes_diff
    # -------------------------------------------------------------------
    cols_famille = [
        "maraude_rencontre_nb_hommes",
        "maraude_rencontre_nb_femmes",
        "maraude_rencontre_nb_transgenres",
        "maraude_rencontre_nb_mineurs",
        "maraude_rencontre_nb_inconnus",
    ]

    for col in cols_famille:
        df_jointure[col] = pd.to_numeric(df_jointure[col], errors="coerce").fillna(0)

    df_jointure["nombre_personnes_diff"] = np.where(
        df_jointure["maraude_rencontre_typologie_norm"] == "famille",
        df_jointure[cols_famille].sum(axis=1),
        1
    )

    # -------------------------------------------------------------------
    # 5) Contrôle : un beneficiaire_identification_id ne doit appartenir
    #    qu'à une seule structure
    # -------------------------------------------------------------------
    controle_structure = (
        df_jointure
        .groupby("beneficiaire_identification_id")["maraude_structure_id_fk"]
        .nunique()
        .reset_index(name="nb_structures_distinctes")
    )

    anomalies = controle_structure[controle_structure["nb_structures_distinctes"] > 1]

    if not anomalies.empty:
        raise ValueError(
            "Anomalie détectée : certains beneficiaire_identification_id sont rattachés à plusieurs maraude_structure_id_fk."
        )

    # -------------------------------------------------------------------
    # 6) Moyenne par beneficiaire_identification_id
    # -------------------------------------------------------------------
    df_benef_moyenne = (
        df_jointure
        .groupby("beneficiaire_identification_id", as_index=False)["nombre_personnes_diff"]
        #.mean()
        .max()
        .rename(columns={"nombre_personnes_diff": "nombre_personnes_diff_moyenne"})
    )

    # -------------------------------------------------------------------
    # 7) Récupération de la structure unique par bénéficiaire
    # -------------------------------------------------------------------
    df_benef_structure = (
        df_jointure[["beneficiaire_identification_id", "maraude_structure_id_fk"]]
        .drop_duplicates(subset=["beneficiaire_identification_id"])
        .copy()
    )

    # -------------------------------------------------------------------
    # 8) Table bénéficiaire finale
    # -------------------------------------------------------------------
    df_benef_final = df_benef_moyenne.merge(
        df_benef_structure,
        how="left",
        on="beneficiaire_identification_id"
    )

    # -------------------------------------------------------------------
    # 9) Somme finale par structure
    # -------------------------------------------------------------------
    df_final = (
        df_benef_final
        .groupby("maraude_structure_id_fk", as_index=False)["nombre_personnes_diff_moyenne"]
        .sum()
        .rename(columns={
            "nombre_personnes_diff_moyenne": "nb_beneficiaires_differents_rencontres"
        })
    )



    df_final.rename(columns={'maraude_structure_id_fk': 'n_structure'}, inplace=True)

    return df_final


def maraude_calcul_final(df_final, df_Nb_maraudes_SIGMA_prep, df_nb_personnes_rencontrees_sigma, df_ref_structure): 

        # -----------------------------------------------------------------
    # 1) MARAUDES (STRUCT)
    # -----------------------------------------------------------------
    d_m = df_Nb_maraudes_SIGMA_prep.copy()
    d_m = d_m.rename(columns={"maraude_structure_id_fk": "n_structure"})
    d_m["n_structure"] = pd.to_numeric(d_m["n_structure"], errors="coerce").astype("Int64")

    df_maraudes_struct = d_m.groupby("n_structure", as_index=False)["maraude_id_fk"].count()
    df_maraudes_struct.columns = ["n_structure", "Maraude Nb_maraudes_SIGMA"]



    # -----------------------------------------------------------------
    # 2) CONTACTS (STRUCT)
    # -----------------------------------------------------------------
    d_c = df_nb_personnes_rencontrees_sigma.copy()
    d_c = d_c.rename(columns={"maraude_structure_id_fk": "n_structure"})
    d_c["n_structure"] = pd.to_numeric(d_c["n_structure"], errors="coerce").astype("Int64")
    d_c = add_nb_personnes(d_c)

    df_contacts_struct = d_c.groupby("n_structure", as_index=False)["nb personnes"].sum()
    df_contacts_struct.columns = ["n_structure", "Maraude Nb_contacts"]


    df_final = pd.merge(df_final, df_contacts_struct, on='n_structure', how="outer")

    df_final = pd.merge(df_final, df_maraudes_struct, on='n_structure', how="outer")

    df_final = pd.merge(df_final, df_ref_structure[["n_structure",'n_structure-ratt']], on='n_structure', how="inner")

    df_SIGMA_struct = (
            df_final.groupby('n_structure-ratt', as_index=False)
            .agg(
                **{
                    'nb_beneficiaires_differents_rencontres': ('nb_beneficiaires_differents_rencontres', 'sum'),
                    'Maraude Nb_contacts': ('Maraude Nb_contacts', 'sum'),
                    'Maraude Nb_maraudes_SIGMA': ('Maraude Nb_maraudes_SIGMA', 'sum')
                }
            )
        )

    df_SIGMA_struct.rename(columns={'n_structure-ratt': 'n_structure'}, inplace=True)

    df_SIGMA_DT = pd.merge(df_SIGMA_struct, df_ref_structure[["n_structure",'DT_de_rattachement']], on='n_structure', how="inner")

    df_SIGMA_DT = (
            df_SIGMA_DT.groupby('DT_de_rattachement', as_index=False)
            .agg(
                **{
                    'nb_beneficiaires_differents_rencontres': ('nb_beneficiaires_differents_rencontres', 'sum'),
                    'Maraude Nb_contacts': ('Maraude Nb_contacts', 'sum'),
                    'Maraude Nb_maraudes_SIGMA': ('Maraude Nb_maraudes_SIGMA', 'sum')
                }
            )
        )


    return df_SIGMA_DT, df_SIGMA_struct

