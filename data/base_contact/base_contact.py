import pandas as pd
import numpy as np
import re
import sys
import os
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *
from datetime import datetime



filtres_bc = {
        'CRB' : ['CRB', 'ECRB', 'VI'],
        'ACRB' : ['ACRB2','ACRB2024'], # suppression'AVI'
        'TCAS' : ['TCAS', 'ETCAS'], # suppression 'TCAS2'
        'TCAU' : ['TCAU', 'ETCAU'],
        'TCEO' : ['TCEO','ESE'],
        'PSP' : ['PSP'], #suppression 'PSP1'
        'IRR' : ['IRR','IRRA','IRRJ'],
        'solidar' : ['SOLIDAR2','SOLIDAR1','SOLIDAR'],
        'solidar20' : ['PASSOLIDAR2020','ESOLIDAR2026','SOLIDAR2020'], # suppression'PASSSOLIDAR2020'
        'AAD' : ['AAD'], # suppression'IAD','MAO'
        'FAAD' : ['FAAD','EPIAF FAAD'],
        'FPSC' : ['FCFPSC','RATFCFPSC', 'FPSC', 'RECFPSC', 'PICF FPSC', 'PAE3'], #ajout de 'FPSC', 'RECFPSC', 'PICF FPSC'
        'AGQS' : ['AGQS'], # suppression'RATAGQS'
        'FIPSEN' : ['FIPSEN','RECFIPSEN'],
        'PSE1' : ['APTE PSE1', 'PSE1','RECPSE1', 'RATPSE1', 'FCPSE1'], #ajout formation continue FC
        'PSE1_i' : ['APTE PSE1', 'PSE1', 'RATPSE1'],
        'RECPSE1' : ['RECPSE1', 'FCPSE1'],
        'PSE2' : ['RECPSE2','PSE2','RECPSE2', 'PSE', 'RATPSE2', 'FCPSE2', 'FCPSE', 'PSE AGSU'], #ajout formation continue FC + PSE
        'PSE2_i' : ['PSE','PSE2','RATPSE2'],
        'RECPSE2' : ['RECPSE2', 'FCPSE2'],
        'CI' : ['CI P1 P2', 'CI','CIP2' ,'RECCI', 'REC PSECI' ,'RECPSECI', 'FCCI'], #'RATCI', 'CIP1','CI EXT' 
        'CI_i' : ['CI', 'CI P1 P2', 'CI P1', 'CI P2', 'CI EXT', 'RATCI'],
        'FPSE': ['RECFPS', 'FPS', 'FPSE', 'FCFPSE', 'RATFCFPSE', 'PICF FPS', 'PICF FPSE', 'FPSE AFGU'],
        'FPSE_i': ['FPS', 'FPSE', 'FCFPSE', 'RATFCFPSE', 'PICF FPS', 'PICF FPSE', 'FPSE AFGU'],
        'RECFPSE': ['RECFPS'],
        'RECCI' : ['RECCI', 'REC PSECI', 'RECPSECI'],
        'PSC' : ["PSC1 IRR","EPSC1","RECPSC1","PSC1","PSC1 AC",'PSC', 'PSC IRR', 'EPSC', 'PSC AC', 'FCPSC'], #ajout de 'PSC', 'PSC IRR', 'EPSC', 'PSC AC', 'FCPSC'
        'GQS' : ['GQS', 'GQS AC', 'FIPS', 'FIPS2'],
        'IPSEN' : ['IPSEN'],
        'IPS' : ['IPS', 'IPS SR', 'IPSE', 'IPSEF', 'IPSJ', 'IPSJP', 'IPSM', 'IPSP', 'IPS AC'],
        'PREVIC' : ['PREVIC'],
        'FPS': ['RECFPS', 'FPS', 'FPSE', 'FCFPSE', 'RATFCFPSE', 'PICF FPS', 'PICF FPSE'], #ajout de 'PICF FPS', 'PICF FPSE'
        'PSE': ['APTE PSE1', 'PSE1','RECPSE1', 'RATPSE1', 'FCPSE1', 'RECPSE2','PSE2','RECPSE2', 'PSE', 'FCPSE', 'RATPSE2', 'FCPSE2'],
        'ATEX' : ['ATEXTILE'],
        'SAH' : ['SAH', 'TASA'],
        'ASAH' : ['ASAH', 'FASAH']

        }




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
def nb_bene_suivi_form(df_filtered, filtres_bc, col_groupby,target_date):
    """
    Nombre de bénévoles formés aux différentes formations  (toutes années confondues)
    """
    target = pd.Timestamp(target_date)
    year = target.year
    df_res = df_filtered[(df_filtered['FORMATION_BENEVOLE_DANS_L_ANNEE'] == 'Oui') & (df_filtered['FORMATION_DATE_OBTENTION'] <= target)].copy()

    # Filtre spécial GQS
    filtres_bc['taux_GQS'] = filtres_bc['GQS'] + filtres_bc['PSC'] + filtres_bc['PSE1'] + filtres_bc['PSE2']

    indic_filtres = [('AEO Nb_AAD', 'AAD'),
                       (f'Dispositifs_d_urgence Nb_formes_TCAU_{year}', 'TCAU'),
                       (f'Dispositifs_d_urgence Nb_formes_TCEO_{year}', 'TCEO'),
                       (f'Dispositifs_d_urgence Nb_formes_PSP_{year}', 'PSP'),
                       (f'Dispositifs_d_urgence Nb_formes_IRR_{year}', 'IRR'),
                       (f'Dispositifs_d_urgence Nb_formes_GQS_{year}', 'taux_GQS'),
                       (f'Structure Nb_formes_CRB_{year}', 'CRB')]
    indic_listes = [col for col, _ in indic_filtres]
    
    # Ajouter colonnes booléennes par filtre
    for name, code in indic_filtres:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

    # Vérification des codes
    print("\n===== Vérification des codes =====")
    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in indic_filtres:
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
        lambda g: pd.Series({col: count_unique(g, col) for col in indic_listes})
    ).reset_index()

    # Somme globale par indicateur
    print("\n===== Somme globale par indicateur =====")
    totaux = result[[col for col, _ in indic_filtres]].sum()
    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

    return result

