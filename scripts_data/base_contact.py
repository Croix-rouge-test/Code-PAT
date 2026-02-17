import pandas as pd
import numpy as np
import re

def keep_integer(x):
    if x is None:
        return None
    return re.sub(r'\D', '', str(x))

def dt_rattachement(df, df_ref_structure):
    """
    Associer les structures avec la DT de rattachement.
    """
    df = df.rename(columns={"FORMATION_SESSION_STRUCTURE_ID_FK": "n_structure"})
    df_return = df.merge(
        df_ref_structure[['n_structure', 'DT_de_rattachement']].drop_duplicates(),
        on='n_structure',
        how='left'
    )
    df_return['DT_de_rattachement'] = df_return['DT_de_rattachement'].apply(lambda x: keep_integer(x))
    return df_return

def flatten(xss):
    return [x for xs in xss for x in xs]

# ------------------------------
# Fonctions indicateurs
# ------------------------------

def nb_suivi_form(df_filtered, filtres_bc, col_groupby):
    df_res = df_filtered[df_filtered['FORMATION_BENEVOLE_DANS_L_ANNEE'] == 'Oui'].copy()

    # Ajouter colonnes booléennes par filtre
    for name, code in [('Maraude Nb_SOLIDAR', 'solidar'),
                       ('Maraude Nb_SOLIDAR2020', 'solidar20'),
                       ('AEO Nb_AAD', 'AAD'),
                       ('AEO Nb_FAAD', 'FAAD'),
                       ('Dispositifs_d_urgence Nb_formes_TCAU_2025', 'TCAU'),
                       ('Dispositifs_d_urgence Nb_formes_TCEO_2025', 'TCEO'),
                       ('Dispositifs_d_urgence Nb_formes_IPSP_2025', 'IPSP'),
                       ('Dispositifs_d_urgence Nb_formes_IRR_2025', 'IRR'),
                       ('Dispositifs_d_urgence Nb_formes_GQS_2025', 'GQS')]:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

    # Groupby et count distinct
    def count_unique(group, col_name):
        return group.loc[group[col_name], 'NIVOL_ID_FK'].nunique()

    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({col: count_unique(g, col) for col in ['Maraude Nb_SOLIDAR', 'Maraude Nb_SOLIDAR2020',
                                                                  'AEO Nb_AAD', 'AEO Nb_FAAD',
                                                                  'Dispositifs_d_urgence Nb_formes_TCAU_2025',
                                                                  'Dispositifs_d_urgence Nb_formes_TCEO_2025',
                                                                  'Dispositifs_d_urgence Nb_formes_IPSP_2025',
                                                                  'Dispositifs_d_urgence Nb_formes_IRR_2025',
                                                                  'Dispositifs_d_urgence Nb_formes_GQS_2025']})
    ).reset_index()
    return result

def nb_suivi_form_tous(df_2025, filtres_bc, col_groupby):
    df_res = df_2025.copy()
    for name, code in [('Formation_grand_public Nb_formes_PSC_2025', 'PSC'),
                       ('Formation_grand_public Nb_formes_GQS_2025', 'GQS'),
                       ('Formation_grand_public Nb_formes_IPS_2025', 'IPS'),
                       ('Formation_grand_public Nb_formes_IPSEN_2025', 'IPSEN'),
                       ('Formation_grand_public Nb_formes_PREVIC_2025', 'PREVIC'),
                       ('Structure Nb_formes_CRB_2025', 'CRB'),
                       ('Structure Nb_formateurs_CRB_2025', 'ACRB'),
                       ('Structure Nb_formes_TCAS_2025', 'TCAS')]:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

    def count_unique(group, col_name):
        return group.loc[group[col_name], 'NIVOL_ID_FK'].nunique()

    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({col: count_unique(g, col) for col in ['Formation_grand_public Nb_formes_PSC_2025',
                                                                  'Formation_grand_public Nb_formes_GQS_2025',
                                                                  'Formation_grand_public Nb_formes_IPS_2025',
                                                                  'Formation_grand_public Nb_formes_IPSEN_2025',
                                                                  'Formation_grand_public Nb_formes_PREVIC_2025'
                                                                  'Structure Nb_formes_CRB_2025',
                                                                  'Structure Nb_formateurs_CRB_2025',
                                                                  'Structure Nb_formes_TCAS_2025']})
    ).reset_index()
    return result

