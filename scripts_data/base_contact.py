import pandas as pd
import numpy as np
import re
import sys
import os
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *

def keep_integer(x):
    if x is None:
        return None
    return re.sub(r'\D', '', str(x))

def dt_rattachement(df, df_ref_structure):
    """
    Associer les structures avec la DT de rattachement.
    """
    #df = df.rename(columns={"FORMATION_SESSION_STRUCTURE_ID_FK": "n_structure"}) =>Enlever car traité plus bas 
    #df = df.rename(columns={"rattachement_benevole_structure_id_fk": "n_structure"}) =>Enlever car traité plus bas 
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
                       ('Dispositifs_d_urgence Nb_formes_PSP_2025', 'PSP'),
                       ('Dispositifs_d_urgence Nb_formes_IRR_2025', 'IRR'),
                       ('Dispositifs_d_urgence Nb_formes_GQS_2025', 'GQS')]:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

    # Vérification des codes
    print("\n===== Vérification des codes =====")
    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in [('Maraude Nb_SOLIDAR', 'solidar'),
                       ('Maraude Nb_SOLIDAR2020', 'solidar20'),
                       ('AEO Nb_AAD', 'AAD'),
                       ('AEO Nb_FAAD', 'FAAD'),
                       ('Dispositifs_d_urgence Nb_formes_TCAU_2025', 'TCAU'),
                       ('Dispositifs_d_urgence Nb_formes_TCEO_2025', 'TCEO'),
                       ('Dispositifs_d_urgence Nb_formes_PSP_2025', 'PSP'),
                       ('Dispositifs_d_urgence Nb_formes_IRR_2025', 'IRR'),
                       ('Dispositifs_d_urgence Nb_formes_GQS_2025', 'GQS')]:
        codes_attendus = set(filtres_bc.get(code, []))
        codes_trouves = codes_df.intersection(codes_attendus)
        codes_manquants = codes_attendus - codes_df

        print(f"\nIndicateur : {name}")
        print(f"  Codes attendus : {codes_attendus}")
        print(f"  Codes trouvés  : {codes_trouves}")
        print(f"  Codes manquants: {codes_manquants}")

        df_res[name] = df_res['FORMATION_CODE'].isin(codes_attendus)


    # Groupby et count distinct
    def count_unique(group, col_name):
        return group.loc[group[col_name], 'NIVOL_ID_FK'].nunique()

    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({col: count_unique(g, col) for col in ['Maraude Nb_SOLIDAR', 'Maraude Nb_SOLIDAR2020',
                                                                  'AEO Nb_AAD', 'AEO Nb_FAAD',
                                                                  'Dispositifs_d_urgence Nb_formes_TCAU_2025',
                                                                  'Dispositifs_d_urgence Nb_formes_TCEO_2025',
                                                                  'Dispositifs_d_urgence Nb_formes_PSP_2025',
                                                                  'Dispositifs_d_urgence Nb_formes_IRR_2025',
                                                                  'Dispositifs_d_urgence Nb_formes_GQS_2025']})
    ).reset_index()

    # Somme globale par indicateur
    print("\n===== Somme globale par indicateur =====")
    totaux = result[[col for col, _ in [('Maraude Nb_SOLIDAR', 'solidar'),
                       ('Maraude Nb_SOLIDAR2020', 'solidar20'),
                       ('AEO Nb_AAD', 'AAD'),
                       ('AEO Nb_FAAD', 'FAAD'),
                       ('Dispositifs_d_urgence Nb_formes_TCAU_2025', 'TCAU'),
                       ('Dispositifs_d_urgence Nb_formes_TCEO_2025', 'TCEO'),
                       ('Dispositifs_d_urgence Nb_formes_PSP_2025', 'PSP'),
                       ('Dispositifs_d_urgence Nb_formes_IRR_2025', 'IRR'),
                       ('Dispositifs_d_urgence Nb_formes_GQS_2025', 'GQS')]]].sum()
    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

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

    # Vérification des codes
    print("\n===== Vérification des codes =====")
    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in [('Formation_grand_public Nb_formes_PSC_2025', 'PSC'),
                       ('Formation_grand_public Nb_formes_GQS_2025', 'GQS'),
                       ('Formation_grand_public Nb_formes_IPS_2025', 'IPS'),
                       ('Formation_grand_public Nb_formes_IPSEN_2025', 'IPSEN'),
                       ('Formation_grand_public Nb_formes_PREVIC_2025', 'PREVIC'),
                       ('Structure Nb_formes_CRB_2025', 'CRB'),
                       ('Structure Nb_formateurs_CRB_2025', 'ACRB'),
                       ('Structure Nb_formes_TCAS_2025', 'TCAS')]:
        codes_attendus = set(filtres_bc.get(code, []))
        codes_trouves = codes_df.intersection(codes_attendus)
        codes_manquants = codes_attendus - codes_df

        print(f"\nIndicateur : {name}")
        print(f"  Codes attendus : {codes_attendus}")
        print(f"  Codes trouvés  : {codes_trouves}")
        print(f"  Codes manquants: {codes_manquants}")

        df_res[name] = df_res['FORMATION_CODE'].isin(codes_attendus)

    def count_unique(group, col_name):
        return group.loc[group[col_name], 'NIVOL_ID_FK'].nunique()

    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({col: count_unique(g, col) for col in ['Formation_grand_public Nb_formes_PSC_2025',
                                                                  'Formation_grand_public Nb_formes_GQS_2025',
                                                                  'Formation_grand_public Nb_formes_IPS_2025',
                                                                  'Formation_grand_public Nb_formes_IPSEN_2025',
                                                                  'Formation_grand_public Nb_formes_PREVIC_2025',
                                                                  'Structure Nb_formes_CRB_2025',
                                                                  'Structure Nb_formateurs_CRB_2025',
                                                                  'Structure Nb_formes_TCAS_2025']})
    ).reset_index()

    # Somme globale par indicateur
    print("\n===== Somme globale par indicateur =====")
    totaux = result[[col for col, _ in [('Formation_grand_public Nb_formes_PSC_2025', 'PSC'),
                       ('Formation_grand_public Nb_formes_GQS_2025', 'GQS'),
                       ('Formation_grand_public Nb_formes_IPS_2025', 'IPS'),
                       ('Formation_grand_public Nb_formes_IPSEN_2025', 'IPSEN'),
                       ('Formation_grand_public Nb_formes_PREVIC_2025', 'PREVIC'),
                       ('Structure Nb_formes_CRB_2025', 'CRB'),
                       ('Structure Nb_formateurs_CRB_2025', 'ACRB'),
                       ('Structure Nb_formes_TCAS_2025', 'TCAS')]]].sum()
    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

    return result




