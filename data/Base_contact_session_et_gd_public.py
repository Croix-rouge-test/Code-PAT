import pandas as pd
import re
import sys
import os

sys.path.append(os.path.abspath("/Code-PAT"))

from utils import *


# ============================================================
# I. COMPTER LES FORMES GD PUBLIC
# ============================================================

# ============================================================
# 1. CODES DE FORMATION UTILISÉS
# ============================================================

filtres_formation_grand_public = {
    "PSC": [
        "PSC1 IRR",
        "EPSC1",
        "RECPSC1",
        "PSC1",
        "PSC1 AC",
        "PSC",
        "PSC IRR",
        "EPSC",
        "PSC AC",
        "FCPSC",
    ],

    "GQS": [
        "GQS",
        "GQS AC",
        "FIPS",
        "FIPS2",
    ],

    "IPS": [
        "IPS",
        "IPS SR",
        "IPSE",
        "IPSEF",
        "IPSJ",
        "IPSJP",
        "IPSM",
        "IPSP",
        "IPS AC",
    ],

    "IPSEN": [
        "IPSEN",
    ],
}


# ============================================================
# 2. FONCTIONS DE RATTACHEMENT AUX DT
# ============================================================

def keep_integer(x):
    if x is None:
        return None

    return re.sub(r"\D", "", str(x))


def dt_rattachement(df, df_ref_structure):
    """
    Associe chaque structure à sa DT de rattachement.
    """

    df_return = df.merge(
        df_ref_structure[
            ["n_structure", "DT_de_rattachement"]
        ].drop_duplicates(),
        on="n_structure",
        how="left",
    )

    df_return["DT_de_rattachement"] = (
        df_return["DT_de_rattachement"]
        .apply(lambda x: keep_integer(x))
    )

    return df_return


# ============================================================
# 3. IMPORT ET PRÉPARATION DE LA BASE FORMATION
# ============================================================

def clean_formations_grand_public(
    client,
    df_ref_structure,
):
    """
    Importe et prépare les données nécessaires au calcul des
    nombres de personnes formées PSC, GQS, IPS et IPSEN.

    La structure retenue est la structure organisatrice
    de la session de formation.
    """

    codes_utiles = list({
        code
        for liste_codes in filtres_formation_grand_public.values()
        for code in liste_codes
    })

    query_formation_session_resultat = """
        SELECT *
        FROM `crf-pat.dataset_PAT_2026.crf_pat_2026_formation_session_resultat`
    """

    df_formation_session_resultat = (
        client
        .query(query_formation_session_resultat)
        .to_dataframe()
    )

    # Conversion de la date d'obtention
    df_formation_session_resultat[
        "FORMATION_DATE_OBTENTION"
    ] = pd.to_datetime(
        df_formation_session_resultat[
            "FORMATION_DATE_OBTENTION"
        ],
        errors="coerce",
    )

    # Conservation uniquement des codes utiles
    df_formation_session_resultat_fpg = (
        df_formation_session_resultat[
            df_formation_session_resultat[
                "FORMATION_CODE"
            ].isin(codes_utiles)
        ]
        .copy()
    )

    # La structure utilisée est la structure organisatrice
    # de la session
    df_formation_session_resultat_fpg = (
        df_formation_session_resultat_fpg
        .rename(
            columns={
                "FORMATION_SESSION_STRUCTURE_ID_FK":
                    "n_structure"
            }
        )
    )

    # Remontée éventuelle des structures locales vers leur
    # structure de rattachement
    df_formation_session_resultat_fpg = (
        apply_rattachement_successif(
            df_ref_structure,
            df_formation_session_resultat_fpg,
            col="n_structure",
        )
    )

    # Conservation uniquement des structures présentes
    # dans le référentiel
    liste_structures = (
        df_ref_structure["n_structure"]
        .drop_duplicates()
        .tolist()
    )

    df_formation_session_resultat_fpg = (
        df_formation_session_resultat_fpg[
            df_formation_session_resultat_fpg[
                "n_structure"
            ].isin(liste_structures)
        ]
        .copy()
    )

    # Ajout de la DT de rattachement
    df_formation_session_resultat_fpg = (
        dt_rattachement(
            df_formation_session_resultat_fpg,
            df_ref_structure,
        )
    )

    return df_formation_session_resultat_fpg