def nb_session_form(df_2025, filtres_bc, col_groupby):
    df_res = df_2025[df_2025['FORMATION_BENEVOLE_DANS_L_ANNEE'] == 'Oui'].copy()
    for name, code in [('Formation_grand_public Nb_sessions_PSC_2025', 'PSC'),
                       ('Formation_grand-public Nb_sessions_GQS_2025', 'GQS'),
                       ('Formation_grand-public Nb_sessions_IPS_2025', 'IPS'),
                       ('Formation_grand-public Nb_sessions_IPSEN_2025', 'IPSEN'),
                       ('Formation_grand-public Nb_sessions_PREVIC_2025', 'PREVIC')]:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

    def count_unique(group, col_name):
        return group.loc[group[col_name], 'SESSION_ID_FK'].nunique()

    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({col: count_unique(g, col) for col in ['Formation_grand_public Nb_sessions_PSC_2025',
                                                                  'Formation_grand-public Nb_sessions_GQS_2025',
                                                                  'Formation_grand-public Nb_sessions_IPS_2025',
                                                                  'Formation_grand-public Nb_sessions_IPSEN_2025',
                                                                  'Formation_grand-public Nb_sessions_PREVIC_2025']})
    ).reset_index()
    return result

def nb_bene_aptes(df_2025, filtres_bc, col_groupby):
    df_res = df_2025[(df_2025['FORMATION_RESULTAT'] == 'Apte') &
                     (df_2025['FORMATION_BENEVOLE_DANS_L_ANNEE'] == 'Oui')].copy()
    for name, code in [('Formation_grand_public Nb_FPSC', 'FPSC'),
                       ('Formation_grand_public Nb_AGQS', 'AGQS'),
                       ('Formation_grand_public Nb_FIPSEN', 'FIPSEN'),
                       ('Secours Nb_PSE1', 'PSE1'),
                       ('Secours Nb_PSE2', 'PSE2'),
                       ('Secours Nb_CI', 'CI')]:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

    def count_unique(group, col_name):
        return group.loc[group[col_name], 'NIVOL_ID_FK'].nunique()

    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({col: count_unique(g, col) for col in ['Formation_grand_public Nb_FPSC',
                                                                  'Formation_grand_public Nb_AGQS',
                                                                  'Formation_grand_public Nb_FIPSEN',
                                                                  'Secours Nb_PSE1',
                                                                  'Secours Nb_PSE2',
                                                                  'Secours Nb_CI']})
    ).reset_index()
    return result

# ------------------------------
# Fonctions taux
# ------------------------------

def taux_recy(df_2025, filtres_bc, col_groupby):
    df_res = df_2025.copy()
    result = pd.DataFrame({col_groupby: df_res[col_groupby].unique()})
    result.set_index(col_groupby, inplace=True)

    for code, alias in [('PSE1', 'Secours Taux_recy26_PSE1'),
                        ('PSE2', 'Secours Taux_recy26_PSE2'),
                        ('CI', 'Secours Taux_recy26_CI')]:
        taux = df_res.groupby(col_groupby).apply(
            lambda g: ((g[g['FORMATION_CODE'].isin(filtres_bc[code])]
                        ['FORMATION_DATE_RECYCLAGE'].dt.year == 2025).sum()
                       / max(1, g[g['FORMATION_CODE'].isin(filtres_bc[code])].shape[0]))
        )
        result[alias] = taux

    result = result.reset_index()
    return result