def nb_session_form(df_2025, filtres_bc, col_groupby):
    #df_res = df_2025[df_2025['FORMATION_BENEVOLE_DANS_L_ANNEE'] == 'Oui'].copy()
    df_res = df_2025.copy()
    for name, code in [('Formation_grand_public Nb_sessions_PSC_2025', 'PSC'),
                       ('Formation_grand_public Nb_sessions_GQS_2025', 'GQS'),
                       ('Formation_grand_public Nb_sessions_IPS_2025', 'IPS'),
                       ('Formation_grand_public Nb_sessions_IPSEN_2025', 'IPSEN'),
                       ('Formation_grand_public Nb_sessions_PREVIC_2025', 'PREVIC'),
                       ('Formation_grand_public Nb_sessions_PSE', 'PSE'),
                       ('Formation_grand_public Nb_sessions_CI', 'CI'),
                       ('Formation_grand_public Nb_sessions_FPSE', 'FPS')]:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

        # Vérification des codes
    print("\n===== Vérification des codes =====")
    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in [('Formation_grand_public Nb_sessions_PSC_2025', 'PSC'),
                       ('Formation_grand_public Nb_sessions_GQS_2025', 'GQS'),
                       ('Formation_grand_public Nb_sessions_IPS_2025', 'IPS'),
                       ('Formation_grand_public Nb_sessions_IPSEN_2025', 'IPSEN'),
                       ('Formation_grand_public Nb_sessions_PREVIC_2025', 'PREVIC'),
                       ('Formation_grand_public Nb_sessions_PSE', 'PSE'),
                       ('Formation_grand_public Nb_sessions_CI', 'CI'),
                       ('Formation_grand_public Nb_sessions_FPSE', 'FPS')]:
        codes_attendus = set(filtres_bc.get(code, []))
        codes_trouves = codes_df.intersection(codes_attendus)
        codes_manquants = codes_attendus - codes_df

        print(f"\nIndicateur : {name}")
        print(f"  Codes attendus : {codes_attendus}")
        print(f"  Codes trouvés  : {codes_trouves}")
        print(f"  Codes manquants: {codes_manquants}")

        df_res[name] = df_res['FORMATION_CODE'].isin(codes_attendus)

    def count_unique(group, col_name):
        return group.loc[group[col_name], 'SESSION_ID_FK'].nunique()

    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({col: count_unique(g, col) for col in ['Formation_grand_public Nb_sessions_PSC_2025',
                                                                  'Formation_grand_public Nb_sessions_GQS_2025',
                                                                  'Formation_grand_public Nb_sessions_IPS_2025',
                                                                  'Formation_grand_public Nb_sessions_IPSEN_2025',
                                                                  'Formation_grand_public Nb_sessions_PREVIC_2025',
                                                                  'Formation_grand_public Nb_sessions_PSE',
                                                                  'Formation_grand_public Nb_sessions_CI',
                                                                  'Formation_grand_public Nb_sessions_FPSE']})
    ).reset_index()

    # Somme globale par indicateur
    print("\n===== Somme globale par indicateur =====")
    totaux = result[[col for col, _ in [('Formation_grand_public Nb_sessions_PSC_2025', 'PSC'),
                       ('Formation_grand_public Nb_sessions_GQS_2025', 'GQS'),
                       ('Formation_grand_public Nb_sessions_IPS_2025', 'IPS'),
                       ('Formation_grand_public Nb_sessions_IPSEN_2025', 'IPSEN'),
                       ('Formation_grand_public Nb_sessions_PREVIC_2025', 'PREVIC'),
                       ('Formation_grand_public Nb_sessions_PSE', 'PSE'),
                       ('Formation_grand_public Nb_sessions_CI', 'CI'),
                       ('Formation_grand_public Nb_sessions_FPSE', 'FPS')]]].sum()
    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

    return result