def nb_suivi_form(df_filtered, filtres_bc, col_groupby, target_date):
    """
    Nombre de formateurs  (déclarés aptes toutes années confondues)
    """
    target = pd.Timestamp(target_date)
    year = target.year
    df_res = df_filtered[(df_filtered['FORMATION_RESULTAT'] == 'Apte') & (df_filtered['FORMATION_DATE_OBTENTION'] <= target)].copy()

    indic_filtres = [('Maraude Nb_SOLIDAR', 'all_solidar'),
                       ('Maraude Nb_SOLIDAR2020', 'solidar20'),
                       ('AEO Nb_FAAD', 'FAAD'),
                       (f'Structure Nb_formateurs_CRB_{year}', 'ACRB'),
                       (f'Structure Nb_formes_TCAS_{year}', 'TCAS'),
                       ('Textile Animateurs_textile', 'ATEX'),
                       ('Aide_alimentaire nb_ASAH' , 'ASAH'),
                       ('Aide_alimentaire nb_SAH' , 'SAH')]
    indic_liste = [col for col, _ in indic_filtres]
    # Ajouter colonnes booléennes par filtre
    for name, code in indic_filtres:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

    # Vérification des codes
    print("\n===== Vérification des codes =====")
    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in indic_filtres:
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
        lambda g: pd.Series({col: count_unique(g, col) for col in indic_liste})
    ).reset_index()

    # Somme globale par indicateur
    print("\n===== Somme globale par indicateur =====")
    totaux = result[[col for col, _ in indic_filtres]].sum()
    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

    return result

def nb_suivi_form_tous(df, filtres_bc, col_groupby, target_date):
    """
    Nombre de non bénévoles formés aux différentes formations
    """
    target = pd.Timestamp(target_date)
    year = target.year
    df_res = df[(df['FORMATION_BENEVOLE_DANS_L_ANNEE'] != 'Oui') & (df['FORMATION_DATE_OBTENTION'] <= target) & (df['FORMATION_DATE_OBTENTION'].dt.year == year)].copy()
    indic_filtres = [(f'Formation_grand_public Nb_formes_PSC_{year}', 'PSC'),
                       (f'Formation_grand_public Nb_formes_GQS_{year}', 'GQS'),
                       (f'Formation_grand_public Nb_formes_IPS_{year}', 'IPS'),
                       (f'Formation_grand_public Nb_formes_IPSEN_{year}', 'IPSEN'),
                       (f'Formation_grand_public Nb_formes_PREVIC_{year}', 'PREVIC')]
    indic_liste = [col for col, _ in indic_filtres]
    for name, code in indic_filtres:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

    # Vérification des codes
    print("\n===== Vérification des codes =====")
    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in indic_filtres:
        codes_attendus = set(filtres_bc.get(code, []))
        codes_trouves = codes_df.intersection(codes_attendus)
        codes_manquants = codes_attendus - codes_df

        print(f"\nIndicateur : {name}")
        print(f"  Codes attendus : {codes_attendus}")
        print(f"  Codes trouvés  : {codes_trouves}")
        print(f"  Codes manquants: {codes_manquants}")

        df_res[name] = df_res['FORMATION_CODE'].isin(codes_attendus)

    mask_gqs = df_res[f'Formation_grand_public Nb_formes_GQS_{year}']
    mask_psc = df_res[f'Formation_grand_public Nb_formes_PSC_{year}']

    sessions_psc = df_res.loc[mask_psc, 'NIVOL_ID_FK']

    df_res.loc[mask_gqs & df_res['NIVOL_ID_FK'].isin(sessions_psc),
              f'Formation_grand_public Nb_formes_GQS_{year}'] = False

    def count_unique(group, col_name):
        return group.loc[group[col_name], 'NIVOL_ID_FK'].nunique()

    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({col: count_unique(g, col) for col in indic_liste})
    ).reset_index()

    # Somme globale par indicateur
    print("\n===== Somme globale par indicateur =====")
    totaux = result[[col for col, _ in indic_filtres]].sum()
    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

    return result