# ============================================================
# 4. CALCUL DES QUATRE INDICATEURS
# ============================================================

def nb_suivi_form_tous(
    df,
    filtres_formation_grand_public,
    col_groupby,
    target_date,
):
    """
    Calcule le nombre de non-bénévoles formés aux formations
    PSC, GQS, IPS et IPSEN.

    Le comptage est effectué en NIVOL distincts.
    """

    target = pd.Timestamp(target_date)
    year = target.year

    # Population retenue :
    # - personnes non identifiées comme bénévoles dans l'année ;
    # - formation obtenue pendant l'année cible ;
    # - formation obtenue au plus tard à la date cible.
    df_res = df[
        (
            df["FORMATION_BENEVOLE_DANS_L_ANNEE"]
            != "Oui"
        )
        & (
            df["FORMATION_DATE_OBTENTION"]
            <= target
        )
        & (
            df["FORMATION_DATE_OBTENTION"].dt.year
            == year
        )
    ].copy()

    indic_filtres = [
        (
            f"Formation_grand_public Nb_formes_PSC_{year}",
            "PSC",
        ),
        (
            f"Formation_grand_public Nb_formes_GQS_{year}",
            "GQS",
        ),
        (
            f"Formation_grand_public Nb_formes_IPS_{year}",
            "IPS",
        ),
        (
            f"Formation_grand_public Nb_formes_IPSEN_{year}",
            "IPSEN",
        ),
    ]

    indic_liste = [
        colonne
        for colonne, code in indic_filtres
    ]

    # Création d'une colonne booléenne pour chaque indicateur
    for nom_indicateur, groupe_code in indic_filtres:

        df_res[nom_indicateur] = (
            df_res["FORMATION_CODE"]
            .isin(filtres_formation_grand_public[groupe_code])
        )

    # ========================================================
    # Exclusion des personnes comptées à la fois en GQS et PSC
    # ========================================================

    mask_gqs = df_res[
        f"Formation_grand_public Nb_formes_GQS_{year}"
    ]

    mask_psc = df_res[
        f"Formation_grand_public Nb_formes_PSC_{year}"
    ]

    nivols_psc = df_res.loc[
        mask_psc,
        "NIVOL_ID_FK",
    ]

    # Une personne PSC n'est pas également comptée en GQS
    df_res.loc[
        mask_gqs
        & df_res["NIVOL_ID_FK"].isin(nivols_psc),
        f"Formation_grand_public Nb_formes_GQS_{year}",
    ] = False


    # ========================================================
    # Exclusion des personnes comptées à la fois en IPS et PSC
    # ========================================================

    mask_ips = df_res[
        f"Formation_grand_public Nb_formes_IPS_{year}"
    ]

    mask_psc = df_res[
        f"Formation_grand_public Nb_formes_PSC_{year}"
    ]

    nivols_psc = df_res.loc[
        mask_psc,
        "NIVOL_ID_FK",
    ]

    # Une personne IPS n'est pas également comptée en GQS
    df_res.loc[
        mask_ips
        & df_res["NIVOL_ID_FK"].isin(nivols_psc),
        f"Formation_grand_public Nb_formes_IPS_{year}",
    ] = False


    # ========================================================
    # Comptage des NIVOL distincts
    # ========================================================

    def count_unique(group, col_name):

        return group.loc[
            group[col_name],
            "NIVOL_ID_FK",
        ].nunique()

    result = (
        df_res
        .groupby(col_groupby)
        .apply(
            lambda groupe: pd.Series({
                colonne: count_unique(
                    groupe,
                    colonne,
                )
                for colonne in indic_liste
            })
        )
        .reset_index()
    )

    return result