def nb_bene_aptes(df_2025, filtres_bc, col_groupby):
    df_res = df_2025[(df_2025['FORMATION_RESULTAT'] == 'Apte') &
                     (df_2025['FORMATION_BENEVOLE_DANS_L_ANNEE'] == 'Oui')].copy()

    for name, code in [('Formation_grand_public Nb_FPSC', 'FPSC'),
                       ('Formation_grand_public Nb_AGQS', 'AGQS'),
                       ('Formation_grand_public Nb_FIPSEN', 'FIPSEN')]:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

        # PARTIE SECOURS (corrigée hiérarchie)
    # Attribution d’un niveau hiérarchique
    def get_level(code):
        if code in filtres_bc['CI']:
            return 3
        elif code in filtres_bc['PSE2']:
            return 2
        elif code in filtres_bc['PSE1']:
            return 1
        else:
            return 0

    df_res['SECOURS_LEVEL'] = df_res['FORMATION_CODE'].apply(get_level)

    # Niveau maximum par bénévole
    max_level = (
        df_res.groupby('NIVOL_ID_FK')['SECOURS_LEVEL']
        .max()
        .reset_index()
    )

    df_res = df_res.merge(max_level, on='NIVOL_ID_FK', suffixes=('', '_MAX'))

    # Colonnes exclusives
    df_res['Secours Nb_PSE1'] = df_res['SECOURS_LEVEL_MAX'] == 1
    df_res['Secours Nb_PSE2'] = df_res['SECOURS_LEVEL_MAX'] == 2
    df_res['Secours Nb_CI'] = df_res['SECOURS_LEVEL_MAX'] == 3


    # Vérification des codes
    print("\n===== Vérification des codes =====")
    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in [('Formation_grand_public Nb_FPSC', 'FPSC'),
                       ('Formation_grand_public Nb_AGQS', 'AGQS'),
                       ('Formation_grand_public Nb_FIPSEN', 'FIPSEN'),
                                        ('Secours Nb_PSE1', 'PSE1'),
                                        ('Secours Nb_PSE2', 'PSE2'),
                                        ('Secours Nb_CI', 'CI')]:
        codes_attendus = set(filtres_bc.get(code, []))
        codes_trouves = codes_df.intersection(codes_attendus)
        codes_manquants = codes_attendus - codes_df

        print(f"\nIndicateur : {name}")
        print(f"  Codes attendus : {codes_attendus}")
        print(f"  Codes trouvés  : {codes_trouves}")
        print(f"  Codes manquants: {codes_manquants}")

        df_res[name] = df_res['FORMATION_CODE'].isin(codes_attendus)

    # Fonction de comptage
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

    # Somme globale par indicateur
    print("\n===== Somme globale par indicateur =====")
    totaux = result[[col for col, _ in [('Formation_grand_public Nb_FPSC', 'FPSC'),
                       ('Formation_grand_public Nb_AGQS', 'AGQS'),
                       ('Formation_grand_public Nb_FIPSEN', 'FIPSEN'),
                                        ('Secours Nb_PSE1', 'PSE1'),
                                        ('Secours Nb_PSE2', 'PSE2'),
                                        ('Secours Nb_CI', 'CI')]]].sum()

    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

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
                    nb_actifs_solidar, nb_actifs_solidar_DT,
                    taux_is_actifs, taux_is_actifs_DT,
                    df_nvx_forme_crb, df_nvx_forme_crb_DT,
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
                                         taux_nouveau_form,
                                         nb_actifs_solidar,
                                         taux_is_actifs,
                                         df_nvx_forme_crb])

    # Même pour DT
    for df in [nb_suivi_formation_DT, nb_suivi_formation_tous_DT, nb_sessions_DT,
               nb_apte_formation_DT, taux_rec_DT, taux_nouveau_form_DT,nb_actifs_solidar_DT,taux_is_actifs_DT,df_nvx_forme_crb_DT]:
        df.rename(columns={'DT_de_rattachement':'n_structure'}, inplace=True)

    indicateurs_base_contact_DT = merge_all([nb_suivi_formation_DT,
                                            nb_suivi_formation_tous_DT,
                                            nb_sessions_DT,
                                            nb_apte_formation_DT,
                                            taux_rec_DT,
                                            taux_nouveau_form_DT,
                                            nb_actifs_solidar_DT,
                                            taux_is_actifs_DT,
                                            df_nvx_forme_crb_DT])

    return indicateurs_base_contact, indicateurs_base_contact_DT

