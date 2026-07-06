import pandas as pd

# À ADAPTER uniquement si ces fonctions sont définies dans un autre fichier Python.
# Si elles ont déjà été exécutées plus haut dans ton notebook, aucun import supplémentaire
# n'est nécessaire.
#
from pegass import (
    get_codes_is_actifs,
    get_codes_maraude,
    build_ben_activite_synthetique,
)


def calcul_indicateurs_IS(
    df_pegass_ben_activite,
    df_NIVOLS_IS,
    df_ref_structure,
):
    ###############
    # Travail IS actif

    # On récupère les codes utiles
    IS_actifs = get_codes_is_actifs()

    df_pegass_ben_nivol_IS_actifs = (
        df_pegass_ben_activite[
            df_pegass_ben_activite[
                "ACTIVITE_BENEVOLE_ID_FK"
            ].isin(IS_actifs)
        ]
        .copy()
    )

    # On ne prend que les NIVOLS ayant réalisé une activité dans les 3 derniers mois
    df_pegass_ben_nivol_IS_actifs[
        "PEGASS_ACTIVITE_DATE_DEBUT"
    ] = pd.to_datetime(
        df_pegass_ben_nivol_IS_actifs["PEGASS_ACTIVITE_DATE_DEBUT"],
        errors="coerce"
    )

    df_pegass_ben_nivol_IS_actifs = df_pegass_ben_nivol_IS_actifs[
        df_pegass_ben_nivol_IS_actifs["PEGASS_ACTIVITE_DATE_DEBUT"] >= "2026-03-01"
    ]

    df_pegass_ben_nivol_IS_actifs = build_ben_activite_synthetique(
        df_pegass_ben_nivol_IS_actifs
    )

    # On supprime les doublons Structure/NIVOL
    df_pegass_ben_nivol_IS_actifs = df_pegass_ben_nivol_IS_actifs[
        [
            "PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK",
            "PEGASS_ACTIVITE_SEANCE_INSCRIPTION_NIVOL_ID_FK",
        ]
    ].drop_duplicates().copy()

    # On rename les variables IS
    df_pegass_ben_nivol_IS_actifs = (
        df_pegass_ben_nivol_IS_actifs.rename(
            columns={
                "PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK": "n_structure",
                "PEGASS_ACTIVITE_SEANCE_INSCRIPTION_NIVOL_ID_FK": "NIVOL_IS_ACTIF",
            }
        )
    )

    df_NIVOLS_IS = df_NIVOLS_IS.rename(
        columns={"NIVOL_ID_FK": "NIVOL_IS_APTE"}
    )

    df_NIVOLS_IS = df_NIVOLS_IS[["n_structure", "NIVOL_IS_APTE"]]

    df_NIVOLS_IS = df_NIVOLS_IS.drop_duplicates(
        subset=["n_structure", "NIVOL_IS_APTE"]
    )

    df_pegass_ben_nivol_IS_actifs = (
        df_pegass_ben_nivol_IS_actifs.drop_duplicates(
            subset=["n_structure", "NIVOL_IS_ACTIF"]
        )
    )

    df_NIVOLS_IS_merge = df_NIVOLS_IS.copy()

    # On compte les NIVOLS aptes mais inactifs dans une structure
    df_NIVOLS_IS_merge["NIVOL_IS_APTE_INACTIF"] = (
        df_NIVOLS_IS_merge["NIVOL_IS_APTE"].notna()
        & ~df_NIVOLS_IS_merge["NIVOL_IS_APTE"].isin(
            df_pegass_ben_nivol_IS_actifs["NIVOL_IS_ACTIF"].dropna()
        )
    ).astype(int)

    # On compte les NIVOLS actifs
    df_NIVOLS_IS_merge = df_NIVOLS_IS_merge.merge(
        df_pegass_ben_nivol_IS_actifs[
            ["n_structure", "NIVOL_IS_ACTIF"]
        ].assign(NIVOL_IS_ACTIF_STRUCT_RATT=1),
        left_on=["n_structure", "NIVOL_IS_APTE"],
        right_on=["n_structure", "NIVOL_IS_ACTIF"],
        how="left"
    )

    df_NIVOLS_IS_merge["NIVOL_IS_ACTIF_STRUCT_RATT"] = (
        df_NIVOLS_IS_merge["NIVOL_IS_ACTIF_STRUCT_RATT"]
        .fillna(0)
        .astype(int)
    )

    df_NIVOLS_IS_merge = df_NIVOLS_IS_merge.drop(columns="NIVOL_IS_ACTIF")

    # On compte les NIVOLS ayant fait du renfort ailleurs
    comptage_actifs = (
        df_pegass_ben_nivol_IS_actifs["NIVOL_IS_ACTIF"]
        .dropna()
        .value_counts()
        .rename_axis("NIVOL_IS_APTE")
        .reset_index(name="NIVOL_NB_STRUCT_RENFORT")
    )

    # On compte le nombre d'interventions dans une structure
    df_NIVOLS_IS_merge = pd.merge(
        df_NIVOLS_IS_merge,
        comptage_actifs,
        left_on="NIVOL_IS_APTE",
        right_on="NIVOL_IS_APTE",
        how="left"
    )

    # On enlève l'intervention dans sa propre structure
    df_NIVOLS_IS_merge["NIVOL_NB_STRUCT_RENFORT"] = (
        df_NIVOLS_IS_merge["NIVOL_NB_STRUCT_RENFORT"]
        - df_NIVOLS_IS_merge["NIVOL_IS_ACTIF_STRUCT_RATT"]
    )

    # Variable binaire : NIVOL ayant fait du renfort dans une autre structure
    df_NIVOLS_IS_merge["NIVOL_IS_APTE_RENFORT_AUTRE_STRUCTURE"] = (
        df_NIVOLS_IS_merge["NIVOL_NB_STRUCT_RENFORT"]
        .fillna(0)
        .gt(0)
        .astype(int)
    )

    # On groupby et somme par structure
    df_indicateurs_IS = df_NIVOLS_IS_merge[
        [
            "n_structure",
            "NIVOL_IS_APTE_INACTIF",
            "NIVOL_IS_ACTIF_STRUCT_RATT",
            "NIVOL_IS_APTE_RENFORT_AUTRE_STRUCTURE",
        ]
    ]

    df_indicateurs_IS = df_indicateurs_IS.groupby(
        "n_structure",
        as_index=False
    ).sum()

    # Calcul du nombre de bénévoles en renfort
    df_pegass_ben_nivol_IS_actifs_renfort = pd.merge(
        df_NIVOLS_IS,
        df_pegass_ben_nivol_IS_actifs,
        left_on=["n_structure", "NIVOL_IS_APTE"],
        right_on=["n_structure", "NIVOL_IS_ACTIF"],
        how="right",
        indicator=True,
        validate="one_to_one"
    )

    df_pegass_ben_nivol_IS_actifs_renfort["Structure_NB_IS_RENFORT"] = (
        df_pegass_ben_nivol_IS_actifs_renfort["NIVOL_IS_ACTIF"].notna()
        & df_pegass_ben_nivol_IS_actifs_renfort["NIVOL_IS_APTE"].isna()
    ).astype(int)

    df_pegass_ben_nivol_IS_actifs_renfort = (
        df_pegass_ben_nivol_IS_actifs_renfort[
            ["n_structure", "Structure_NB_IS_RENFORT"]
        ]
    )

    df_pegass_ben_nivol_IS_actifs_renfort = (
        df_pegass_ben_nivol_IS_actifs_renfort.groupby(
            "n_structure",
            as_index=False
        ).sum()
    )

    # On merge les 2 dfs pour avoir tout sur un seul df
    df_indicateurs_IS_Structure = pd.merge(
        df_indicateurs_IS,
        df_pegass_ben_nivol_IS_actifs_renfort,
        on="n_structure",
        how="outer"
    )

    # On rename les variables
    df_indicateurs_IS_Structure = df_indicateurs_IS_Structure.rename(
        columns={
            "NIVOL_IS_APTE_INACTIF": "Secours Nb_IS_apte_inactif",
            "NIVOL_IS_ACTIF_STRUCT_RATT": "Secours Nb_IS_actifs",
            "NIVOL_IS_APTE_RENFORT_AUTRE_STRUCTURE": "Secours Nb_renfort_IS_OUT",
            "Structure_NB_IS_RENFORT": "Secours Nb_renfort_IS_IN",
        }
    )

    # On fait le calcul par DT
    df_ref_structure_DT = (df_ref_structure[["n_structure-ratt","DT_de_rattachement"]].dropna(subset=["n_structure-ratt", "DT_de_rattachement"]).drop_duplicates())

    df_indicateurs_IS_DT = pd.merge(
        df_indicateurs_IS_Structure,
        df_ref_structure_DT,
        left_on="n_structure",
        right_on="n_structure-ratt",
        how="left"
    )

    df_indicateurs_IS_DT = df_indicateurs_IS_DT[
        [
            "DT_de_rattachement",
            "Secours Nb_IS_apte_inactif",
            "Secours Nb_IS_actifs",
            "Secours Nb_renfort_IS_OUT",
            "Secours Nb_renfort_IS_IN",
        ]
    ]

    df_indicateurs_IS_DT = df_indicateurs_IS_DT.groupby(
        "DT_de_rattachement",
        as_index=False
    ).sum()

    return df_indicateurs_IS_DT, df_indicateurs_IS_Structure