# ============================================================
# 5. CALCUL PAR STRUCTURE ET PAR DT
# ============================================================

def calcul_indicateurs_formation_grand_public(
    client,
    df_ref_structure,
    target_date="2026-05-31",
):
    """
    Retourne :
    - les quatre indicateurs par structure organisatrice ;
    - les quatre indicateurs par DT de rattachement.
    """

    # Import et préparation de la base
    df_formation_session_resultat_fpg = (
        clean_formations_grand_public(
            client=client,
            df_ref_structure=df_ref_structure,
        )
    )

    # Calcul par structure
    indicateurs_fgp_structure = nb_suivi_form_tous(
        df=df_formation_session_resultat_fpg,
        filtres_formation_grand_public=filtres_formation_grand_public,
        col_groupby="n_structure",
        target_date=target_date,
    )

    # Calcul par DT
    indicateurs_fgp_DT = nb_suivi_form_tous(
        df=df_formation_session_resultat_fpg,
        filtres_formation_grand_public=filtres_formation_grand_public,
        col_groupby="DT_de_rattachement",
        target_date=target_date,
    )

    # Suppression des DT manquantes ou vides
    indicateurs_fgp_DT = indicateurs_fgp_DT[
        indicateurs_fgp_DT["DT_de_rattachement"].notna()
        & indicateurs_fgp_DT["DT_de_rattachement"].astype(str).str.strip().ne("")
    ].copy()


    return (
        indicateurs_fgp_structure,
        indicateurs_fgp_DT,
    )




# ============================================================
# II. COMPTER LES SESSIONS DE FORMATIONS
# ============================================================



# ============================================================
# 1. CODES UTILISÉS
# ============================================================

filtres_bc_formation = {
    'PSE1': [
        'APTE PSE1',
        'PSE1',
        'RECPSE1',
        'RATPSE1',
        'FCPSE1'
    ],

    'PSE2': [
        'RECPSE2',
        'PSE2',
        'RECPSE2',
        'PSE',
        'RATPSE2',
        'FCPSE2',
        'FCPSE',
        'PSE AGSU'
    ],

    'CI': [
        'CI P1 P2',
        'CI',
        'CIP2',
        'RECCI',
        'REC PSECI',
        'RECPSECI',
        'FCCI'
    ],

    'FPSE': [
        'RECFPS',
        'FPS',
        'FPSE',
        'FCFPSE',
        'RATFCFPSE',
        'PICF FPS',
        'PICF FPSE',
        'FPSE AFGU'
    ],

    'PSC': [
        "PSC1 IRR",
        "EPSC1",
        "RECPSC1",
        "PSC1",
        "PSC1 AC",
        'PSC',
        'PSC IRR',
        'EPSC',
        'PSC AC',
        'FCPSC'
    ],

    'GQS': [
        'GQS',
        'GQS AC',
        'FIPS',
        'FIPS2'
    ],

    'IPSEN': [
        'IPSEN'
    ],

    'IPS': [
        'IPS',
        'IPS SR',
        'IPSE',
        'IPSEF',
        'IPSJ',
        'IPSJP',
        'IPSM',
        'IPSP',
        'IPS AC'
    ],

    'PSE': [
        'APTE PSE1',
        'PSE1',
        'RECPSE1',
        'RATPSE1',
        'FCPSE1',
        'RECPSE2',
        'PSE2',
        'RECPSE2',
        'PSE',
        'FCPSE',
        'RATPSE2',
        'FCPSE2', 
        'PSE AGSU'
    ],
}
        

# ============================================================
# 3. PRÉPARATION DU DATAFRAME UTILISÉ POUR LES SESSIONS
# ============================================================