# ------------------------------
# Indicateurs fusionnés
# ------------------------------

def nb_nvx_forme_crb(client, df, filtres_bc, col_groupby):

    query_nvx_bene = """SELECT DISTINCT
        rattachement_benevole_nivol_id_fk
        FROM crf-pat.dataset_PAT_2025.crf_pat_2025_rattachement_benevole
        WHERE rattachement_benevole_date_debut >= DATE('2025-01-01')
        AND rattachement_benevole_date_debut < DATE('2026-01-01')"""

    df_nvx_bene = client.query(query_nvx_bene).to_dataframe()
    df_nvx_bene = df_nvx_bene.rename(columns = {'rattachement_benevole_nivol_id_fk' : 'NIVOL_ID_FK'})['NIVOL_ID_FK'].drop_duplicates()

    df = pd.merge(df, df_nvx_bene, on = 'NIVOL_ID_FK', how = 'inner')


    df_res = df[(df['FORMATION_RESULTAT'] == 'Apte') & (df['FORMATION_BENEVOLE_DANS_L_ANNEE'] == 'Oui')].copy()
    for name, code in [('Structure Nb_nvx_formes_CRB_2025', 'CRB')]:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

    # Vérification des codes
    print("\n===== Vérification des codes =====")
    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in [('Structure Nb_nvx_formes_CRB_2025', 'CRB')]:
        codes_attendus = set(filtres_bc.get(code, []))
        codes_trouves = codes_df.intersection(codes_attendus)
        codes_manquants = codes_attendus - codes_df

        print(f"\nIndicateur : {name}")
        print(f"  Codes attendus : {codes_attendus}")
        print(f"  Codes trouvés  : {codes_trouves}")
        print(f"  Codes manquants: {codes_manquants}")

        df_res[name] = df_res['FORMATION_CODE'].isin(codes_attendus)

    def count_unique(group, col_name):
        return group.loc[group[col_name], 'NIVOL_ID_FK'].nunique()

    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({col: count_unique(g, col) for col in ['Structure Nb_nvx_formes_CRB_2025']})
    ).reset_index()

    # Somme globale par indicateur
    print("\n===== Somme globale par indicateur =====")
    totaux = result[[col for col, _ in [('Structure Nb_nvx_formes_CRB_2025', 'CRB')]]].sum()
    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

    return result