def calcul_indicateurs_maraude(
    df_pegass_ben_activite_synthetique,
    df_nivol_solidar,
    df_ref_structure,
):
    ###########################################################################
    # Travail maraude

    # On récupère les codes utiles
    Activite_maraude = get_codes_maraude()

    # On récupère les NIVOLS associés aux codes
    df_pegass_ben_nivol_Maraude = (
        df_pegass_ben_activite_synthetique[
            df_pegass_ben_activite_synthetique[
                "ACTIVITE_BENEVOLE_ID_FK"
            ].isin(Activite_maraude)
        ]
        .copy()
    )

    # On supprime les doublons Structure/NIVOL
    df_pegass_ben_nivol_Maraude = df_pegass_ben_nivol_Maraude[
        [
            "PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK",
            "PEGASS_ACTIVITE_SEANCE_INSCRIPTION_NIVOL_ID_FK",
        ]
    ].drop_duplicates().copy()

    df_maraude_benevole_actif = pd.merge(
        df_pegass_ben_nivol_Maraude,
        df_nivol_solidar[["NIVOL_ID_FK"]].drop_duplicates(),
        left_on="PEGASS_ACTIVITE_SEANCE_INSCRIPTION_NIVOL_ID_FK",
        right_on="NIVOL_ID_FK",
        how="left",
        validate="many_to_one"
    )

    # On met 1 si on a une correspondance de NIVOL
    df_maraude_benevole_actif["Maraude Nb_benevoles_actifs_formes"] = (
        df_maraude_benevole_actif["NIVOL_ID_FK"]
        .notna()
        .astype(int)
    )

    df_maraude_benevole_actif = df_maraude_benevole_actif[
        [
            "PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK",
            "Maraude Nb_benevoles_actifs_formes",
        ]
    ]

    # On fait le calcul par structure
    df_maraude_benevole_actif = pd.merge(
        df_maraude_benevole_actif,
        df_ref_structure[["n_structure", "n_structure-ratt"]],
        left_on="PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK",
        right_on="n_structure",
        how="left"
    )

    df_maraude_benevole_actif = df_maraude_benevole_actif[
        ["n_structure-ratt", "Maraude Nb_benevoles_actifs_formes"]
    ]

    df_maraude_benevole_actif = df_maraude_benevole_actif.rename(
        columns={"n_structure-ratt": "n_structure"}
    )

    df_maraude_benevole_actif_structure = (
        df_maraude_benevole_actif.groupby(
            "n_structure",
            as_index=False
        ).sum()
    )

    # On fait le calcul par DT
    df_maraude_benevole_actif_DT = pd.merge(
        df_maraude_benevole_actif_structure,
        df_ref_structure[["n_structure", "DT_de_rattachement"]],
        left_on="n_structure",
        right_on="n_structure",
        how="left"
    )

    df_maraude_benevole_actif_DT = df_maraude_benevole_actif_DT[
        [
            "DT_de_rattachement",
            "Maraude Nb_benevoles_actifs_formes",
        ]
    ]

    df_maraude_benevole_actif_DT = df_maraude_benevole_actif_DT.groupby(
        "DT_de_rattachement",
        as_index=False
    ).sum()

    return (
        df_maraude_benevole_actif_DT,
        df_maraude_benevole_actif_structure,
    )