def nb_session_form(df_year, filtres_bc, col_groupby, target_date):
    """
    Nombre de session de formations sur 2025
    """
    #df_res = df_2025[df_2025['FORMATION_BENEVOLE_DANS_L_ANNEE'] == 'Oui'].copy()
    df_res = df_year.copy()
    target = pd.Timestamp(target_date)
    year = target.year

    df_res = df_res[df_res['FORMATION_DATE_OBTENTION'] <= target]

    indic_filtres = [(f'Formation_grand_public Nb_sessions_PSC_{year}', 'PSC'),
                       (f'Formation_grand_public Nb_sessions_GQS_{year}', 'GQS'),
                       (f'Formation_grand_public Nb_sessions_IPS_{year}', 'IPS'),
                       (f'Formation_grand_public Nb_sessions_IPSEN_{year}', 'IPSEN'),
                       (f'Formation_grand_public Nb_sessions_PREVIC_{year}', 'PREVIC'),
                       (f'Secours Nb_sessions_PSE', 'PSE'),
                       (f'Secours Nb_sessions_CI', 'CI'),
                       (f'Secours Nb_sessions_FPSE', 'FPSE')]
    indic_liste = [col for col, _ in indic_filtres]
    for name, code in indic_filtres:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

        # Vérification des codes
    print("\n===== Vérification des codes =====")
    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in indic_filtres:
        codes_attendus = set(filtres_bc.get(code, []))
        codes_trouves = codes_df.intersection(codes_attendus)
        codes_manquants = codes_attendus - codes_df

        print(f"\nIndicateur : {name}")
        print(f"  Codes attendus : {codes_attendus}")
        print(f"  Codes trouvés  : {codes_trouves}")
        print(f"  Codes manquants: {codes_manquants}")

        df_res[name] = df_res['FORMATION_CODE'].isin(codes_attendus)

    mask_gqs = df_res[f'Formation_grand_public Nb_sessions_GQS_{year}']
    mask_psc = df_res[f'Formation_grand_public Nb_sessions_PSC_{year}']

    sessions_psc = df_res.loc[mask_psc, 'SESSION_ID_FK']

    df_res.loc[mask_gqs & df_res['SESSION_ID_FK'].isin(sessions_psc),
              f'Formation_grand_public Nb_sessions_GQS_{year}'] = False

    def count_unique(group, col_name):
        return group.loc[group[col_name], 'SESSION_ID_FK'].nunique()

    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({col: count_unique(g, col) for col in indic_liste})
    ).reset_index()

    # Somme globale par indicateur
    print("\n===== Somme globale par indicateur =====")
    totaux = result[[col for col, _ in indic_filtres]].sum()
    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

    return result

# ======================
# Structures menant activité
# ======================

def nb_structures_menant_activite(df_2025, filtres_bc, col_groupby, target_date):
    """
    Nombre de session de formations sur 2025
    """
    #df_res = df_2025[df_2025['FORMATION_BENEVOLE_DANS_L_ANNEE'] == 'Oui'].copy()
    df_res = df_2025.copy()
    target = pd.Timestamp(target_date)
    year = target.year

    df_res = df_res[df_res['FORMATION_DATE_OBTENTION'] <= target]

    for name, code in [('Dispositifs_d_urgence Structures_menant_activite_TCAU', 'TCAU'),
                       ('Dispositifs_d_urgence Structures_menant_activite_PSP', 'PSP'),
                       ('Dispositifs_d_urgence Structures_menant_activite_GQS', 'GQS')]:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

        # Vérification des codes
    print("\n===== Vérification des codes =====")
    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in [('Dispositifs_d_urgence Structures_menant_activite_TCAU', 'TCAU'),
                       ('Dispositifs_d_urgence Structures_menant_activite_PSP', 'PSP'),
                       ('Dispositifs_d_urgence Structures_menant_activite_GQS', 'GQS')]:
        codes_attendus = set(filtres_bc.get(code, []))
        codes_trouves = codes_df.intersection(codes_attendus)
        codes_manquants = codes_attendus - codes_df

        print(f"\nIndicateur : {name}")
        print(f"  Codes attendus : {codes_attendus}")
        print(f"  Codes trouvés  : {codes_trouves}")
        print(f"  Codes manquants: {codes_manquants}")

        df_res[name] = df_res['FORMATION_CODE'].isin(codes_attendus)

    cols = [
        col for col,code in [('Dispositifs_d_urgence Structures_menant_activite_TCAU', 'TCAU'),
                       ('Dispositifs_d_urgence Structures_menant_activite_PSP', 'PSP'),
                       ('Dispositifs_d_urgence Structures_menant_activite_GQS', 'GQS')]
    ]


    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({
            col: g.loc[g[col], 'n_structure'].nunique()
            for col in cols
        })
    ).reset_index()

    # Somme globale par indicateur
    print("\n===== Somme globale par indicateur =====")
    totaux = result[[col for col, _ in [('Dispositifs_d_urgence Structures_menant_activite_TCAU', 'TCAU'),
                       ('Dispositifs_d_urgence Structures_menant_activite_PSP', 'PSP'),
                       ('Dispositifs_d_urgence Structures_menant_activite_GQS', 'GQS')]]].sum()
    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

    return result

