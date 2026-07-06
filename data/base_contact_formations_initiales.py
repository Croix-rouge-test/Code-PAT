"""
Calcul des indicateurs de formations initiales de la Base Contact.

Le module attend que le notebook fournisse :
- un client BigQuery authentifié ;
- le DataFrame df_ref_structure ;
- la date cible éventuelle.

Les traitements Google Sheets et l'authentification restent dans le notebook.
"""

from functools import reduce

import pandas as pd


# ---------------------------------------------------------------------
# Variables globales
# ---------------------------------------------------------------------

TARGET_DATE = "2026-05-31"
TARGET_YEAR = pd.Timestamp(TARGET_DATE).year

# Uniquement utile pour Base Contact
half_year = True


FILTRES_BC_SANS_RECYCLAGE = {
    "AAD": ["AAD"],
    "FAAD": ["FAAD", "EPIAF FAAD"],
    "solidar": [
        "SOLIDAR2",
        "SOLIDAR1",
        "SOLIDAR",
        "PASSOLIDAR2020",
        "ESOLIDAR2026",
        "SOLIDAR2020",
    ],
    "SAH": ["SAH", "TASA"],
    "ASAH": ["ASAH", "FASAH"],
    "CRB": ["CRB", "ECRB", "VI"],
    "ACRB": ["ACRB2", "ACRB2024"],
    "TCAS": ["TCAS", "ETCAS"],
    "TCAU": ["TCAU", "ETCAU"],
    "TCEO": ["TCEO", "ESE"],
    "PSP": ["PSP"],
    "IRR": ["IRR", "IRRA", "IRRJ"],
    "ATEX": ["ATEXTILE"],
    "GQS": ["GQS", "GQS AC", "FIPS", "FIPS2"],
}


TYPES_FORMATIONS = [
    "AAD",
    "FAAD",
    "solidar",
    "SAH",
    "ASAH",
    "CRB",
    "ACRB",
    "TCAS",
    "TCAU",
    "TCEO",
    "PSP",
    "IRR",
    "ATEX",
    "GQS",
]


CODES_SOLIDAR2020 = [
    "PASSOLIDAR2020",
    "ESOLIDAR2026",
    "SOLIDAR2020",
]


# ---------------------------------------------------------------------
# Import des données
# ---------------------------------------------------------------------

def importer_base_contact(
    client,
    target_date=TARGET_DATE,
    filtres_bc_sans_recyclage=FILTRES_BC_SANS_RECYCLAGE,
):
    """
    Importe la table des résultats de formation et conserve uniquement
    les codes utiles aux indicateurs de formation initiale.
    """
    target = pd.Timestamp(target_date)
    bdd_year = max(target.year, 2025)

    codes_filtres = list(
        {
            code
            for liste_codes in filtres_bc_sans_recyclage.values()
            for code in liste_codes
        }
    )

    query_formation_session_resultat = f"""
        SELECT *
        FROM `crf-pat.dataset_PAT_{bdd_year}.crf_pat_{bdd_year}_formation_session_resultat`
    """

    df_formation_session_resultat = (
        client
        .query(query_formation_session_resultat)
        .to_dataframe()
    )

    df_formation_session_resultat["FORMATION_DATE_OBTENTION"] = pd.to_datetime(
        df_formation_session_resultat["FORMATION_DATE_OBTENTION"],
        errors="coerce",
    )

    df_formation_session_resultat["FORMATION_DATE_RECYCLAGE"] = pd.to_datetime(
        df_formation_session_resultat["FORMATION_DATE_RECYCLAGE"],
        errors="coerce",
    )

    df_formation_session_resultat_formation_initiale = (
        df_formation_session_resultat[
            df_formation_session_resultat["FORMATION_CODE"].isin(
                codes_filtres
            )
        ]
        .copy()
    )

    return df_formation_session_resultat_formation_initiale