def calcul_indicateurs_CRB(
    df_NIVOLS_Nouveaux_benevoles_gaia,
    df_nivol_CRB,
    df_ref_structure,
    target_date,
):
    ###########################################################################
    # Calcul CRB

    df_NIVOLS_Nouveaux_benevoles_gaia = (
        df_NIVOLS_Nouveaux_benevoles_gaia[
            [
                "rattachement_benevole_nivol_id_fk",
                "rattachement_benevole_structure_id_fk",
            ]
        ].drop_duplicates()
    )

    df_nivol_CRB = df_nivol_CRB[["NIVOL_ID_FK"]].drop_duplicates()

    target = pd.Timestamp(target_date)
    year = target.year

    df_nouveaux_CRB = pd.merge(
        df_NIVOLS_Nouveaux_benevoles_gaia,
        df_nivol_CRB,
        left_on="rattachement_benevole_nivol_id_fk",
        right_on="NIVOL_ID_FK",
        how="left",
        validate="many_to_one"
    )

    # On met 1 si on a une correspondance de NIVOL
    df_nouveaux_CRB[f"Structure Nb_nvx_formes_CRB_{year}"] = (
        df_nouveaux_CRB["NIVOL_ID_FK"]
        .notna()
        .astype(int)
    )

    df_nouveaux_CRB = df_nouveaux_CRB.rename(
        columns={
            "rattachement_benevole_structure_id_fk": "n_structure"
        }
    )

    df_nouveaux_CRB = df_nouveaux_CRB[
        ["n_structure", f"Structure Nb_nvx_formes_CRB_{year}"]
    ]

    # On fait le calcul par structure
    df_nouveaux_CRB = pd.merge(
        df_nouveaux_CRB,
        df_ref_structure[
            ["n_structure", "n_structure-ratt"]
        ].drop_duplicates(),
        on="n_structure",
        how="left"
    )

    df_nouveaux_CRB = df_nouveaux_CRB[
        ["n_structure-ratt", f"Structure Nb_nvx_formes_CRB_{year}"]
    ]

    df_nouveaux_CRB = df_nouveaux_CRB.rename(
        columns={"n_structure-ratt": "n_structure"}
    )

    df_nouveaux_CRB_structure = df_nouveaux_CRB.groupby(
        "n_structure",
        as_index=False
    ).sum()

    # On fait le calcul par DT
    df_nouveaux_CRB_DT = pd.merge(
        df_nouveaux_CRB_structure,
        df_ref_structure[
            ["n_structure", "DT_de_rattachement"]
        ].drop_duplicates(),
        left_on="n_structure",
        right_on="n_structure",
        how="left"
    )

    df_nouveaux_CRB_DT = df_nouveaux_CRB_DT[
        [
            "DT_de_rattachement",
            f"Structure Nb_nvx_formes_CRB_{year}",
        ]
    ]

    df_nouveaux_CRB_DT = df_nouveaux_CRB_DT.groupby(
        "DT_de_rattachement",
        as_index=False
    ).sum()

    return df_nouveaux_CRB_DT, df_nouveaux_CRB_structure


# EXEMPLES D'APPEL
#
# df_indicateurs_IS_DT, df_indicateurs_IS_Structure = calcul_indicateurs_IS(
#     df_pegass_ben_activite,
#     df_NIVOLS_IS,
#     df_ref_structure,
# )
#
# (
#     df_maraude_benevole_actif_DT,
#     df_maraude_benevole_actif_structure,
# ) = calcul_indicateurs_maraude(
#     df_pegass_ben_activite_synthetique,
#     df_nivol_solidar,
#     df_ref_structure,
# )
#
# df_nouveaux_CRB_DT, df_nouveaux_CRB_structure = calcul_indicateurs_CRB(
#     df_NIVOLS_Nouveaux_benevoles_gaia,
#     df_nivol_CRB,
#     df_ref_structure,
#     target_date,
# )