# ------------------------------
# Fusion
# ------------------------------

def fusion_bc_final(df_ref_structure, df_ref_structure_DT,nb_bene_suivi_formation, nb_bene_suivi_formation_DT,
                    nb_suivi_formation, nb_suivi_formation_DT,
                    nb_suivi_formation_tous, nb_suivi_formation_tous_DT,
                    nb_sessions, nb_sessions_DT,
                    nb_actifs_solidar, nb_actifs_solidar_DT,
                    taux_is_actifs, taux_is_actifs_DT,
                    df_nvx_forme_crb, df_nvx_forme_crb_DT,
                    nb_structures_ma, nb_structures_ma_DT,
                    col_groupby):

    """
    Cette fonction permet de fusionner tous les dataframes en un, on utilise df_ref_structure comme référence et on fait un left join dessus pour avoir exactement les mêmes structures
    On peut améliorer la robustesse en changeant les arguments en deux listes, une toutes structure et une DT.
    """
    # Fusion des DataFrames
    def merge_all(dfs):
        from functools import reduce
        return reduce(lambda left, right: left.merge(right, on=col_groupby, how='left'), dfs)

    indicateurs_base_contact = merge_all([df_ref_structure,nb_bene_suivi_formation,
                                         nb_suivi_formation,
                                         nb_suivi_formation_tous,
                                         nb_sessions,
                                         nb_actifs_solidar,
                                         taux_is_actifs,
                                         df_nvx_forme_crb])

    # Même pour DT
    for df in [nb_bene_suivi_formation_DT,nb_suivi_formation_DT, nb_suivi_formation_tous_DT, nb_sessions_DT, nb_actifs_solidar_DT,taux_is_actifs_DT,df_nvx_forme_crb_DT,nb_structures_ma_DT]:
        df.rename(columns={'DT_de_rattachement':'n_structure'}, inplace=True)

    indicateurs_base_contact_DT = merge_all([df_ref_structure_DT,nb_bene_suivi_formation_DT,nb_suivi_formation_DT,
                                            nb_suivi_formation_tous_DT,
                                            nb_sessions_DT,
                                            nb_actifs_solidar_DT,
                                            taux_is_actifs_DT,
                                            df_nvx_forme_crb_DT,nb_structures_ma_DT])

    return indicateurs_base_contact, indicateurs_base_contact_DT

# ------------------------------
# Indicateurs fusionnés
# ------------------------------

