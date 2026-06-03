import pandas as pd
import numpy as np
import re


"""##Appel des fonction PEGASS.PY"""

def import_tables_PEGASS(client,target_date = '2025-12-31',  project_id="crf-pat"):
    """
    Charge les tables BigQuery nécessaires et renvoie tous les DataFrames importés
    (et ref_structure1 calculé comme dans ton code).
    """
    target = pd.Timestamp(target_date)
    year = target.year

    dataset_id = f"dataset_PAT_{year}"

    # ---- Imports ----
    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.crf_activite_ref_activite_benevole`
    """
    df_ref_activite_benevole = client.query(query).to_dataframe()

    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.crf_pat_{year}_pegass_activite`
    """
    df_pegass_activite = client.query(query).to_dataframe()

    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.crf_pat_{year}_pegass_activite_seance`
    """
    df_pegass_activite_seance = client.query(query).to_dataframe()

    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.crf_pat_{year}_pegass_activite_seance_inscription`
    """
    df_pegass_activite_seance_inscription = client.query(query).to_dataframe()

    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.Ref_structure`
    """
    df_ref_structure = client.query(query).to_dataframe()

    # Preparation ref structure (comme ton code)
    ref_structure1 = df_ref_structure[
        (df_ref_structure["type_structure"] == "UNITE LOCALE - UL")
        | (df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT")
    ]

    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.rattachement_court`
    """
    df_rattachement_court = client.query(query).to_dataframe()

    query = f"""
    SELECT *
    FROM `{project_id}.{dataset_id}.crf_as_ref_action_groupe_action`
    """
    df_ref_action_groupe_action = client.query(query).to_dataframe()

    # Renommage colonnes (comme ton code)
    df_ref_action_groupe_action.columns = ["action_id_fk", "ACTION_LIBELLE", "GROUPE_ACTION_ID_FK"]
    df_pegass_activite["PEGASS_ACTIVITE_DATE_DEBUT"] = pd.to_datetime(df_pegass_activite["PEGASS_ACTIVITE_DATE_DEBUT"], errors="coerce")

    df_pegass_activite = df_pegass_activite[(df_pegass_activite["PEGASS_ACTIVITE_DATE_DEBUT"].dt.year == year) & (df_pegass_activite["PEGASS_ACTIVITE_DATE_DEBUT"] <= target)]


    return (
        df_ref_activite_benevole,
        df_pegass_activite,
        df_pegass_activite_seance,
        df_pegass_activite_seance_inscription,
        # ref_structure1,
        df_rattachement_court,
        df_ref_action_groupe_action
    )


def get_codes_activite_ben():
    return [
        10119, 10122, 10123, 10125, 10126, 10127, 10128, 10129,
        10132, 10133, 10134, 10135, 10136, 10137,
        10032, 10033, 10034, 10035, 11110,
        10015, 10046, 10047, 11126,
        10105, 10106, 11007, 10108, 10113
    ]

def get_codes_maraude():
    return [10032, 10033, 10034, 10035, 10036, 10037, 11110]

def get_codes_nb_exercice():
    return [10122, 10123]

def get_codes_nb_operations():
    return [11015, 10132, 10133, 10134, 10135, 10136, 10137, 10119, 10125, 10126, 10127, 10128, 10129]

def get_codes_aeo():
    return [10015]

def get_codes_domiciliation():
    return [10046]

def get_codes_ecrivain_public():
    return [10047, 11126]

def get_codes_dps():
    return [10105, 10106, 11007, 10108, 10113]

def get_codes_is_actifs():
    return [10105, 10106, 10108, 10113, 10114, 10115, 10116]

# =========================================================
# FONCTIONS DE MERGE / PRÉPARATION PEGASS
# =========================================================

def merge_action_activite(df_ref_action_groupe_action, df_ref_activite_benevole):
    return pd.merge(
        df_ref_action_groupe_action,
        df_ref_activite_benevole,
        on="action_id_fk",
        how="left"
    )


def rename_pegass_activite_id(df_pegass_activite):
    return df_pegass_activite.rename(
        columns={"PEGASS_ACTIVITE_ID_PK": "PEGASS_ACTIVITE_ID_FK"}
    )