def clean_base_contact_formation_gd_public(
    client,
    df_ref_structure,
    target_date="2025-12-31"
):

    target = pd.Timestamp(target_date)
    year = target.year

    bdd_year = year

    if year < 2025:
        bdd_year = 2025

    codes_filtres_bc_formation = list({
        element
        for sous_liste in filtres_bc_formation.values()
        for element in sous_liste
    })

    TARGET_YEAR = pd.to_datetime(target_date).year

    query_formation_session_resultat = f"""
        SELECT *
        FROM `crf-pat.dataset_PAT_2026.crf_pat_2026_formation_session_resultat`
    """

    df_formation_session_resultat = (
        client
        .query(query_formation_session_resultat)
        .to_dataframe()
    )

    df_formation_session_resultat[
        'FORMATION_DATE_OBTENTION'
    ] = pd.to_datetime(
        df_formation_session_resultat[
            'FORMATION_DATE_OBTENTION'
        ],
        errors='coerce'
    )

    df_formation_session_resultat[
        'FORMATION_DATE_RECYCLAGE'
    ] = pd.to_datetime(
        df_formation_session_resultat[
            'FORMATION_DATE_RECYCLAGE'
        ],
        errors='coerce'
    )

    df_formation_session_resultat = (
        df_formation_session_resultat[
            df_formation_session_resultat[
                "FORMATION_CODE"
            ].isin(codes_filtres_bc_formation)
        ]
    )

    # --------------------------------------------------------
    # DataFrame spécialement utilisé pour compter les sessions
    # --------------------------------------------------------

    df_formation_count_session = (
        df_formation_session_resultat.copy()
    )

    df_formation_count_session = (
        df_formation_count_session.rename(
            columns={
                "FORMATION_SESSION_STRUCTURE_ID_FK":
                    "n_structure"
            }
        )
    )

    df_formation_count_session = (
        apply_rattachement_successif(
            df_ref_structure,
            df_formation_count_session,
            col='n_structure'
        )
    )

    df_formation_count_session = dt_rattachement(
        df_formation_count_session,
        df_ref_structure
    )

    # Conservation uniquement des sessions de l'année cible
    df_formation_count_session_year = (
        df_formation_count_session[
            df_formation_count_session[
                'FORMATION_DATE_OBTENTION'
            ].dt.year == TARGET_YEAR
        ]
        .copy()
    )

    # Conservation uniquement des structures du référentiel
    liste_structure_garder = (
        df_ref_structure[
            'n_structure'
        ]
        .drop_duplicates()
        .tolist()
    )

    df_formation_count_session_year = (
        df_formation_count_session_year[
            df_formation_count_session_year[
                'n_structure'
            ].isin(liste_structure_garder)
        ]
    )

    return df_formation_count_session_year


# ============================================================
# 4. CALCUL DES NOMBRES DE SESSIONS
# ============================================================