def nb_nvx_forme_crb(client, df, filtres_bc, col_groupby, target_date = '2025-12-31'):
    """ 
    Nombre de nouveaux bénévoles formés CRB, on détermine les nouveaux bénévoles grâce à la requête SQL
    # Il faut que le bénévole ne soit jamais apparu avant et que le bénévole soit toujours présent au 12-31-2025
    """
    target = pd.Timestamp(target_date)
    year = target.year

    query_nvx_bene = f"""SELECT
                DISTINCT rattachement_benevole_nivol_id_fk
            FROM `crf-pat.dataset_PAT_{year}.crf_pat_{year}_rattachement_benevole` t
            WHERE 
                -- Date de début en {year}
                EXTRACT(YEAR FROM rattachement_benevole_date_debut) = {year}

                -- Jamais apparu avant {year}
                AND NOT EXISTS (
                    SELECT 1
                    FROM `crf-pat.dataset_PAT_{year}.crf_pat_{year}_rattachement_benevole` t2
                    WHERE t2.rattachement_benevole_nivol_id_fk = t.rattachement_benevole_nivol_id_fk
                    AND t2.rattachement_benevole_date_debut < '{year}-01-01'
                )"""
        # WHERE rattachement_benevole_date_debut >= DATE('2025-01-01')
        # AND rattachement_benevole_date_debut < DATE('2026-01-01')"""

    df_nvx_bene = client.query(query_nvx_bene).to_dataframe()
    df_nvx_bene = df_nvx_bene.rename(columns = {'rattachement_benevole_nivol_id_fk' : 'NIVOL_ID_FK'})['NIVOL_ID_FK'].drop_duplicates()

    df = pd.merge(df, df_nvx_bene, on = 'NIVOL_ID_FK', how = 'inner')

    df_res = df[(df['FORMATION_BENEVOLE_DANS_L_ANNEE'] == 'Oui') & (df['FORMATION_DATE_OBTENTION'].dt.year == year)].copy()
    for name, code in [(f'Structure Nb_nvx_formes_CRB_{year}', 'CRB')]:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

    # Vérification des codes
    print("\n===== Vérification des codes =====")
    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in [(f'Structure Nb_nvx_formes_CRB_{year}', 'CRB')]:
        codes_attendus = set(filtres_bc.get(code, []))
        codes_trouves = codes_df.intersection(codes_attendus)
        codes_manquants = codes_attendus - codes_df

        print(f"\nIndicateur : {name}")
        print(f"  Codes attendus : {codes_attendus}")
        print(f"  Codes trouvés  : {codes_trouves}")
        print(f"  Codes manquants: {codes_manquants}")

    def count_unique(group, col_name):
        return group.loc[group[col_name], 'NIVOL_ID_FK'].nunique()

    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({col: count_unique(g, col) for col in [f'Structure Nb_nvx_formes_CRB_{year}']})
    ).reset_index()

    # Somme globale par indicateur
    print("\n===== Somme globale par indicateur =====")
    totaux = result[[col for col, _ in [(f'Structure Nb_nvx_formes_CRB_{year}', 'CRB')]]].sum()
    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

    return result


def nb_bene_actifs_solidar(client, df, filtres_bc, df_ref_structure, col_groupby, target_date = '2025-12-31'):

    target = pd.Timestamp(target_date)
    year = target.year
    query_bene_actifs = f"""SELECT
                            act.*,
                            insc.*
                        FROM `crf-pat.dataset_PAT_{year}.crf_pat_{year}_pegass_activite` AS act
                        INNER JOIN `crf-pat.dataset_PAT_{year}.crf_pat_{year}_pegass_activite_seance_inscription` AS insc
                            ON act.PEGASS_ACTIVITE_ID_PK = insc.PEGASS_ACTIVITE_ID_FK
                        WHERE insc.PEGASS_ACTIVITE_SEANCE_INSCRIPTION_STATUT = 'Valide' AND PEGASS_ACTIVITE_DATE_DEBUT >= DATE('{year}-01-01')  AND PEGASS_ACTIVITE_DATE_DEBUT <= DATE('{target_date}')"""

    df_bene_actifs = client.query(query_bene_actifs).to_dataframe()
    df_bene_actifs = df_bene_actifs.rename(columns = {'PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK': 'n_structure','PEGASS_ACTIVITE_SEANCE_INSCRIPTION_NIVOL_ID_FK' : 'NIVOL_ID_FK'})[['n_structure','NIVOL_ID_FK']].drop_duplicates()

    df = pd.merge(df.drop(['n_structure'], axis = 1), df_bene_actifs, on = 'NIVOL_ID_FK', how = 'inner')

    df_res = df[(df['FORMATION_RESULTAT'] == 'Apte') & (df['FORMATION_BENEVOLE_DANS_L_ANNEE'] == 'Oui')].copy()
    df_res = apply_rattachement_successif(df_ref_structure, df_res, col = 'n_structure')

    df_res = df_res.drop('DT_de_rattachement', axis = 1)
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

