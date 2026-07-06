import pandas as pd
import numpy as np
import re
import sys
import os
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *
from datetime import datetime
import gspread
from gspread_dataframe import get_as_dataframe

def clean_base_contact(client, gspread_client, mapping_df):
    query_formation_session_resultat = """
    SELECT *
    FROM `crf-pat.dataset_PAT_2026.crf_pat_2026_formation_session_resultat`
"""

    df_formation_session_resultat = (
        client
        .query(query_formation_session_resultat)
        .to_dataframe()
    )

    # Conversion des colonnes de dates
    df_formation_session_resultat[
        "FORMATION_DATE_OBTENTION"
    ] = pd.to_datetime(
        df_formation_session_resultat[
            "FORMATION_DATE_OBTENTION"
        ],
        errors="coerce"
    )

    df_formation_session_resultat[
        "FORMATION_DATE_RECYCLAGE"
    ] = pd.to_datetime(
        df_formation_session_resultat[
            "FORMATION_DATE_RECYCLAGE"
        ],
        errors="coerce"
    )

    df_ref_structure = get_as_dataframe(gspread_client.open_by_url('https://docs.google.com/spreadsheets/d/1PUdny0DiyOjSSYLte2o9r1Xyh02O9INFlzLJVHl92ic/').worksheet('Ref_structure RP 2026'))
    df_ref_structure = renommer_par_nom_table(df_ref_structure, "AS_Informations_structures", mapping_df)
    df_ref_structure['n_structure'] = df_ref_structure['n_structure'].astype(int)
    df_ref_structure = df_ref_structure[df_ref_structure["type_structure"].isin(["UNITE LOCALE - UL", "DELEGATION TERRITORIALE - DT", 'IMPLANTATION LOCALE HORS AL - IL', 'ANTENNE LOCALE - AL','INSTANCES NATIONALES - IN'])]
    
    ### 0.1 rattachement_court
    rattachement_court = df_ref_structure[['n_structure', 'DT_de_rattachement']].copy().drop_duplicates()

    return df_formation_session_resultat, df_ref_structure, rattachement_court

# ============================================================
# 4. IMPORT TABLE RATTACHEMENT_BENEVOLE
# ============================================================

def import_rattachement_benevole(target_date, df_ref_structure, client):

    target = pd.Timestamp(target_date)
    year = target.year

    bdd_year = year

    if year < 2025:
        bdd_year = 2025

    query_rattachement_benevole = f"""
        SELECT *
        FROM `crf-pat.dataset_PAT_{bdd_year}.crf_pat_{bdd_year}_rattachement_benevole`
    """

    df_rattachement_benevole = client.query(
        query_rattachement_benevole
    ).to_dataframe()

    # On ne garde que les rattachements associés aux structures
    # présentes dans le référentiel
    df_ref_structure_type = df_ref_structure[
        ["n_structure", "type_structure"]
    ]

    df_rattachement_benevole = pd.merge(
        df_rattachement_benevole,
        df_ref_structure_type,
        left_on="rattachement_benevole_structure_id_fk",
        right_on="n_structure",
        how="inner"
    )

    # Conversion des dates de rattachement
    df_rattachement_benevole["rattachement_benevole_date_fin"] = (
        pd.to_datetime(
            df_rattachement_benevole[
                "rattachement_benevole_date_fin"
            ],
            errors="coerce"
        )
    )

    df_rattachement_benevole["rattachement_benevole_date_debut"] = (
        pd.to_datetime(
            df_rattachement_benevole[
                "rattachement_benevole_date_debut"
            ],
            errors="coerce"
        )
    )

    # On garde uniquement les rattachements actifs à la date cible
    df_rattachement_benevole = df_rattachement_benevole.loc[
        (
            df_rattachement_benevole[
                "rattachement_benevole_date_fin"
            ].isna()
            |
            (
                df_rattachement_benevole[
                    "rattachement_benevole_date_fin"
                ] >= target
            )
        )
        &
        (
            df_rattachement_benevole[
                "rattachement_benevole_date_debut"
            ] <= target
        )
    ].copy()

    # On trie pour garder le rattachement le plus récent
    # pour chaque bénévole
    df_rattachement_benevole = (
        df_rattachement_benevole
        .sort_values(
            "rattachement_benevole_date_debut",
            ascending=False
        )
        .drop_duplicates(
            subset="rattachement_benevole_nivol_id_fk",
            keep="first"
        )
        .copy()
    )

    # On garde uniquement les colonnes utiles au merge
    df_rattachement_benevole = df_rattachement_benevole[
        [
            "rattachement_benevole_nivol_id_fk",
            "rattachement_benevole_structure_id_fk"
        ]
    ].copy()

    return df_rattachement_benevole