def merge_activite_seance(df_pegass_activite_seance, df_pegass_activite):
    return pd.merge(
        df_pegass_activite_seance,
        df_pegass_activite,
        on="PEGASS_ACTIVITE_ID_FK",
        how="left"
    )


def build_ben_activite(df_pegass_activite, df_pegass_activite_seance_inscription):
    return pd.merge(
        df_pegass_activite,
        df_pegass_activite_seance_inscription,
        on="PEGASS_ACTIVITE_ID_FK",
        how="right"
    )


def filter_inscriptions_valides(df_pegass_ben_activite):
    return df_pegass_ben_activite[
        df_pegass_ben_activite["PEGASS_ACTIVITE_SEANCE_INSCRIPTION_STATUT"] == "Valide"
    ].copy()


def build_ben_activite_synthetique(df_pegass_ben_activite):
    df_syn = df_pegass_ben_activite[[
        "PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK",
        "ACTIVITE_BENEVOLE_ID_FK",
        "PEGASS_ACTIVITE_SEANCE_INSCRIPTION_NIVOL_ID_FK"
    ]].copy()

    return df_syn.drop_duplicates()


# =========================================================
# FONCTIONS DE FILTRE ACTIVITÉS
# =========================================================

def filter_ref_action_activite(df_ref_action_activite, codes_activite_ben=None):
    if codes_activite_ben is None:
        codes_activite_ben = get_codes_activite_ben()

    return df_ref_action_activite[
        df_ref_action_activite["activite_benevole_id_pk"].isin(codes_activite_ben)
    ].copy()


def rename_activite_benevole_id(df_ref_action_activite_filtre):
    return df_ref_action_activite_filtre.rename(
        columns={"activite_benevole_id_pk": "ACTIVITE_BENEVOLE_ID_FK"}
    )


def merge_on_activite_benevole(df_left, df_ref_action_activite_filtre, how="inner"):
    return pd.merge(
        df_left,
        df_ref_action_activite_filtre,
        on="ACTIVITE_BENEVOLE_ID_FK",
        how=how
    )


def drop_duplicates_seance(df, col="PEGASS_ACTIVITE_SEANCE_ID_FK"):
    return df.drop_duplicates(col)


# =========================================================
# FONCTIONS INDICATEURS BÉNÉVOLES
# =========================================================

def count_ben_structure(df):
    return (
        df.groupby("PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK", as_index=False)
          .size()
          .rename(columns={
              "PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK": "n_structure",
              "size": "nb_benevoles"
          })
    )


def filter_ben_by_activite(df_synth, codes_activite):
    df_out = df_synth[
        df_synth["ACTIVITE_BENEVOLE_ID_FK"].isin(codes_activite)
    ].copy()

    df_out = df_out.drop(columns=["ACTIVITE_BENEVOLE_ID_FK"])

    return df_out.drop_duplicates()


def compute_nb_benevoles_indicator(df_synth, codes_activite, out_col_name):
    df_filtered = filter_ben_by_activite(df_synth, codes_activite)
    df_count = count_ben_structure(df_filtered)

    return df_count.rename(columns={"nb_benevoles": out_col_name})


# =========================================================
# FONCTION STATUT ACTION MENÉE
# =========================================================

def add_statut_action(
    df,
    col_nb,
    out_col="activité menée",
    label_yes="Action menée",
    label_no="Action non menée",
    treat_zero_as_no=True,
    copy=True
):
    df_out = df.copy() if copy else df

    nb = pd.to_numeric(df_out[col_nb], errors="coerce")

    if treat_zero_as_no:
        mask_yes = nb.notna() & (nb != 0)
    else:
        mask_yes = nb.notna()

    df_out[out_col] = np.where(mask_yes, label_yes, label_no)

    return df_out


# =========================================================
# FONCTIONS INDICATEURS ACTIVITÉS
# =========================================================