def clean_base_contact(client, df_ref_structure, target_date="2025-12-31"):
    """
    Traitements à partir de la table brute big query:
    - Filtre pour garder uniquement les codes formation nécessaires et les nivols absents aux sessions
    - Join avec gaia (rattachement_benevole) pour obtenir les structures de rattachement des nivols
    - Dataframe df_formation_count_session_2025 pour garder uniquement les structures organisatrices quand on doit calculer le nombre de session
    - apply_rattachement_benevole pour remplacer les numéros de structure ILs et équipes locales par leur rattachement UL ou DT
    """
    target = pd.Timestamp(target_date)
    year = target.year

    bdd_year = year

    if year < 2025:
        bdd_year = 2025

    codes_filtres_bc = list({element for sous_liste in filtres_bc.values() for element in sous_liste})
    TARGET_YEAR = pd.to_datetime(target_date).year

    query_formation_session_resultat = f"""
        SELECT * FROM `crf-pat.dataset_PAT_2026.crf_pat_2026_formation_session_resultat`
        """ # On ne change pas le dataset car 2026 est supposé être mis à jour régulièrement, devra peut-être être changé ultérieurement
    df_formation_session_resultat = client.query(query_formation_session_resultat).to_dataframe()

    df_formation_session_resultat['FORMATION_DATE_OBTENTION'] = pd.to_datetime(df_formation_session_resultat['FORMATION_DATE_OBTENTION'], errors='coerce')
    df_formation_session_resultat['FORMATION_DATE_RECYCLAGE'] = pd.to_datetime(df_formation_session_resultat['FORMATION_DATE_RECYCLAGE'], errors='coerce')

    df_formation_session_resultat = df_formation_session_resultat[df_formation_session_resultat["FORMATION_CODE"].isin(codes_filtres_bc)]

    df_formation_session_resultat_fpg = df_formation_session_resultat.copy()
    df_formation_session_resultat_fpg = df_formation_session_resultat_fpg.rename(columns={'FORMATION_SESSION_STRUCTURE_ID_FK' : 'n_structure'})

    df_formation_session_resultat_fpg = apply_rattachement_successif(df_ref_structure, df_formation_session_resultat_fpg, col = 'n_structure')


    query_rattachement_benevole = f"""
        SELECT *
        FROM `crf-pat.dataset_PAT_{bdd_year}.crf_pat_{bdd_year}_rattachement_benevole`
        """

        #SELECT rattachement_benevole_nivol_id_fk, rattachement_benevole_structure_id_fk
    df_rattachement_benevole = client.query(query_rattachement_benevole).to_dataframe()
    #df_rattachement_benevole.drop_duplicates(subset=["rattachement_benevole_nivol_id_fk"], inplace=True)

    df_rattachement_benevole["rattachement_benevole_date_fin"] = pd.to_datetime(df_rattachement_benevole["rattachement_benevole_date_fin"])

    df_rattachement_benevole["rattachement_benevole_date_debut"] = pd.to_datetime(
    df_rattachement_benevole["rattachement_benevole_date_debut"],
    errors="coerce"
    )

    df_rattachement_benevole = (
        df_rattachement_benevole
        .sort_values("rattachement_benevole_date_debut", ascending=False)
        .drop_duplicates(subset="rattachement_benevole_nivol_id_fk", keep="first")
        .copy()
    )

    df_rattachement_benevole = df_rattachement_benevole.drop_duplicates("rattachement_benevole_nivol_id_fk")

    
    df_rattachement_benevole = df_rattachement_benevole.loc[
        (df_rattachement_benevole["rattachement_benevole_date_fin"].isna()
        | (df_rattachement_benevole["rattachement_benevole_date_fin"] >= target)) & (df_rattachement_benevole["rattachement_benevole_date_debut"]  <= target)
    ]
    
    df_rattachement_benevole = df_rattachement_benevole[["rattachement_benevole_nivol_id_fk","rattachement_benevole_structure_id_fk"]]



    df_formation_session_resultat_rattachement = pd.merge(
        df_formation_session_resultat,
        df_rattachement_benevole,
        left_on="NIVOL_ID_FK",
        right_on="rattachement_benevole_nivol_id_fk",
        how="left"
    )



    df_formation_count_session = df_formation_session_resultat.copy()
    df_formation_count_session = df_formation_count_session.rename(columns={"FORMATION_SESSION_STRUCTURE_ID_FK": "n_structure"})

    df_formation_count_session = apply_rattachement_successif(df_ref_structure, df_formation_count_session, col = 'n_structure')


    df_formation_count_session = dt_rattachement(df_formation_count_session, df_ref_structure)
    df_formation_count_session_year = df_formation_count_session[df_formation_count_session['FORMATION_DATE_OBTENTION'].dt.year == TARGET_YEAR].copy()

    df_formation_session_resultat = df_formation_session_resultat_rattachement
    df_formation_session_resultat = df_formation_session_resultat.rename(columns={"rattachement_benevole_structure_id_fk": "n_structure"})
    df_formation_session_resultat = apply_rattachement_successif(df_ref_structure, df_formation_session_resultat, col = 'n_structure')

    df_formation_session_resultat = df_formation_session_resultat[df_formation_session_resultat['FORMATION_RESULTAT'] != 'Absent']

    # On garde seulement les structures dans df_ref_structure

    liste_structure_garder = df_ref_structure['n_structure'].drop_duplicates().tolist()
    df_formation_session_resultat = df_formation_session_resultat[df_formation_session_resultat['n_structure'].isin(liste_structure_garder)]
    df_formation_session_resultat_IS = df_formation_session_resultat_IS[df_formation_session_resultat_IS['n_structure'].isin(liste_structure_garder)]
    df_formation_session_resultat_fpg = df_formation_session_resultat_fpg[df_formation_session_resultat_fpg['n_structure'].isin(liste_structure_garder)]
    df_formation_count_session_year = df_formation_count_session_year[df_formation_count_session_year['n_structure'].isin(liste_structure_garder)]

    
    df_formation_session_resultat_fpg = dt_rattachement(df_formation_session_resultat_fpg, df_ref_structure)
    df_formation_session_resultat = dt_rattachement(df_formation_session_resultat, df_ref_structure)
    df_formation_session_resultat_IS = dt_rattachement(df_formation_session_resultat_IS, df_ref_structure)


    return df_formation_session_resultat, df_formation_count_session_year, df_formation_session_resultat_fpg