def taux_IS(client, df, filtres_bc, df_ref_structure, col_groupby):

    query_is = """WITH codes_actifs AS (
                            SELECT 10105 AS code UNION ALL
                            SELECT 10106 UNION ALL
                            SELECT 10108 UNION ALL
                            SELECT 10113 UNION ALL
                            SELECT 10114 UNION ALL
                            SELECT 10115 UNION ALL
                            SELECT 10116
                          )

                          SELECT
                              act.*,
                              insc.*
                          FROM `crf-pat.dataset_PAT_2025.crf_pat_2025_pegass_activite` AS act
                          INNER JOIN `crf-pat.dataset_PAT_2025.crf_pat_2025_pegass_activite_seance_inscription` AS insc
                              ON act.PEGASS_ACTIVITE_ID_PK = insc.PEGASS_ACTIVITE_ID_FK
                          WHERE act.ACTIVITE_BENEVOLE_ID_FK IN (SELECT code FROM codes_actifs) AND insc.PEGASS_ACTIVITE_SEANCE_INSCRIPTION_STATUT = 'Valide' """


    df_is = client.query(query_is).to_dataframe()
    df_is = df_is.rename(columns = {'PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK': 'n_structure','PEGASS_ACTIVITE_SEANCE_INSCRIPTION_NIVOL_ID_FK' : 'NIVOL_ID_FK'})[['n_structure','NIVOL_ID_FK']].drop_duplicates()

    df = pd.merge(df.drop(['n_structure'], axis = 1), df_is, on = 'NIVOL_ID_FK', how = 'inner')
    filtres_bc['IS'] = filtres_bc['PSE1'] + filtres_bc['PSE2'] + filtres_bc['CI']

    df_res = df[(df['FORMATION_RESULTAT'] == 'Apte') & (df['FORMATION_BENEVOLE_DANS_L_ANNEE'] == 'Oui')].copy()
    _ , _ , _, df_res = apply_rattachement_successif(df_ref_structure, df_res, col = 'n_structure')
    _ , _ , _, df_is = apply_rattachement_successif(df_ref_structure, df_is, col = 'n_structure')

    df_res = dt_rattachement(df_res, df_ref_structure)
    df_is = dt_rattachement(df_is, df_ref_structure)
    

    df_res = df_res.drop_duplicates([col_groupby,'NIVOL_ID_FK'])
    df_is = df_is.drop_duplicates([col_groupby,'NIVOL_ID_FK'])
    for name, code in [('Nb_IS', 'IS')]:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

    # Vérification des codes
    print("\n===== Vérification des codes =====")
    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in [('Nb_IS', 'IS')]:
        codes_attendus = set(filtres_bc.get(code, []))
        codes_trouves = codes_df.intersection(codes_attendus)
        codes_manquants = codes_attendus - codes_df

        print(f"\nIndicateur : {name}")
        print(f"  Codes attendus : {codes_attendus}")
        print(f"  Codes trouvés  : {codes_trouves}")
        print(f"  Codes manquants: {codes_manquants}")

        df_res[name] = df_res['FORMATION_CODE'].isin(codes_attendus)

    def count_unique(group, col_name):
        return group.loc[group[col_name], 'NIVOL_ID_FK'].nunique()

    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({col: count_unique(g, col) for col in ['Nb_IS']})
    ).reset_index()

    # Somme globale par indicateur
    print("\n===== Somme globale par indicateur =====")
    totaux = result[[col for col, _ in [('Nb_IS', 'IS')]]].sum()
    for col in totaux.index:
        print(f"{col} : {totaux[col]}")


    df_nb_bene_actifs = df_is.groupby(col_groupby)['NIVOL_ID_FK'].nunique().rename("nb_bene_actifs").reset_index()

    result = pd.merge(result, df_nb_bene_actifs, on = col_groupby, how = 'left')
    result["Secours Taux_IS_actifs"] = np.where(
      (result["nb_bene_actifs"] == 0) | (result["nb_bene_actifs"].isna()),
      np.nan,
      result["Nb_IS"] / result["nb_bene_actifs"]
    )
    assert (result["Nb_IS"] <= result["nb_bene_actifs"]).all()
    return result[[col_groupby, "Secours Taux_IS_actifs"]]