def calc_nb_activite_pegass(df):
    return (
        df.groupby(
            [
                "PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK",
                "ACTIVITE_BENEVOLE_ID_FK"
            ],
            dropna=False
        )
        .size()
        .reset_index(name="nb_activite")
        .rename(columns={
            "PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK": "n_structure",
            "ACTIVITE_BENEVOLE_ID_FK": "N° activité"
        })
    )


def indicator_nb_activites(df_activite_counts, codes_activite, out_col):
    df_out = df_activite_counts[
        df_activite_counts["N° activité"].isin(codes_activite)
    ].copy()

    df_out = (
        df_out
        .rename(columns={"nb_activite": out_col})
        .drop(columns=["N° activité"])
    )

    return df_out.groupby("n_structure", as_index=False)[out_col].sum()

def calcul_PEGASS_indicateurs(
    df_ref_structure,  # conservé dans la signature mais non utilisé
    df_ref_action_groupe_action,
    df_ref_activite_benevole,
    df_pegass_activite,
    df_pegass_activite_seance,
    df_pegass_activite_seance_inscription,
    df_rattachement_court,  # conservé dans la signature mais non utilisé
    df_nivols_gaia
):
    """
    Version sans rattachement structure.

    Principe :
    - On ne travaille plus avec le référentiel structure.
    - On ne rattache plus les IL / AL à une UL ou DT.
    - On calcule les indicateurs directement sur :
      PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK
    - On ne calcule plus Indics_pegass_DT, car cela nécessite un rattachement à une DT.
    """

    # =========================================================
    # 1. Merge des tables d'activités
    # =========================================================

    df_ref_action_activite = merge_action_activite(
        df_ref_action_groupe_action,
        df_ref_activite_benevole
    )

    df_pegass_activite = rename_pegass_activite_id(df_pegass_activite)

    # IMPORTANT :
    # on ne filtre plus df_pegass_activite avec df_ref_structure
    # on garde directement la structure PEGASS :
    # PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK

    df_pegass_activite_merge = merge_activite_seance(
        df_pegass_activite_seance,
        df_pegass_activite
    )

    df_pegass_ben_activite = build_ben_activite(
        df_pegass_activite,
        df_pegass_activite_seance_inscription
    )

    df_pegass_ben_activite = filter_inscriptions_valides(
        df_pegass_ben_activite
    )

    df_pegass_ben_activite_synthetique = build_ben_activite_synthetique(
        df_pegass_ben_activite
    )

    # =========================================================
    # 2. Filtre sur les activités utiles
    # =========================================================

    codes_activite_ben = get_codes_activite_ben()

    df_ref_action_activite_filtre = filter_ref_action_activite(
        df_ref_action_activite,
        codes_activite_ben
    )

    df_ref_action_activite_filtre = rename_activite_benevole_id(
        df_ref_action_activite_filtre
    )

    df_pegass_activite_merge2 = merge_on_activite_benevole(
        df_pegass_activite_merge,
        df_ref_action_activite_filtre,
        how="inner"
    )

    df_pegass_ben_activite = merge_on_activite_benevole(
        df_pegass_ben_activite,
        df_ref_action_activite_filtre,
        how="inner"
    )

    df_pegass_activite_merge2 = drop_duplicates_seance(
        df_pegass_activite_merge2,
        col="PEGASS_ACTIVITE_SEANCE_ID_FK"
    )

    # =========================================================
    # 3. Codes activités
    # =========================================================

    Activite_maraude = get_codes_maraude()
    Nb_Exercice = get_codes_nb_exercice()
    NB_operations = get_codes_nb_operations()
    AEO = get_codes_aeo()
    DPS = get_codes_dps()
    IS_actifs = get_codes_is_actifs()
    Domiciliation = get_codes_domiciliation()
    Ecrivain_public = get_codes_ecrivain_public()

    # =========================================================
    # 4. Filtre des bénévoles à date fixe
    # =========================================================

    liste_nivols_date_fixe = (
        df_nivols_gaia["rattachement_benevole_nivol_id_fk"]
        .drop_duplicates()
        .tolist()
    )

    df_pegass_ben_activite_synthetique = (
        df_pegass_ben_activite_synthetique[
            df_pegass_ben_activite_synthetique[
                "PEGASS_ACTIVITE_SEANCE_INSCRIPTION_NIVOL_ID_FK"
            ].isin(liste_nivols_date_fixe)
        ]
    )

    # =========================================================
    # 5. Calcul du nombre de bénévoles actifs
    # =========================================================

    nb_ben_Maraude_Pegass = compute_nb_benevoles_indicator(
        df_pegass_ben_activite_synthetique,
        Activite_maraude,
        "Maraude Nb_benevoles_actifs"
    )

    nb_ben_AEO_Pegass = compute_nb_benevoles_indicator(
        df_pegass_ben_activite_synthetique,
        AEO,
        "AEO Nb_benevoles_actifs"
    )

    nb_ben_IS_Pegass = compute_nb_benevoles_indicator(
        df_pegass_ben_activite_synthetique,
        IS_actifs,
        "IS Nb_benevoles_actifs"
    )

    # =========================================================
    # 6. Calcul du nombre d'activités par structure PEGASS
    # =========================================================

    nb_activite_Pegass = calc_nb_activite_pegass(
        df_pegass_activite_merge2
    )

    nb_Maraude_Pegass1 = indicator_nb_activites(
        nb_activite_Pegass,
        Activite_maraude,
        "Maraude Nb_maraudes_PEGASS"
    )

    nb_operations_Pegass1 = indicator_nb_activites(
        nb_activite_Pegass,
        NB_operations,
        "Dispositifs_d_urgence Nb_operations"
    )

    nb_Exercice_Pegass1 = indicator_nb_activites(
        nb_activite_Pegass,
        Nb_Exercice,
        "Dispositifs_d_urgence Nb_exercices"
    )

    nb_AEO_Pegass1 = indicator_nb_activites(
        nb_activite_Pegass,
        AEO,
        "nb_activite_AEO"
    )

    nb_Domiciliation_Pegass = indicator_nb_activites(
        nb_activite_Pegass,
        Domiciliation,
        "AEO activite_domiciliation_fixe"
    )

    nb_Ecrivain_public_Pegass = indicator_nb_activites(
        nb_activite_Pegass,
        Ecrivain_public,
        "AEO activite_ecrivain_public_fixe"
    )

    nb_Maraude_Pegass_verif = nb_Maraude_Pegass1.copy()

    # =========================================================
    # 7. Statuts AEO / domiciliation / écrivain public
    # =========================================================

    nb_AEO_Pegass1 = add_statut_action(
        nb_AEO_Pegass1,
        col_nb="nb_activite_AEO",
        out_col="AEO Structure_activite_fixe",
        label_yes="Activités AEO/AAD menée en fixe",
        treat_zero_as_no=True
    )

    nb_Domiciliation_Pegass1 = add_statut_action(
        nb_Domiciliation_Pegass,
        col_nb="AEO activite_domiciliation_fixe",
        out_col="AEO Structure_domiciliation_fixe",
        label_yes="Domiciliation",
        treat_zero_as_no=True
    )

    nb_Ecrivain_public_Pegass1 = add_statut_action(
        nb_Ecrivain_public_Pegass,
        col_nb="AEO activite_ecrivain_public_fixe",
        out_col="AEO Structure_ecrivain_public_fixe",
        label_yes="Ecrivain public",
        treat_zero_as_no=True
    )

    # =========================================================
    # 8. Merge global des indicateurs structure
    # =========================================================

    Indics_pegass = pd.merge(
        nb_Maraude_Pegass1,
        nb_operations_Pegass1,
        on="n_structure",
        how="outer"
    )

    Indics_pegass = pd.merge(
        Indics_pegass,
        nb_Exercice_Pegass1,
        on="n_structure",
        how="outer"
    )

    Indics_pegass = pd.merge(
        Indics_pegass,
        nb_ben_Maraude_Pegass,
        on="n_structure",
        how="outer"
    )

    Indics_pegass = pd.merge(
        Indics_pegass,
        nb_ben_IS_Pegass,
        on="n_structure",
        how="outer"
    )

    Indics_pegass = pd.merge(
        Indics_pegass,
        nb_ben_AEO_Pegass,
        on="n_structure",
        how="outer"
    )

    Indics_pegass_struct = pd.merge(
        Indics_pegass,
        nb_AEO_Pegass1,
        on="n_structure",
        how="outer"
    )

    Indics_pegass_struct = pd.merge(
        Indics_pegass_struct,
        nb_Ecrivain_public_Pegass1,
        on="n_structure",
        how="outer"
    )

    Indics_pegass_struct = pd.merge(
        Indics_pegass_struct,
        nb_Domiciliation_Pegass1,
        on="n_structure",
        how="outer"
    )




    # =========================================================
    # 9. Création de la variable Activités AAD facultatives
    # =========================================================

    Indics_pegass_struct["Activités AAD facultatives"] = (
        Indics_pegass_struct["AEO Structure_ecrivain_public_fixe"]
        .fillna("")
        .astype(str)
        + " "
        + Indics_pegass_struct["AEO Structure_domiciliation_fixe"]
        .fillna("")
        .astype(str)
    ).str.strip()

    Indics_pegass_struct["Activités AAD facultatives"] = (
        Indics_pegass_struct["Activités AAD facultatives"]
        .replace({
            "Ecrivain public Domiciliation": "Domiciliation & Ecrivain public"
        })
    )

    Indics_pegass_struct["Activités AAD facultatives"] = (
        Indics_pegass_struct["Activités AAD facultatives"]
        .replace(r"^\s*$", np.nan, regex=True)
    )

    # =========================================================
    # 10. Nettoyage du df final structure
    # =========================================================

    colonnes_finales_struct = [
        "n_structure",
        "Maraude Nb_maraudes_PEGASS",
        #"Dispositifs_d_urgence Nb_operations",
        #"Dispositifs_d_urgence Nb_exercices",
        "AEO Structure_activite_fixe",
        "AEO Structure_domiciliation_fixe",
        "AEO Structure_ecrivain_public_fixe",
        "Maraude Nb_benevoles_actifs",
        "AEO Nb_benevoles_actifs",
        "IS Nb_benevoles_actifs"
        #"Activités AAD facultatives"
        #"nb_activite_AEO"
        
    ]

    Indics_pegass_struct = Indics_pegass_struct.reindex(
        columns=colonnes_finales_struct
    )

    # Pas de calcul DT dans cette version :
    # sans référentiel structure / rattachement, on ne peut pas produire
    # DT_de_rattachement proprement.
    Indics_pegass_DT = pd.DataFrame()

    # =========================================================
    # 11. Return
    # =========================================================

    return {
        # tables ref / bases
        "df_ref_action_activite": df_ref_action_activite,
        "df_ref_action_activite_filtre": df_ref_action_activite_filtre,

        # bases pegass
        "df_pegass_activite": df_pegass_activite,
        "df_pegass_activite_merge": df_pegass_activite_merge,
        "df_pegass_activite_merge2": df_pegass_activite_merge2,
        "df_pegass_ben_activite": df_pegass_ben_activite,
        "df_pegass_ben_activite_synthetique": df_pegass_ben_activite_synthetique,

        # indicateurs intermédiaires
        "nb_ben_Maraude_Pegass": nb_ben_Maraude_Pegass,
        "nb_ben_AEO_Pegass": nb_ben_AEO_Pegass,
        "nb_ben_IS_Pegass": nb_ben_IS_Pegass,
        "nb_activite_Pegass": nb_activite_Pegass,
        "nb_Maraude_Pegass1": nb_Maraude_Pegass1,
        "nb_operations_Pegass1": nb_operations_Pegass1,
        "nb_Exercice_Pegass1": nb_Exercice_Pegass1,
        "nb_AEO_Pegass1": nb_AEO_Pegass1,
        "nb_Maraude_Pegass_verif": nb_Maraude_Pegass_verif,
        "nb_Domiciliation_Pegass": nb_Domiciliation_Pegass,
        "nb_Ecrivain_public_Pegass": nb_Ecrivain_public_Pegass,

        # outputs finaux
        "Indics_pegass": Indics_pegass,
        "Indics_pegass_struct": Indics_pegass_struct,
        #"Indics_pegass_DT": Indics_pegass_DT,

        # codes
        "codes_activite_ben": codes_activite_ben,
        "Activite_maraude": Activite_maraude,
        "Nb_Exercice": Nb_Exercice,
        "NB_operations": NB_operations,
        "AEO": AEO,
        "DPS": DPS,
        "IS_actifs": IS_actifs,
        "Domiciliation": Domiciliation,
        "Ecrivain_public": Ecrivain_public,
    }