def indicateurs_base_contact(client,df_formation_session_resultat, df_formation_count_session_year,df_formation_session_resultat_fpg, df_ref_structure, target_date="2025-12-31", half_year = False):
    """
    Utilisation de toutes les fonctions du fichier pour calculer les indicateurs fonction par fonction.
    Les résultats sont stockés dans un dataframe différent à chaque fois, on a un calcul par structure et un par DT de rattachement pour obtenir les deux types d'agrégat.
    Tous les dataframes sont ensuite données à la fonction de fusion pour obtenir deux dataframes finaux : un par structure et un par DT, qui sont ensuite retournés 
    half_year : si les données sont calculés en milieu d'année (TRUE), on prend comme dénominateur le nombre d'apte PSE1, PSE2, CI, FPSC de 2 ans plus tôt, sinon 1 an plus tôt
    """
    # Définition filtres
    filtres_bc['all_solidar'] = filtres_bc['solidar'] + filtres_bc['solidar20']

    target = pd.Timestamp(target_date)
    year = target.year

    df_filtered = df_formation_session_resultat.copy()
    df_filtered = df_filtered[df_filtered['FORMATION_CODE'].isin(flatten(list(filtres_bc.values())))]

    df_filtered_year = df_filtered[df_filtered['FORMATION_DATE_OBTENTION'].dt.year == year].copy()

    # Calculs indicateurs
    nb_bene_suivi_formation = nb_bene_suivi_form(df_filtered, filtres_bc, 'n_structure', target_date)
    nb_bene_suivi_formation_DT = nb_bene_suivi_form(df_filtered, filtres_bc, 'DT_de_rattachement', target_date)

    nb_suivi_formation = nb_suivi_form(df_filtered, filtres_bc, 'n_structure', target_date)
    nb_suivi_formation_DT = nb_suivi_form(df_filtered, filtres_bc, 'DT_de_rattachement', target_date)

    nb_suivi_formation_tous = nb_suivi_form_tous(df_formation_session_resultat_fpg, filtres_bc, 'n_structure', target_date)
    nb_suivi_formation_tous_DT = nb_suivi_form_tous(df_formation_session_resultat_fpg, filtres_bc, 'DT_de_rattachement', target_date)

    # nb_sessions = nb_session_form(df_filtered_2025, filtres_bc, 'n_structure') => Ancienne version
    # nb_sessions_DT = nb_session_form(df_filtered_2025, filtres_bc, 'DT_de_rattachement')

    # Nouvelle version
    nb_sessions = nb_session_form(df_formation_count_session_year, filtres_bc, 'n_structure', target_date)
    nb_sessions_DT = nb_session_form(df_formation_count_session_year, filtres_bc, 'DT_de_rattachement', target_date)

    nb_structures_ma = nb_structures_menant_activite(df_formation_count_session_year, filtres_bc, 'n_structure', target_date)
    nb_structures_ma_DT = nb_structures_menant_activite(df_formation_count_session_year, filtres_bc, 'DT_de_rattachement', target_date)

    # Indicateurs fusion

    nb_actifs_solidar = nb_bene_actifs_solidar(client, df_formation_session_resultat, filtres_bc, df_ref_structure, 'n_structure', target_date)
    nb_actifs_solidar_DT = nb_bene_actifs_solidar(client, df_formation_session_resultat, filtres_bc, df_ref_structure, 'DT_de_rattachement', target_date)

    df_nvx_forme_crb = nb_nvx_forme_crb(client, df_filtered_year, filtres_bc, 'n_structure', target_date)
    df_nvx_forme_crb_DT = nb_nvx_forme_crb(client, df_filtered_year, filtres_bc, 'DT_de_rattachement', target_date)

    indicateurs_base_contact_pd, indicateurs_base_contact_DT_pd = fusion_bc_final(
      df_ref_structure['n_structure'].drop_duplicates().to_frame(),df_ref_structure[df_ref_structure['type_structure'] == "DELEGATION TERRITORIALE - DT"]['n_structure'].astype(str).drop_duplicates().to_frame(),
        nb_bene_suivi_formation, nb_bene_suivi_formation_DT,
        nb_suivi_formation, nb_suivi_formation_DT,
        nb_suivi_formation_tous, nb_suivi_formation_tous_DT,
        nb_sessions, nb_sessions_DT,
        nb_actifs_solidar, nb_actifs_solidar_DT,
        df_nvx_forme_crb, df_nvx_forme_crb_DT,nb_structures_ma,nb_structures_ma_DT,
        'n_structure'
    )

    indicateurs_base_contact_DT_pd = indicateurs_base_contact_DT_pd[indicateurs_base_contact_DT_pd['n_structure'] != '']

    return indicateurs_base_contact_pd, indicateurs_base_contact_DT_pd