def calcul_base_contact( df_formation_session_resultat, df_ref_structure,df_rattachement_benevole, annee = 2026,  date_limite_recyclage=None, date_limite_obtention_debut=None, date_limite_obtention_fin=None): 

    # Étape 2 — Définir les codes utiles

    filtres_bc = {
        "FPSC": [
            "FCFPSC",
            "RATFCFPSC",
            "FPSC",
            "RECFPSC",
            "PICF FPSC",
            "PAE3",
        ],

        "AGQS": [
            "AGQS",
        ],

        "FIPSEN": [
            "FIPSEN",
            "RECFIPSEN",
        ],

        "PSE1": [
            "APTE PSE1",
            "PSE1",
            "RECPSE1",
            "RATPSE1",
            "FCPSE1",
        ],

        "PSE1_i": [
            "APTE PSE1",
            "PSE1",
            "RATPSE1",
        ],

        "RECPSE1": [
            "RECPSE1",
            "FCPSE1",
        ],

        "PSE2": [
            "RECPSE2",
            "PSE2",
            "PSE",
            "RATPSE2",
            "FCPSE2",
            "FCPSE",
            "PSE AGSU",
        ],

        "PSE2_i": [
            "PSE",
            "PSE2",
            "RATPSE2",
        ],

        "RECPSE2": [
            "RECPSE2",
            "FCPSE2",
        ],

        "CI": [
            "CI P1 P2",
            "CI",
            "CIP2",
            "RECCI",
            "REC PSECI",
            "RECPSECI",
            "FCCI",
        ],

        "CI_i": [
            "CI",
            "CI P1 P2",
            "CI P1",
            "CI P2",
            "CI EXT",
            "RATCI",
        ],

        "FPSE": [
            "RECFPS",
            "FPS",
            "FPSE",
            "FCFPSE",
            "RATFCFPSE",
            "PICF FPS",
            "PICF FPSE",
            "FPSE AFGU",
        ],

        "FPSE_i": [
            "FPS",
            "FPSE",
            "FCFPSE",
            "RATFCFPSE",
            "PICF FPS",
            "PICF FPSE",
            "FPSE AFGU",
        ],

        "RECFPSE": [
            "RECFPS",
        ],

        "RECCI": [
            "RECCI",
            "REC PSECI",
            "RECPSECI",
            "FCCI",
        ],

        "FPS": [
            "RECFPS",
            "FPS",
            "FPSE",
            "FCFPSE",
            "RATFCFPSE",
            "PICF FPS",
            "PICF FPSE",
        ],
    }

    #Créer la liste unique des codes bruts

    codes_formations_utiles = sorted(
            {
                code
                for liste_codes in filtres_bc.values()
                for code in liste_codes
            }
    )

    # Étape 3 — Filtrer les codes de formation
    df_formations_codes_utiles = (
        df_formation_session_resultat[
            df_formation_session_resultat[
                "FORMATION_CODE"
            ].isin(codes_formations_utiles)
        ]
        .copy()
    )

    # Étape 4 — Filtrer les résultats « Apte »
    df_formations_aptes = (
        df_formations_codes_utiles[
            df_formations_codes_utiles[
                "FORMATION_RESULTAT"
            ] == "Apte"
        ]
        .copy()
    )

    ##### On crée la partie de la fonction qui définit les dates de recyclage = c'est ici que cela peuit bugger


    conditions = []

    # Condition sur la date de recyclage
    if date_limite_recyclage is not None:

        date_limite_recyclage = pd.Timestamp(
            date_limite_recyclage
        )

        condition_recyclage = (
            df_formations_aptes[
                "FORMATION_DATE_RECYCLAGE"
            ] >= date_limite_recyclage
        )

        conditions.append(condition_recyclage)

    # Condition sur la date d'obtention
    if (
        date_limite_obtention_debut is not None
        or date_limite_obtention_fin is not None
    ):

        condition_obtention = pd.Series(
            True,
            index=df_formations_aptes.index
        )

        if date_limite_obtention_debut is not None:

            date_limite_obtention_debut = pd.Timestamp(
                date_limite_obtention_debut
            )

            condition_obtention = (
                condition_obtention
                & (
                    df_formations_aptes[
                        "FORMATION_DATE_OBTENTION"
                    ] >= date_limite_obtention_debut
                )
            )

        if date_limite_obtention_fin is not None:

            date_limite_obtention_fin = pd.Timestamp(
                date_limite_obtention_fin
            )

            condition_obtention = (
                condition_obtention
                & (
                    df_formations_aptes[
                        "FORMATION_DATE_OBTENTION"
                    ] <= date_limite_obtention_fin
                )
            )

        conditions.append(condition_obtention)

    # On combine les conditions avec un OU
    if len(conditions) > 0:

        condition_finale = conditions[0]

        for condition in conditions[1:]:
            condition_finale = condition_finale | condition

        df_formations_valides = (
            df_formations_aptes[
                condition_finale
            ]
            .copy()
        )

    # Si aucune date n'est renseignée, aucune condition n'est appliquée
    else:

        df_formations_valides = (
            df_formations_aptes
            .copy()
        )


    # Étape 6 — Supprimer les doublons NIVOL et code

    # Retirer les lignes inutilisables pour le tableau large
    df_formations_valides_identifiees = (
        df_formations_valides
        .dropna(
            subset=[
                "NIVOL_ID_FK",
                "FORMATION_CODE",
            ]
        )
        .copy()
    )

    # Dédoublonner

    df_formations_valides_uniques = (
        df_formations_valides_identifiees
        .drop_duplicates(
            subset=[
                "NIVOL_ID_FK",
                "FORMATION_CODE",
            ]
        )
        .copy()
    )

    # Étape 7 — Transformer la table au format large

    df_formations_par_nivol = pd.crosstab(
        index=(
            df_formations_valides_uniques[
                "NIVOL_ID_FK"
            ]
        ),
        columns=(
            df_formations_valides_uniques[
                "FORMATION_CODE"
            ]
        ),
    )

    # Transformer toutes les valeurs positives en 1
    df_formations_par_nivol = (
        df_formations_par_nivol
        .gt(0)
        .astype(int)
    )

    # Ajouter les codes utiles absents des données avec la valeur 0
    df_formations_par_nivol = (
        df_formations_par_nivol
        .reindex(
            columns=codes_formations_utiles,
            fill_value=0,
        )
    )

    # Replacer NIVOL_ID_FK comme colonne
    df_formations_par_nivol = (
        df_formations_par_nivol
        .reset_index()
    )

    # Supprimer le nom technique de l'axe des colonnes
    df_formations_par_nivol.columns.name = None


    # Création des indicateurs agrégés

    for indicateur, codes_formations in filtres_bc.items():

        nom_nouvelle_colonne = f"calcul_{indicateur}"

        df_formations_par_nivol[nom_nouvelle_colonne] = (
            df_formations_par_nivol[codes_formations]
            .sum(axis=1)
            .gt(0)
            .astype(int)
        )


    # Modification des calculs pour intégrer les induits 

    df_formations_par_nivol_avant_exclusions = (
        df_formations_par_nivol.copy()
    )


    # ============================================================