def nb_session_form(
    df_year,
    filtres_bc_formation,
    col_groupby,
    target_date
):
    """
    Nombre de sessions de formation.
    """

    df_res = df_year.copy()

    target = pd.Timestamp(target_date)
    year = target.year

    # Sessions dont la date est antérieure ou égale
    # à la date cible
    df_res = df_res[
        df_res['FORMATION_DATE_OBTENTION'] <= target
    ].copy()

    indic_filtres = [
        (
            f'Formation_grand_public Nb_sessions_PSC_{year}',
            'PSC'
        ),
        (
            f'Formation_grand_public Nb_sessions_GQS_{year}',
            'GQS'
        ),
        (
            f'Formation_grand_public Nb_sessions_IPS_{year}',
            'IPS'
        ),
        (
            f'Formation_grand_public Nb_sessions_IPSEN_{year}',
            'IPSEN'
        ),
        (
            f'Secours Nb_sessions_PSE',
            'PSE'
        ),
        (
            f'Secours Nb_sessions_CI',
            'CI'
        ),
        (
            f'Secours Nb_sessions_FPSE',
            'FPSE'
        )
    ]

    indic_liste = [
        col
        for col, _ in indic_filtres
    ]

    # Création d'une colonne booléenne par indicateur
    for name, code in indic_filtres:

        df_res[name] = (
            df_res['FORMATION_CODE']
            .isin(filtres_bc_formation[code])
        )

    # --------------------------------------------------------
    # Vérification des codes
    # --------------------------------------------------------

    print("\n===== Vérification des codes =====")

    codes_df = set(
        df_res['FORMATION_CODE'].unique()
    )

    for name, code in indic_filtres:

        codes_attendus = set(
            filtres_bc_formation.get(code, [])
        )

        codes_trouves = (
            codes_df
            .intersection(codes_attendus)
        )

        codes_manquants = (
            codes_attendus
            - codes_df
        )

        print(f"\nIndicateur : {name}")
        print(f"  Codes attendus : {codes_attendus}")
        print(f"  Codes trouvés  : {codes_trouves}")
        print(f"  Codes manquants: {codes_manquants}")

        df_res[name] = (
            df_res['FORMATION_CODE']
            .isin(codes_attendus)
        )

    # --------------------------------------------------------
    # Exclusion des sessions GQS également identifiées PSC
    # --------------------------------------------------------

    mask_gqs = df_res[
        f'Formation_grand_public Nb_sessions_GQS_{year}'
    ]

    mask_psc = df_res[
        f'Formation_grand_public Nb_sessions_PSC_{year}'
    ]

    sessions_psc = df_res.loc[
        mask_psc,
        'SESSION_ID_FK'
    ]

    df_res.loc[
        mask_gqs
        & df_res['SESSION_ID_FK'].isin(sessions_psc),
        f'Formation_grand_public Nb_sessions_GQS_{year}'
    ] = False


        # --------------------------------------------------------
    # Exclusion des sessions IPS également identifiées PSC
    # --------------------------------------------------------

    mask_ips = df_res[
        f'Formation_grand_public Nb_sessions_IPS_{year}'
    ]

    mask_psc = df_res[
        f'Formation_grand_public Nb_sessions_PSC_{year}'
    ]

    sessions_psc = df_res.loc[
        mask_psc,
        'SESSION_ID_FK'
    ]

    df_res.loc[
        mask_ips
        & df_res['SESSION_ID_FK'].isin(sessions_psc),
        f'Formation_grand_public Nb_sessions_IPS_{year}'
    ] = False

    # --------------------------------------------------------
    # Nombre de SESSION_ID_FK distincts
    # --------------------------------------------------------

    def count_unique(group, col_name):

        return group.loc[
            group[col_name],
            'SESSION_ID_FK'
        ].nunique()

    result = (
        df_res
        .groupby(col_groupby)
        .apply(
            lambda g: pd.Series({
                col: count_unique(g, col)
                for col in indic_liste
            })
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Totaux de contrôle
    # --------------------------------------------------------

    print("\n===== Somme globale par indicateur =====")

    totaux = result[
        [
            col
            for col, _ in indic_filtres
        ]
    ].sum()

    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

    return result


# ============================================================
# 5. APPEL DU CALCUL PAR STRUCTURE ET PAR DT
# ============================================================

def calcul_indicateurs_sessions(
    client,
    df_ref_structure,
    target_date="2026-05-31"
):

    df_formation_count_session_year = (
        clean_base_contact_formation_gd_public(
            client,
            df_ref_structure,
            target_date
        )
    )

    # Calcul par structure organisatrice
    nb_sessions = nb_session_form(
        df_formation_count_session_year,
        filtres_bc_formation,
        'n_structure',
        target_date
    )

    # Calcul par DT de rattachement
    nb_sessions_DT = nb_session_form(
        df_formation_count_session_year,
        filtres_bc_formation,
        'DT_de_rattachement',
        target_date
    )


    nb_sessions_DT = nb_sessions_DT[
        nb_sessions_DT["DT_de_rattachement"].notna()
        & nb_sessions_DT["DT_de_rattachement"].astype(str).str.strip().ne("")
    ].copy()



    return nb_sessions, nb_sessions_DT