def correction_indic_BC_DT(df_ref_structure, indicateurs_base_contact, indicateurs_base_contact_DT, year):

    #On définit df_rattachement_structure2
    df_rattachement_structure2 = df_ref_structure[["n_structure","DT_de_rattachement"]]

    #On merge indic base contact avec rattachement structure
    indicateurs_base_contact_2= indicateurs_base_contact.merge(df_rattachement_structure2, on="n_structure", how="left")

    #On enlève le siège
    indicateurs_base_contact_2 = indicateurs_base_contact_2[~indicateurs_base_contact_2["DT_de_rattachement"].isna()]

    #On ne conserve que les indicateurs qui nous intéressent
    indicateurs_base_contact_2 = indicateurs_base_contact_2[['DT_de_rattachement',f"Formation_grand_public Nb_formes_PSC_{year}",
    f"Formation_grand_public Nb_formes_GQS_{year}",
    f"Formation_grand_public Nb_formes_IPS_{year}",
    f"Formation_grand_public Nb_formes_IPSEN_{year}"]]



    #Groupby par structure de rattachement
    indicateurs_base_contact_2 = (
        indicateurs_base_contact_2
        .groupby("DT_de_rattachement")
        .sum()
        .reset_index()
    )

    #Passage en Int pour les 4 indicateurs
    cols_to_int = [
        f"Formation_grand_public Nb_formes_PSC_{year}",
        f"Formation_grand_public Nb_formes_GQS_{year}",
        f"Formation_grand_public Nb_formes_IPS_{year}",
        f"Formation_grand_public Nb_formes_IPSEN_{year}"
    ]

    indicateurs_base_contact_2[cols_to_int] = (
        indicateurs_base_contact_2[cols_to_int]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
        .astype(int)
    )

    #On comment les 4 indicateurs différents
    indicateurs_base_contact_DT= indicateurs_base_contact_DT[['n_structure', 'AEO Nb_AAD',
          f'Dispositifs_d_urgence Nb_formes_TCAU_{year}',
          f'Dispositifs_d_urgence Nb_formes_TCEO_{year}',
          f'Dispositifs_d_urgence Nb_formes_PSP_{year}',
          f'Dispositifs_d_urgence Nb_formes_IRR_{year}',
          f'Dispositifs_d_urgence Nb_formes_GQS_{year}',
          f'Structure Nb_formes_CRB_{year}', 'Maraude Nb_SOLIDAR',
          'Maraude Nb_SOLIDAR2020', 'AEO Nb_FAAD',
          f'Structure Nb_formateurs_CRB_{year}', f'Structure Nb_formes_TCAS_{year}',
          #f'Formation_grand_public Nb_formes_PSC_{year}',
          #f'Formation_grand_public Nb_formes_GQS_{year}',
          #f'Formation_grand_public Nb_formes_IPS_{year}',
          #f'Formation_grand_public Nb_formes_IPSEN_{year}',
          f'Formation_grand_public Nb_formes_PREVIC_{year}',
          f'Formation_grand_public Nb_sessions_PSC_{year}',
          f'Formation_grand_public Nb_sessions_GQS_{year}',
          f'Formation_grand_public Nb_sessions_IPS_{year}',
          f'Formation_grand_public Nb_sessions_IPSEN_{year}',
          f'Formation_grand_public Nb_sessions_PREVIC_{year}',
          'Secours Nb_sessions_PSE', 'Secours Nb_sessions_CI',
          'Secours Nb_sessions_FPSE',
          'Maraude Nb_benevoles_actifs_formes',
          f'Structure Nb_nvx_formes_CRB_{year}',
          'Dispositifs_d_urgence Structures_menant_activite_TCAU',
          'Dispositifs_d_urgence Structures_menant_activite_PSP',
          'Dispositifs_d_urgence Structures_menant_activite_GQS',
          'Aide_alimentaire nb_ASAH', 'Aide_alimentaire nb_SAH',
          'Textile Animateurs_textile']].copy()

    indicateurs_base_contact_DT['n_structure'] = pd.to_numeric(indicateurs_base_contact_DT['n_structure'], errors='coerce').fillna(0).astype(int)
    indicateurs_base_contact_DT = indicateurs_base_contact_DT.merge(df_rattachement_structure2, on="n_structure", how="left").copy()

    indicateurs_base_contact_DT = pd.merge(indicateurs_base_contact_DT, indicateurs_base_contact_2, on="DT_de_rattachement")
    indicateurs_base_contact_DT = indicateurs_base_contact_DT.drop(columns="DT_de_rattachement")

    return indicateurs_base_contact_DT