def taux_ren(df_filtered, filtres_bc, col_groupby):
    df_2025 = df_filtered[df_filtered['FORMATION_DATE_OBTENTION'].dt.year == 2025].copy()
    df_autres = df_filtered[df_filtered['FORMATION_DATE_OBTENTION'].dt.year == 2024].copy()

    result = pd.DataFrame({col_groupby: df_2025[col_groupby].unique()})
    result.set_index(col_groupby, inplace=True)

    for code, alias in [('PSE1', 'Secours Taux_ren25_PSE1'),
                        ('PSE2', 'Secours Taux_ren25_PSE2'),
                        ('CI', 'Secours Taux_ren25_CI')]:
        def compute_taux(g):
            nivol_2025 = g[g['FORMATION_CODE'].isin(filtres_bc[code])]['NIVOL_ID_FK'].unique()
            nivol_autres = df_autres['NIVOL_ID_FK'].unique()
            nivol_absents = np.setdiff1d(nivol_2025, nivol_autres)
            return len(nivol_absents) / max(1, len(nivol_2025))
        taux = df_2025.groupby(col_groupby).apply(compute_taux)
        result[alias] = taux

    result = result.reset_index()
    return result

# ------------------------------
# Fusion
# ------------------------------

def fusion_bc_final(nb_suivi_formation, nb_suivi_formation_DT,
                    nb_suivi_formation_tous, nb_suivi_formation_tous_DT,
                    nb_sessions, nb_sessions_DT,
                    nb_apte_formation, nb_apte_formation_DT,
                    taux_rec, taux_rec_DT,
                    taux_nouveau_form, taux_nouveau_form_DT,
                    col_groupby):
    # Fusion des DataFrames
    def merge_all(dfs):
        from functools import reduce
        return reduce(lambda left, right: left.merge(right, on=col_groupby, how='left'), dfs)

    indicateurs_base_contact = merge_all([nb_suivi_formation,
                                         nb_suivi_formation_tous,
                                         nb_sessions,
                                         nb_apte_formation,
                                         taux_rec,
                                         taux_nouveau_form])

    # Même pour DT
    for df in [nb_suivi_formation_DT, nb_suivi_formation_tous_DT, nb_sessions_DT,
               nb_apte_formation_DT, taux_rec_DT, taux_nouveau_form_DT]:
        df.rename(columns={'DT_de_rattachement':'n_structure'}, inplace=True)

    indicateurs_base_contact_DT = merge_all([nb_suivi_formation_DT,
                                            nb_suivi_formation_tous_DT,
                                            nb_sessions_DT,
                                            nb_apte_formation_DT,
                                            taux_rec_DT,
                                            taux_nouveau_form_DT])

    return indicateurs_base_contact, indicateurs_base_contact_DT

# ------------------------------
# Fonction principale
# ------------------------------

def clean_base_contact(client):
    query_formation_session_resultat = """
    SELECT * FROM `crf-pat.dataset_PAT_2025.crf_pat_2025_formation_session_resultat`
    """
    df_formation_session_resultat = client.query(query_formation_session_resultat).to_dataframe()
    df_formation_session_resultat['FORMATION_DATE_OBTENTION'] = pd.to_datetime(df_formation_session_resultat['FORMATION_DATE_OBTENTION'], errors='coerce')
    df_formation_session_resultat['FORMATION_DATE_RECYCLAGE'] = pd.to_datetime(df_formation_session_resultat['FORMATION_DATE_RECYCLAGE'], errors='coerce')
    df_formation_session_resultat = df_formation_session_resultat[df_formation_session_resultat['FORMATION_SESSION_STRUCTURE_ID_FK'] != 1]
    return df_formation_session_resultat