def nb_bene_actifs_solidar(client, df, filtres_bc, df_ref_structure, col_groupby):

  query_bene_actifs = """SELECT
                          act.*,
                          insc.*
                      FROM `crf-pat.dataset_PAT_2025.crf_pat_2025_pegass_activite` AS act
                      INNER JOIN `crf-pat.dataset_PAT_2025.crf_pat_2025_pegass_activite_seance_inscription` AS insc
                          ON act.PEGASS_ACTIVITE_ID_PK = insc.PEGASS_ACTIVITE_ID_FK
                      WHERE insc.PEGASS_ACTIVITE_SEANCE_INSCRIPTION_STATUT = 'Valide' """

  df_bene_actifs = client.query(query_bene_actifs).to_dataframe()
  df_bene_actifs = df_bene_actifs.rename(columns = {'PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK': 'n_structure','PEGASS_ACTIVITE_SEANCE_INSCRIPTION_NIVOL_ID_FK' : 'NIVOL_ID_FK'})[['n_structure','NIVOL_ID_FK']].drop_duplicates()

  df = pd.merge(df.drop(['n_structure'], axis = 1), df_bene_actifs, on = 'NIVOL_ID_FK', how = 'inner')
  filtres_bc['all_solidar'] = filtres_bc['solidar'] + filtres_bc['solidar20']

  df_res = df[(df['FORMATION_RESULTAT'] == 'Apte') & (df['FORMATION_BENEVOLE_DANS_L_ANNEE'] == 'Oui')].copy()
  _ , _ , _, df_res = apply_rattachement_successif(df_ref_structure, df_res, col = 'n_structure')

  df_res = dt_rattachement(df_res, df_ref_structure)

  df_res = df_res.drop_duplicates(['n_structure','NIVOL_ID_FK'])


  for name, code in [('Maraude Nb_benevoles_actifs_formes', 'all_solidar')]:
      df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

  # Vérification des codes
  print("\n===== Vérification des codes =====")
  codes_df = set(df_res['FORMATION_CODE'].unique())

  for name, code in [('Maraude Nb_benevoles_actifs_formes', 'all_solidar')]:
      codes_attendus = set(filtres_bc.get(code, []))
      codes_trouves = codes_df.intersection(codes_attendus)
      codes_manquants = codes_attendus - codes_df

      print(f"\nIndicateur : {name}")
      print(f"  Codes attendus : {codes_attendus}")
      print(f"  Codes trouvés  : {codes_trouves}")
      print(f"  Codes manquants: {codes_manquants}")

      df_res[name] = df_res['FORMATION_CODE'].isin(codes_attendus)

  def count_unique(group, col_name):
      return group.loc[group[col_name], 'NIVOL_ID_FK'].nunique()

  result = df_res.groupby(col_groupby).apply(
      lambda g: pd.Series({col: count_unique(g, col) for col in ['Maraude Nb_benevoles_actifs_formes']})
  ).reset_index()

  # Somme globale par indicateur
  print("\n===== Somme globale par indicateur =====")
  totaux = result[[col for col, _ in [('Maraude Nb_benevoles_actifs_formes', 'all_solidar')]]].sum()
  for col in totaux.index:
      print(f"{col} : {totaux[col]}")

  return result
# ------------------------------
# Fonction principale
# ------------------------------