# Règles d'exclusion entre niveaux de formation
# ============================================================

# PSE1 exclu si la personne possède PSE2, CI ou FPSE
    condition_exclusion_PSE1 = (
        df_formations_par_nivol["calcul_PSE2"].eq(1)
        | df_formations_par_nivol["calcul_CI"].eq(1)
        | df_formations_par_nivol["calcul_FPSE"].eq(1)
    )

    df_formations_par_nivol.loc[
        condition_exclusion_PSE1,
        "calcul_PSE1"
    ] = 0


    # PSE1 initial exclu si la personne possède :
    # PSE2, CI, FPSE ou un recyclage PSE1
    condition_exclusion_PSE1_i = (
        df_formations_par_nivol["calcul_PSE2"].eq(1)
        | df_formations_par_nivol["calcul_CI"].eq(1)
        | df_formations_par_nivol["calcul_FPSE"].eq(1)
        | df_formations_par_nivol["calcul_RECPSE1"].eq(1)
    )

    df_formations_par_nivol.loc[
        condition_exclusion_PSE1_i,
        "calcul_PSE1_i"
    ] = 0


    # Recyclage PSE1 exclu si la personne possède PSE2, CI ou FPSE
    condition_exclusion_RECPSE1 = (
        df_formations_par_nivol["calcul_PSE2"].eq(1)
        | df_formations_par_nivol["calcul_CI"].eq(1)
        | df_formations_par_nivol["calcul_FPSE"].eq(1)
    )

    df_formations_par_nivol.loc[
        condition_exclusion_RECPSE1,
        "calcul_RECPSE1"
    ] = 0


    # PSE2 exclu si la personne possède CI ou FPSE
    condition_exclusion_PSE2 = (
        df_formations_par_nivol["calcul_CI"].eq(1)
        | df_formations_par_nivol["calcul_FPSE"].eq(1)
    )

    df_formations_par_nivol.loc[
        condition_exclusion_PSE2,
        "calcul_PSE2"
    ] = 0


    # PSE2 initial exclu si la personne possède :
    # CI, FPSE ou un recyclage PSE2
    condition_exclusion_PSE2_i = (
        df_formations_par_nivol["calcul_CI"].eq(1)
        | df_formations_par_nivol["calcul_FPSE"].eq(1)
        | df_formations_par_nivol["calcul_RECPSE2"].eq(1)
    )

    df_formations_par_nivol.loc[
        condition_exclusion_PSE2_i,
        "calcul_PSE2_i"
    ] = 0


    # Recyclage PSE2 exclu si la personne possède CI ou FPSE
    condition_exclusion_RECPSE2 = (
        df_formations_par_nivol["calcul_CI"].eq(1)
        | df_formations_par_nivol["calcul_FPSE"].eq(1)
    )

    df_formations_par_nivol.loc[
        condition_exclusion_RECPSE2,
        "calcul_RECPSE2"
    ] = 0


    # CI initial exclu si la personne possède un recyclage CI
    condition_exclusion_CI_i = (
        df_formations_par_nivol["calcul_RECCI"].eq(1)
    )

    df_formations_par_nivol.loc[
        condition_exclusion_CI_i,
        "calcul_CI_i"
    ] = 0


    # FPSE initial exclu si la personne possède un recyclage FPSE
    condition_exclusion_FPSE_i = (
        df_formations_par_nivol["calcul_RECFPSE"].eq(1)
    )

    df_formations_par_nivol.loc[
        condition_exclusion_FPSE_i,
        "calcul_FPSE_i"
    ] = 0


    #On merge 

    df_formations_par_nivol = pd.merge(
        df_formations_par_nivol,
        df_rattachement_benevole,
        left_on="NIVOL_ID_FK",
        right_on="rattachement_benevole_nivol_id_fk",
        how="left",
        validate="one_to_one"
    )

    df_formations_par_nivol = pd.merge(
        df_formations_par_nivol,
        df_ref_structure [["n_structure","n_structure-ratt"]],
        left_on="rattachement_benevole_structure_id_fk",
        right_on="n_structure",
        how="left",
        validate="many_to_one"
    )

    df_formations_par_nivol = (df_formations_par_nivol.drop(columns="n_structure").rename(columns={"n_structure-ratt": "n_structure"}))

    #CALCUL DU NB D'IS 
    df_formations_par_nivol["Secours Nb_IS"] = (
        df_formations_par_nivol[
            ["calcul_PSE1", "calcul_PSE2", "calcul_CI"]
        ]
        .sum(axis=1)
        .gt(0)
        .astype(int)
    )

    df_NIVOLS_IS = df_formations_par_nivol[["n_structure", "Secours Nb_IS","NIVOL_ID_FK"]].copy()
    
    # Liste des NIVOL considérés comme IS
    df_NIVOLS_IS = df_NIVOLS_IS.loc[
        df_formations_par_nivol["Secours Nb_IS"] == 1,
        ["n_structure", "Secours Nb_IS", "NIVOL_ID_FK"]
    ].copy()

    df_formations_par_nivol = df_formations_par_nivol[['n_structure','calcul_FPSC','calcul_PSE1', 'calcul_PSE1_i', 'calcul_RECPSE1', 'calcul_PSE2', 'calcul_PSE2_i', 'calcul_RECPSE2', 'calcul_CI', 'calcul_CI_i', 'calcul_FPSE', 'calcul_FPSE_i', 'calcul_RECFPSE', 'calcul_RECCI','calcul_FPS', "Secours Nb_IS"]]



    #On rename 

    df_formations_par_nivol = df_formations_par_nivol.rename(
        columns={
            "calcul_PSE1": f"Secours Nb_PSE1_{annee}",
            "calcul_PSE1_i": f"Secours Nb_FI_PSE1_{annee}",
            "calcul_RECPSE1": f"Secours Nb_FC_PSE1_{annee}",

            "calcul_PSE2": f"Secours Nb_PSE2_{annee}",
            "calcul_PSE2_i": f"Secours Nb_FI_PSE2_{annee}",
            "calcul_RECPSE2": f"Secours Nb_FC_PSE2_{annee}",

            "calcul_CI": f"Secours Nb_CI_{annee}",
            "calcul_CI_i": f"Secours Nb_FI_CI_{annee}",
            "calcul_RECCI": f"Secours Nb_FC_CI_{annee}",

            "calcul_FPSE": f"Secours Nb_FPSE_{annee}",
            "calcul_FPSE_i": f"Secours Nb_FI_FPSE_{annee}",
            "calcul_RECFPSE": f"Secours Nb_FC_FPSE_{annee}",
            "calcul_FPSC" : f"Formation_grand_public Nb_FPSC_{annee}",
            "Secours Nb_IS" : f"Secours Nb_IS_{annee}",
        }
    )

    #On calcule par structure 

    df_formations_par_structure = (
        df_formations_par_nivol
        .groupby("n_structure", as_index=False)
        .sum(numeric_only=True)
    )

    # On calcule par DT

    df_ref_structure_DT = df_ref_structure[['n_structure', 'DT_de_rattachement']].copy().drop_duplicates()

    df_formations_par_DT = pd.merge(
        df_formations_par_structure,
        df_ref_structure_DT,
        on="n_structure",
        how="left"
    )

    df_formations_par_DT = df_formations_par_DT.dropna(
        subset=["DT_de_rattachement"]
    ).copy()

    # Suppression de n_structure
    df_formations_par_DT = df_formations_par_DT.drop(
        columns="n_structure"
    )


    # Somme des indicateurs par DT
    df_formations_par_DT = (
        df_formations_par_DT
        .groupby("DT_de_rattachement", as_index=False)
        .sum(numeric_only=True)
    )

    return df_formations_par_DT, df_formations_par_structure, df_formations_par_nivol, df_NIVOLS_IS