def calcul_PEGASS_DT_indicateurs(Indics_pegass_struct, df_ref_structure):

    # On travaille sur une copie pour ne pas modifier le df structure original
    Indics_pegass_struct = Indics_pegass_struct.copy()

    # =========================================================
    # 1. Transformer les colonnes texte AEO en compteurs numériques
    # =========================================================

    Indics_pegass_struct["AEO Nb_activites_fixes"] = (
        Indics_pegass_struct["AEO Structure_activite_fixe"]
        .apply(lambda x: 1 if x == "Activités AEO/AAD menée en fixe" else 0)
    )

    Indics_pegass_struct["AEO Structure_domiciliation_fixe"] = (
        Indics_pegass_struct["AEO Structure_domiciliation_fixe"]
        .apply(lambda x: 1 if x == "Domiciliation" else 0)
    )

    Indics_pegass_struct["AEO Structure_ecrivain_public_fixe"] = (
        Indics_pegass_struct["AEO Structure_ecrivain_public_fixe"]
        .apply(lambda x: 1 if x == "Ecrivain public" else 0)
    )

    # =========================================================
    # 2. Rattacher chaque structure à sa structure de rattachement
    # =========================================================

    Indics_pegass_struct = pd.merge(
        Indics_pegass_struct,
        df_ref_structure[["n_structure", "n_structure-ratt"]],
        on="n_structure",
        how="inner"
    )

    # On remplace n_structure par la structure de rattachement
    Indics_pegass_struct = Indics_pegass_struct.drop(
        columns=["n_structure"],
        errors="ignore"
    )

    Indics_pegass_struct = Indics_pegass_struct.rename(
        columns={"n_structure-ratt": "n_structure"}
    )

    # =========================================================
    # 3. Agréger les indicateurs au niveau structure de rattachement
    # =========================================================

    Indics_pegass_struct = (
        Indics_pegass_struct
        .groupby("n_structure", as_index=False)
        .sum(numeric_only=True)
    )

    Indics_pegass_struct["AEO Structure_ecrivain_public_fixe"] = (
    Indics_pegass_struct["AEO Structure_ecrivain_public_fixe"]
    .replace(2, 1)
    )

    Indics_pegass_struct['AEO Structure_domiciliation_fixe'] = (
        Indics_pegass_struct['AEO Structure_domiciliation_fixe']
        .replace(2, 1)
    )

    # =========================================================
    # 4. Rattacher les structures de rattachement à leur DT
    # =========================================================

    Indics_pegass_DT = pd.merge(
        Indics_pegass_struct,
        df_ref_structure[["n_structure", "DT_de_rattachement"]],
        on="n_structure",
        how="inner"
    )

    # Recréer un indicateur structure AEO fixe :
    # 1 si au moins une activité AEO/AAD fixe sur la structure de rattachement
    Indics_pegass_DT["AEO Structure_activite_fixe"] = (
        Indics_pegass_DT["AEO Nb_activites_fixes"]
        .apply(lambda x: 1 if x > 0 else 0)
    )

    # =========================================================
    # 5. Agréger au niveau DT
    # =========================================================

    Indics_pegass_DT = (
        Indics_pegass_DT
        .groupby("DT_de_rattachement", as_index=False)
        .sum(numeric_only=True)
    )

    Indics_pegass_DT = Indics_pegass_DT.drop(
        columns=["n_structure"],
        errors="ignore"
    )

    return Indics_pegass_DT, Indics_pegass_struct