def clean_base_contact(client, df_ref_structure):

    filtres_bc = {
        'CRB' : ['CRB', 'ECRB', 'VI'],
        'ACRB' : ['ACRB','ACRB2','ACRB3','ACRB2024'], #'AVI'
        'TCAS' : ['TCAS', 'ETCAS'], #'TCAS2'
        'TCAU' : ['TCAU', 'ETCAU'],
        'TCEO' : ['TCEO','ESE'],
        'PSP' : ['PSP'], #'PSP1'
        'IRR' : ['IRR','IRRA','IRRJ'],
        'solidar' : ['SOLIDAR2','SOLIDAR1','SOLIDAR'],
        'solidar20' : ['PASSOLIDAR2020','ESOLIDAR2026','SOLIDAR2020'], #'PASSSOLIDAR2020'
        'AAD' : ['AAD'], #'IAD','MAO'
        'FAAD' : ['FAAD','FAAAD','EPIAF FAAD'],
        'FPSC' : ['FCFPSC','RATFCFPSC'],
        'AGQS' : ['AGQS'], #,'RATAGQS'
        'FIPSEN' : ['FIPSEN','RECFIPSEN'],
        'PSE1' : ['APTE PSE1', 'PSE1','RECPSE1', 'RATPSE1','PSE'], #rajout de PSE
        'PSE2' : ['RECPSE2','PSE2','RECPSE2', 'PSE', 'RATPSE2'],
        'CI' : ['CI P1 P2', 'CI', 'CIP1' ,'CIP2' ,'CIP3', 'CI EXT','RECCI', 'REC PSECI' ,'RECPSECI', 'RATCI', 'FCCI'],
        'PSC' : ["PSC1 IRR","EPSC1","RECPSC1","PSC1","PSC1 AC",'PSC', 'PSC IRR', 'EPSC', 'PSC AC'],
        'GQS' : ['GQS', 'GQS AC'],
        'IPSEN' : ['IPSEN'],
        'IPS' : ['IPS', 'IPS SR', 'IPSE', 'IPSEF', 'IPSJ', 'IPSJP', 'IPSM', 'IPSP', 'IPS AC'],
        'PREVIC' : ['PREVIC'],
        'FPS': ['RECFPS', 'FPS', 'FPSE', 'FCFPSE', 'RATFCFPSE'], #A voir si il faut suppr FCPSE
        'PSE': ['APTE PSE1', 'PSE1','RECPSE1', 'RATPSE1','RECPSE2','PSE2','RECPSE2', 'PSE', 'RATPSE2']
    }
    codes_filtres_bc = [element for sous_liste in filtres_bc.values() for element in sous_liste] 



    query_formation_session_resultat = """
        SELECT * FROM `crf-pat.dataset_PAT_2025.crf_pat_2025_formation_session_resultat`
        """
    df_formation_session_resultat = client.query(query_formation_session_resultat).to_dataframe()

    df_formation_session_resultat['FORMATION_DATE_OBTENTION'] = pd.to_datetime(df_formation_session_resultat['FORMATION_DATE_OBTENTION'], errors='coerce')
    df_formation_session_resultat['FORMATION_DATE_RECYCLAGE'] = pd.to_datetime(df_formation_session_resultat['FORMATION_DATE_RECYCLAGE'], errors='coerce')

    df_formation_session_resultat = df_formation_session_resultat[df_formation_session_resultat["FORMATION_CODE"].isin( codes_filtres_bc )]


    query_rattachement_benevole = """
        SELECT rattachement_benevole_nivol_id_fk, rattachement_benevole_structure_id_fk
        FROM `crf-pat.dataset_PAT_2025.crf_pat_2025_rattachement_benevole`
        """
    df_rattachement_benevole = client.query(query_rattachement_benevole).to_dataframe()
    df_rattachement_benevole.drop_duplicates(subset=["rattachement_benevole_nivol_id_fk"], inplace=True)



    df_formation_session_resultat_rattachement = pd.merge(
    df_formation_session_resultat,
    df_rattachement_benevole,
    left_on="NIVOL_ID_FK",
    right_on="rattachement_benevole_nivol_id_fk",
    how="left"
    )

    _ , _ , _, df_formation_session_resultat = apply_rattachement_successif(df_ref_structure, df_formation_session_resultat, col = 'FORMATION_SESSION_STRUCTURE_ID_FK')

    _ , _ , _, df_formation_session_resultat_rattachement = apply_rattachement_successif(df_ref_structure, df_formation_session_resultat_rattachement, col = 'rattachement_benevole_structure_id_fk')


    # df_formation_session_resultat_rattachement = df_formation_session_resultat_rattachement[
    # df_formation_session_resultat_rattachement["rattachement_benevole_structure_id_fk"].isin(
    #     df_ref_structure["n_structure"] )]

    # df_formation_session_resultat = df_formation_session_resultat[
    # df_formation_session_resultat["FORMATION_SESSION_STRUCTURE_ID_FK"].isin(
    #     df_ref_structure["n_structure"]
    # )]

    df_formation_count_session = df_formation_session_resultat.copy()
    df_formation_count_session = df_formation_count_session.rename(columns={"FORMATION_SESSION_STRUCTURE_ID_FK": "n_structure"})
    df_formation_count_session = dt_rattachement(df_formation_count_session, df_ref_structure)
    df_formation_count_session_2025 = df_formation_count_session[df_formation_count_session['FORMATION_DATE_OBTENTION'].dt.year == 2025].copy()

    df_formation_session_resultat =df_formation_session_resultat_rattachement
    df_formation_session_resultat = df_formation_session_resultat.rename(columns={"rattachement_benevole_structure_id_fk": "n_structure"})

    mask_2025 = df_formation_session_resultat['FORMATION_DATE_OBTENTION'].dt.year == 2025

    df_formation_session_resultat.loc[mask_2025, "n_structure"] = (
        df_formation_session_resultat.loc[mask_2025, "n_structure"]
        .fillna(df_formation_session_resultat.loc[mask_2025, "FORMATION_SESSION_STRUCTURE_ID_FK"])
    )


    df_formation_session_resultat = df_formation_session_resultat[df_formation_session_resultat['FORMATION_RESULTAT'] != 'Absent']


    return df_formation_session_resultat, df_formation_count_session_2025