def importer_rattachement_benevole(
    client,
    df_ref_structure,
    target_date=TARGET_DATE,
):
    """
    Importe les rattachements bénévoles, conserve les rattachements actifs
    à la date cible, puis garde le rattachement actif le plus récent
    pour chaque NIVOL.
    """
    target = pd.Timestamp(target_date)
    bdd_year = max(target.year, 2025)

    query_rattachement_benevole = f"""
        SELECT *
        FROM `crf-pat.dataset_PAT_{bdd_year}.crf_pat_{bdd_year}_rattachement_benevole`
    """

    df_rattachement_benevole = (
        client
        .query(query_rattachement_benevole)
        .to_dataframe()
    )

    # On ne garde que les rattachements associés aux structures
    # présentes dans le référentiel.
    df_ref_structure_type = (
        df_ref_structure[
            ["n_structure", "type_structure"]
        ]
        .drop_duplicates()
        .copy()
    )

    df_rattachement_benevole = pd.merge(
        df_rattachement_benevole,
        df_ref_structure_type,
        left_on="rattachement_benevole_structure_id_fk",
        right_on="n_structure",
        how="inner",
    )

    df_rattachement_benevole["rattachement_benevole_date_fin"] = pd.to_datetime(
        df_rattachement_benevole["rattachement_benevole_date_fin"],
        errors="coerce",
    )

    df_rattachement_benevole["rattachement_benevole_date_debut"] = pd.to_datetime(
        df_rattachement_benevole["rattachement_benevole_date_debut"],
        errors="coerce",
    )

    # Rattachement actif à la date cible.
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

    # Un seul rattachement actif par bénévole :
    # le plus récent à la date cible.
    df_rattachement_benevole = (
        df_rattachement_benevole
        .sort_values(
            "rattachement_benevole_date_debut",
            ascending=False,
        )
        .drop_duplicates(
            subset="rattachement_benevole_nivol_id_fk",
            keep="first",
        )
        [
            [
                "rattachement_benevole_nivol_id_fk",
                "rattachement_benevole_structure_id_fk",
            ]
        ]
        .copy()
    )

    return df_rattachement_benevole


# ---------------------------------------------------------------------
# Calcul des indicateurs
# ---------------------------------------------------------------------