def indicateurs_base_contact(df_formation_session_resultat, df_ref_structure):
    # Définition filtres
    filtres_bc = {
        'CRB' : ['CRB', 'eCRB', 'VI'],
        'ACRB' : ['AVI','ACRB2','ACRB3','ACRB2024'],
        'TCAS' : ['TCAS','TCAS2', 'ETCAS'],
        'TCAU' : ['TCAU', 'ETCAU'],
        'TCEO' : ['TCEO'],
        'IPSP' : ['PSP','PSP1'],
        'IRR' : ['IRR','IRRA','IRRJ'],
        'solidar' : ['SOLIDAR2','SOLIDAR1','SOLIDAR'],
        'solidar20' : ['PASSSOLIDAR2020','PASSOLIDAR2020','ESOLIDAR2026','SOLIDAR2020'],
        'AAD' : ['AAD','IAD','MAO'],
        'FAAD' : ['FAAD','FAAAD','EPIAF FAAD'],
        'FPSC' : ['RECFFPSC','RATFCFFPSC','FCFPSC','RATFCFPSC'],
        'AGQS' : ['AGQS','RATAGQS'],
        'FIPSEN' : ['FIPSEN','RECFIPSEN'],
        'PSE1' : ['APTE PSE1', 'PSE1','RECPSE1'],
        'PSE2' : ['RECPSE2','PSE2','RECPSE2'],
        'CI' : ['CI P1 P2', 'CI', 'CIP1' ,'CIP2' ,'CIP3', 'CI EXT','RECCI', 'REC PSECI' ,'RECPSECI'],
        'PSC' : ["PSC1 IRR","EPSC1","RECPSC1","PSC1","PSC1 AC"],
        'GQS' : ['GQS'],
        'IPSEN' : ['IPSEN'],
        'IPS' : ['IPS', 'IPS SR', 'ISPE', 'IPSEF', 'IPSJ', 'IPSJP', 'IPSM', 'IPSP', 'IPS AC'],
        'PREVIC' : ['PREVIC']
    }


    # Ajouter DT
    df_filtered = df_formation_session_resultat.copy()
    df_filtered = df_filtered[df_filtered['FORMATION_CODE'].isin(flatten(list(filtres_bc.values())))]
    df_filtered = dt_rattachement(df_filtered, df_ref_structure)

    df_filtered_2025 = df_filtered[df_filtered['FORMATION_DATE_OBTENTION'].dt.year == 2025].copy()

    # Calculs indicateurs
    nb_suivi_formation = nb_suivi_form(df_filtered, filtres_bc, 'n_structure')
    nb_suivi_formation_DT = nb_suivi_form(df_filtered, filtres_bc, 'DT_de_rattachement')

    nb_suivi_formation_tous = nb_suivi_form_tous(df_filtered_2025, filtres_bc, 'n_structure')
    nb_suivi_formation_tous_DT = nb_suivi_form_tous(df_filtered_2025, filtres_bc, 'DT_de_rattachement')

    nb_sessions = nb_session_form(df_filtered_2025, filtres_bc, 'n_structure')
    nb_sessions_DT = nb_session_form(df_filtered_2025, filtres_bc, 'DT_de_rattachement')

    nb_apte_formation = nb_bene_aptes(df_filtered_2025, filtres_bc, 'n_structure')
    nb_apte_formation_DT = nb_bene_aptes(df_filtered_2025, filtres_bc, 'DT_de_rattachement')

    taux_rec = taux_recy(df_filtered_2025, filtres_bc, 'n_structure')
    taux_rec_DT = taux_recy(df_filtered_2025, filtres_bc, 'DT_de_rattachement')

    taux_nouveau_form = taux_ren(df_filtered, filtres_bc, 'n_structure')
    taux_nouveau_form_DT = taux_ren(df_filtered, filtres_bc, 'DT_de_rattachement')

    indicateurs_base_contact_pd, indicateurs_base_contact_DT_pd = fusion_bc_final(
        nb_suivi_formation, nb_suivi_formation_DT,
        nb_suivi_formation_tous, nb_suivi_formation_tous_DT,
        nb_sessions, nb_sessions_DT,
        nb_apte_formation, nb_apte_formation_DT,
        taux_rec, taux_rec_DT,
        taux_nouveau_form, taux_nouveau_form_DT,
        'n_structure'
    )

    return indicateurs_base_contact_pd, indicateurs_base_contact_DT_pd