def indicateurs_base_contact(client,df_formation_session_resultat, df_formation_count_session_2025, df_ref_structure): 
    # Définition filtres
    filtres_bc = {
        'CRB' : ['CRB', 'ECRB', 'VI'],
        'ACRB' : ['ACRB','ACRB2','ACRB3','ACRB2024'], #'AVI'
        'TCAS' : ['TCAS', 'ETCAS'], #'TCAS2'
        'TCAU' : ['TCAU', 'ETCAU'],
        'TCEO' : ['TCEO','ESE'],
        'PSP' : ['PSP'], #'PSP1'
        'IRR' : ['IRR','IRRA','IRRJ'],
        'solidar' : ['SOLIDAR2','SOLIDAR1','SOLIDAR'],
        'solidar20' : ['PASSOLIDAR2020','ESOLIDAR2026','SOLIDAR2020'], #'PASSSOLIDAR2020'
        'AAD' : ['AAD'], #'IAD','MAO'
        'FAAD' : ['FAAD','FAAAD','EPIAF FAAD'],
        'FPSC' : ['FCFPSC','RATFCFPSC'],
        'AGQS' : ['AGQS'], #,'RATAGQS'
        'FIPSEN' : ['FIPSEN','RECFIPSEN'],
        'PSE1' : ['APTE PSE1', 'PSE1','RECPSE1', 'RATPSE1','PSE'], #rajout de PSE
        'PSE2' : ['RECPSE2','PSE2','RECPSE2', 'PSE', 'RATPSE2'],
        'CI' : ['CI P1 P2', 'CI', 'CIP1' ,'CIP2' ,'CIP3', 'CI EXT','RECCI', 'REC PSECI' ,'RECPSECI', 'RATCI', 'FCCI'],
        'PSC' : ["PSC1 IRR","EPSC1","RECPSC1","PSC1","PSC1 AC",'PSC', 'PSC IRR', 'EPSC', 'PSC AC'],
        'GQS' : ['GQS', 'GQS AC'],
        'IPSEN' : ['IPSEN'],
        'IPS' : ['IPS', 'IPS SR', 'IPSE', 'IPSEF', 'IPSJ', 'IPSJP', 'IPSM', 'IPSP', 'IPS AC'],
        'PREVIC' : ['PREVIC'],
        'FPS': ['RECFPS', 'FPS', 'FPSE', 'FCFPSE', 'RATFCFPSE'], #A voir si il faut suppr FCPSE
        'PSE': ['APTE PSE1', 'PSE1','RECPSE1', 'RATPSE1','RECPSE2','PSE2','RECPSE2', 'PSE', 'RATPSE2']
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

    # nb_sessions = nb_session_form(df_filtered_2025, filtres_bc, 'n_structure') => Ancienne version
    # nb_sessions_DT = nb_session_form(df_filtered_2025, filtres_bc, 'DT_de_rattachement')

    #Nouvelle version
    nb_sessions = nb_session_form(df_formation_count_session_2025, filtres_bc, 'n_structure')
    nb_sessions_DT = nb_session_form(df_formation_count_session_2025, filtres_bc, 'DT_de_rattachement')

    nb_apte_formation = nb_bene_aptes(df_filtered_2025, filtres_bc, 'n_structure')
    nb_apte_formation_DT = nb_bene_aptes(df_filtered_2025, filtres_bc, 'DT_de_rattachement')

    taux_rec = taux_recy(df_filtered_2025, filtres_bc, 'n_structure')
    taux_rec_DT = taux_recy(df_filtered_2025, filtres_bc, 'DT_de_rattachement')

    taux_nouveau_form = taux_ren(df_filtered, filtres_bc, 'n_structure')
    taux_nouveau_form_DT = taux_ren(df_filtered, filtres_bc, 'DT_de_rattachement')

    # Indicateurs fusion 

    nb_actifs_solidar = nb_bene_actifs_solidar(client, df_formation_session_resultat, filtres_bc, df_ref_structure, 'n_structure')
    nb_actifs_solidar_DT = nb_bene_actifs_solidar(client, df_formation_session_resultat, filtres_bc, df_ref_structure, 'DT_de_rattachement')

    taux_is_actifs = taux_IS(client, df_formation_session_resultat, filtres_bc, df_ref_structure, 'n_structure')
    taux_is_actifs_DT = taux_IS(client, df_formation_session_resultat, filtres_bc, df_ref_structure, 'DT_de_rattachement')

    df_nvx_forme_crb = nb_nvx_forme_crb(client, df_filtered_2025, filtres_bc, 'n_structure')
    df_nvx_forme_crb_DT = nb_nvx_forme_crb(client, df_filtered_2025, filtres_bc, 'DT_de_rattachement')

    indicateurs_base_contact_pd, indicateurs_base_contact_DT_pd = fusion_bc_final(
        nb_suivi_formation, nb_suivi_formation_DT,
        nb_suivi_formation_tous, nb_suivi_formation_tous_DT,
        nb_sessions, nb_sessions_DT,
        nb_apte_formation, nb_apte_formation_DT,
        taux_rec, taux_rec_DT,
        taux_nouveau_form, taux_nouveau_form_DT,
        nb_actifs_solidar, nb_actifs_solidar_DT,
        taux_is_actifs, taux_is_actifs_DT,
        df_nvx_forme_crb, df_nvx_forme_crb_DT,
        'n_structure'
    )

    indicateurs_base_contact_DT_pd = indicateurs_base_contact_DT_pd[indicateurs_base_contact_DT_pd['n_structure'] != '']

    return indicateurs_base_contact_pd, indicateurs_base_contact_DT_pd