def calculer_formations_initiales(
    df_formation_session_resultat_formation_initiale,
    df_rattachement_benevole,
    df_ref_structure,
    target_date=TARGET_DATE,
    filtres_bc_sans_recyclage=FILTRES_BC_SANS_RECYCLAGE,
    types_formations=TYPES_FORMATIONS,
):
    """
    Calcule les indicateurs de formation initiale.

    Sorties :
    - df_final_formation_initiale : résultats par structure de rattachement ;
    - df_final_formation_initiale_DT : résultats agrégés par DT.
    """
    target = pd.Timestamp(target_date)
    year = target.year

    df_formations = (
        df_formation_session_resultat_formation_initiale
        .copy()
    )

    # On ne conserve que les résultats "Apte".
    df_formations = df_formations[
        df_formations["FORMATION_RESULTAT"] == "Apte"
    ].copy()

    # Ajout du rattachement bénévole actif.
    df_formations = pd.merge(
        df_formations,
        df_rattachement_benevole,
        left_on="NIVOL_ID_FK",
        right_on="rattachement_benevole_nivol_id_fk",
        how="left",
    )

    # On ne conserve que les NIVOL disposant d'un rattachement actif.
    df_formations = df_formations[
        df_formations[
            "rattachement_benevole_structure_id_fk"
        ].notna()
    ].copy()

    # Date d'obtention inférieure ou égale à la date cible.
    df_formations = df_formations[
        df_formations["FORMATION_DATE_OBTENTION"] <= target
    ].copy()

    # Passage de la structure du bénévole à la structure de rattachement
    # utilisée dans les rapports.
    df_ref_structure_ratt = (
        df_ref_structure[
            ["n_structure", "n_structure-ratt"]
        ]
        .drop_duplicates(subset=["n_structure"])
        .copy()
    )

    df_formations = pd.merge(
        df_formations,
        df_ref_structure_ratt,
        left_on="rattachement_benevole_structure_id_fk",
        right_on="n_structure",
        how="left",
    )

    df_formations = df_formations[
        df_formations["n_structure-ratt"].notna()
    ].copy()

    df_formations = (
        df_formations[
            [
                "FORMATION_CODE",
                "NIVOL_ID_FK",
                "FORMATION_DATE_OBTENTION",
                "FORMATION_DATE_RECYCLAGE",
                "n_structure-ratt",
            ]
        ]
        .rename(columns={"n_structure-ratt": "n_structure"})
        .copy()
    )

    # Correspondance entre les codes et les familles de formations.
    mapping_code_formation = {
        code_formation: type_formation
        for type_formation, liste_codes in filtres_bc_sans_recyclage.items()
        for code_formation in liste_codes
    }

    df_formations["TYPE_FORMATION"] = (
        df_formations["FORMATION_CODE"]
        .map(mapping_code_formation)
    )


    #Calcul des NIVOLS CRB

    df_nivol_CRB = (
    df_formations[
        df_formations["TYPE_FORMATION"].eq("CRB")
        
    ])

    df_nivol_CRB = df_nivol_CRB[["n_structure","NIVOL_ID_FK","FORMATION_DATE_OBTENTION"]].drop_duplicates().copy()

    #Calcul des NIVOLS SOLIDAR 

    df_nivol_solidar = (
    df_formations[
        df_formations["TYPE_FORMATION"].eq("solidar")
        
    ])

    df_nivol_solidar = df_nivol_solidar[["n_structure","NIVOL_ID_FK"]].drop_duplicates().copy()


    # Calcul spécifique SOLIDAR2020 :
    # un même NIVOL est compté une seule fois par structure,
    # même s'il possède plusieurs codes SOLIDAR2020.
    df_solidar2020 = (
        df_formations[
            df_formations["FORMATION_CODE"].isin(
                CODES_SOLIDAR2020
            )
        ]
        .groupby(
            "n_structure",
            as_index=False,
        )
        .agg(
            **{
                "Maraude Nb_SOLIDAR2020": (
                    "NIVOL_ID_FK",
                    "nunique",
                )
            }
        )
    )

    # Pour chaque NIVOL et chaque famille de formation,
    # on conserve la formation la plus récente.
    # Cela évite notamment de compter deux fois TCAS + ETCAS.
    df_formations_dedoublonnees = (
        df_formations
        .sort_values(
            by=[
                "NIVOL_ID_FK",
                "TYPE_FORMATION",
                "FORMATION_DATE_OBTENTION",
            ],
            ascending=[True, True, False],
            na_position="last",
        )
        .drop_duplicates(
            subset=[
                "NIVOL_ID_FK",
                "TYPE_FORMATION",
            ],
            keep="first",
        )
        .reset_index(drop=True)
    )

    # Calcul de chaque indicateur par structure.
    dfs_formations = {}

    for formation in types_formations:
        dfs_formations[formation] = (
            df_formations_dedoublonnees[
                df_formations_dedoublonnees[
                    "TYPE_FORMATION"
                ] == formation
            ]
            .groupby("n_structure")
            .size()
            .reset_index(name=f"Nb_{formation}")
        )

    liste_dfs_formations = [
        dfs_formations["AAD"],
        dfs_formations["FAAD"],
        dfs_formations["solidar"],
        dfs_formations["SAH"],
        dfs_formations["ASAH"],
        dfs_formations["CRB"],
        dfs_formations["ACRB"],
        dfs_formations["TCAS"],
        dfs_formations["TCAU"],
        dfs_formations["TCEO"],
        dfs_formations["PSP"],
        dfs_formations["IRR"],
        dfs_formations["ATEX"],
        dfs_formations["GQS"],
        df_solidar2020,
    ]

    df_final_formation_initiale = reduce(
        lambda df_gauche, df_droite: df_gauche.merge(
            df_droite,
            on="n_structure",
            how="outer",
        ),
        liste_dfs_formations,
    )

    df_final_formation_initiale = (
        df_final_formation_initiale
        .rename(
            columns={
                "Nb_AAD": "AEO Nb_AAD",
                "Nb_FAAD": "AEO Nb_FAAD",
                "Nb_solidar": "Maraude Nb_SOLIDAR",
                "Nb_SAH": "Aide_alimentaire nb_SAH",
                "Nb_ASAH": "Aide_alimentaire nb_ASAH",
                "Nb_CRB": f"Structure Nb_formes_CRB_{year}",
                "Nb_ACRB": f"Structure Nb_formateurs_CRB_{year}",
                "Nb_TCAS": f"Structure Nb_formes_TCAS_{year}",
                "Nb_TCAU": (
                    f"Dispositifs_d_urgence Nb_formes_TCAU_{year}"
                ),
                "Nb_TCEO": (
                    f"Dispositifs_d_urgence Nb_formes_TCEO_{year}"
                ),
                "Nb_PSP": (
                    f"Dispositifs_d_urgence Nb_formes_PSP_{year}"
                ),
                "Nb_IRR": (
                    f"Dispositifs_d_urgence Nb_formes_IRR_{year}"
                ),
                "Nb_ATEX": "Textile Animateurs_textile",
                "Nb_GQS": (
                    f"Dispositifs_d_urgence Nb_formes_GQS_{year}"
                ),
            }
        )
    )

    # Agrégation par DT à partir du résultat structure.
    mapping_dt = (
        df_ref_structure[
            ["n_structure", "DT_de_rattachement"]
        ]
        .drop_duplicates(subset=["n_structure"])
        .copy()
    )

    df_final_formation_initiale_DT = pd.merge(
        df_final_formation_initiale,
        mapping_dt,
        on="n_structure",
        how="left",
    )

    colonnes_indicateurs = [
        colonne
        for colonne in df_final_formation_initiale.columns
        if colonne != "n_structure"
    ]

    df_final_formation_initiale_DT = (
        df_final_formation_initiale_DT
        .groupby(
            "DT_de_rattachement",
            as_index=False,
        )[
            colonnes_indicateurs
        ]
        .sum()
    )

    return (
        df_final_formation_initiale,
        df_final_formation_initiale_DT, df_nivol_solidar, df_nivol_CRB,
    )


__all__ = [
    "TARGET_DATE",
    "TARGET_YEAR",
    "half_year",
    "FILTRES_BC_SANS_RECYCLAGE",
    "TYPES_FORMATIONS",
    "CODES_SOLIDAR2020",
    "importer_base_contact",
    "importer_rattachement_benevole",
    "calculer_formations_initiales",
]
