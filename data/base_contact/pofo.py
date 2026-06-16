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
    df_return = df.merge(
        df_ref_structure[['n_structure', 'DT_de_rattachement']].drop_duplicates(),
        on='n_structure',
        how='left'
    )
    df_return['DT_de_rattachement'] = df_return['DT_de_rattachement'].apply(lambda x: keep_integer(x))
    return df_return

def flatten(xss):
    return [x for xs in xss for x in xs]

def calcul_secours_par_annee(df, filtres_bc, target_date):

    # ======================
    # Filtre unique optimisé
    # Permet de faire la différence entre PSE1, PSE2 et CI comme il y a intersection entre ces différents ensembles (concrètement : CI => PSE1 ^ PSE2 et PSE2 => PSE1)
    # ======================
    target = pd.Timestamp(target_date)
    year = target.year
    mask = (
        (df['FORMATION_RESULTAT'] == 'Apte') &
        (df['DATE_FILTRE'] >= target)
    )

    df_year = df.loc[mask, ['FORMATION_CODE', 'NIVOL_ID_FK']]

    # ======================
    # Sets de codes
    # ======================
    codes_ci = set(filtres_bc['CI'])
    codes_pse2 = set(filtres_bc['PSE2'])
    codes_pse1 = set(filtres_bc['PSE1'])
    codes_fpse = set(filtres_bc['FPSE'])

    # ======================
    # Extraction rapide
    # ======================
    nivols_fpse = set(
        df_year.loc[df_year['FORMATION_CODE'].isin(codes_fpse), 'NIVOL_ID_FK']
    )

    nivols_ci = set(
        df_year.loc[df_year['FORMATION_CODE'].isin(codes_ci), 'NIVOL_ID_FK']
    )

    nivols_pse2 = set(
        df_year.loc[df_year['FORMATION_CODE'].isin(codes_pse2), 'NIVOL_ID_FK']
    )

    nivols_pse1 = set(
        df_year.loc[df_year['FORMATION_CODE'].isin(codes_pse1), 'NIVOL_ID_FK']
    )

    # ======================
    # Hiérarchie logique
    # ======================
    nivols_pse2 -= nivols_fpse
    nivols_pse2 -= nivols_ci

    nivols_pse1 -= nivols_fpse
    nivols_pse1 -= nivols_ci
    nivols_pse1 -= nivols_pse2

    # ======================
    # Résultat
    # ======================
    return {
        "LISTE_FPSE": list(nivols_fpse),
        "LISTE_CI": list(nivols_ci),
        "LISTE_PSE2": list(nivols_pse2),
        "LISTE_PSE1": list(nivols_pse1)
    }

# ------------------------------
# Fonctions indicateurs
# ------------------------------

def nb_bene_aptes_PSE1_2_CI(df, filtres_bc, col_groupby, target_date):
    """
    Nombre de bénévoles secouristes (aptitudes PSE1, PSE2 et CI)
    """
    target = pd.Timestamp(target_date)
    year = target.year
    # ======================
    # Filtre principal
    # ======================
    df_res = df[
        (df['FORMATION_RESULTAT'] == 'Apte') &
        (df['DATE_FILTRE'] >= target)
    ].copy()

    df_res = df_res[
        df_res['FORMATION_CODE'].isin(
            filtres_bc['PSE1'] + filtres_bc['PSE2'] + filtres_bc['CI'] + filtres_bc['FPSE']
        )
    ]

    # ======================
    # Calcul hiérarchie secours
    # ======================
    nivols = calcul_secours_par_annee(df_res, filtres_bc, target)

    set_pse1 = set(nivols['LISTE_PSE1'])
    set_pse2 = set(nivols['LISTE_PSE2'])
    set_ci = set(nivols['LISTE_CI'])
    set_fpse = set(nivols['LISTE_FPSE'])

    # ======================
    # Colonnes indicateurs
    # ======================
    df_res['Secours Nb_PSE1'] = (
        df_res['FORMATION_CODE'].isin(filtres_bc['PSE1']) &
        df_res['NIVOL_ID_FK'].isin(set_pse1)
    )

    df_res['Secours Nb_PSE2'] = (
        df_res['FORMATION_CODE'].isin(filtres_bc['PSE2']) &
        df_res['NIVOL_ID_FK'].isin(set_pse2)
    )

    df_res['Secours Nb_CI'] = (
        df_res['FORMATION_CODE'].isin(filtres_bc['CI']) &
        df_res['NIVOL_ID_FK'].isin(set_ci)
    )

    df_res['Secours Nb_FPSE'] = (
        df_res['FORMATION_CODE'].isin(filtres_bc['FPSE']) &
        df_res['NIVOL_ID_FK'].isin(set_fpse)
    )

    # ======================
    # Vérification des codes
    # ======================
    print("\n===== Vérification des codes =====")

    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in [
        ('Secours Nb_PSE1', 'PSE1'),
        ('Secours Nb_PSE2', 'PSE2'),
        ('Secours Nb_CI', 'CI'),
        ('Secours Nb_FPSE', 'FPSE')
    ]:

        codes_attendus = set(filtres_bc.get(code, []))
        codes_trouves = codes_df.intersection(codes_attendus)
        codes_manquants = codes_attendus - codes_df

        print(f"\nIndicateur : {name}")
        print(f"  Codes attendus : {codes_attendus}")
        print(f"  Codes trouvés  : {codes_trouves}")
        print(f"  Codes manquants: {codes_manquants}")

    # ======================
    # Comptage optimisé
    # ======================
    def count_unique(df, mask):
        return df.loc[mask, 'NIVOL_ID_FK'].nunique()

    result = (
        df_res
        .groupby(col_groupby)
        .apply(lambda g: pd.Series({
            'Secours Nb_PSE1': count_unique(g, g['Secours Nb_PSE1']),
            'Secours Nb_PSE2': count_unique(g, g['Secours Nb_PSE2']),
            'Secours Nb_CI': count_unique(g, g['Secours Nb_CI']),
            'Secours Nb_FPSE': count_unique(g, g['Secours Nb_FPSE'])
        }))
        .reset_index()
    )

    # ======================
    # Somme globale
    # ======================
    print("\n===== Somme globale par indicateur =====")

    totaux = result[
        ['Secours Nb_PSE1', 'Secours Nb_PSE2', 'Secours Nb_CI', 'Secours Nb_FPSE']
    ].sum()

    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

    result['Secours Nb_IS'] = result['Secours Nb_PSE1'] + result['Secours Nb_PSE2']

    return result


def nb_bene_aptes_autres(df, filtres_bc, col_groupby, target_date):
    """
    Nombre de personnes aptes aux formations

    Enlever les nivols AGQS et FIPSEN de FPSC, et enlever nivols FPS de AGQS FIPSEN et FPSC
    """
    target = pd.Timestamp(target_date)
    year = target.year
    df_res = df[(df['FORMATION_RESULTAT'] == 'Apte') & (df['DATE_FILTRE'] >= target)].copy()

    # Identifier les NIVOLs à exclure
    fps_nivols = set(df_res[df_res['FORMATION_CODE'].isin(filtres_bc['FPS'])]['NIVOL_ID_FK'])
    fpsc_nivols = set(df_res[df_res['FORMATION_CODE'].isin(filtres_bc['FPSC'])]['NIVOL_ID_FK'])
    agqs_nivols = set(df_res[df_res['FORMATION_CODE'].isin(filtres_bc['AGQS'])]['NIVOL_ID_FK'])
    fipsen_nivols = set(df_res[df_res['FORMATION_CODE'].isin(filtres_bc['FIPSEN'])]['NIVOL_ID_FK'])

    for name, code in [('Formation_grand_public Nb_FPSC', 'FPSC'),
                       ('Formation_grand_public Nb_AGQS', 'AGQS'),
                       ('Formation_grand_public Nb_FIPSEN', 'FIPSEN')]:
        df_res[name] = df_res['FORMATION_CODE'].isin(filtres_bc[code])

    # Vérification des codes
    print("\n===== Vérification des codes =====")
    codes_df = set(df_res['FORMATION_CODE'].unique())

    for name, code in [('Formation_grand_public Nb_FPSC', 'FPSC'),
                       ('Formation_grand_public Nb_AGQS', 'AGQS'),
                       ('Formation_grand_public Nb_FIPSEN', 'FIPSEN')]:
        codes_attendus = set(filtres_bc.get(code, []))
        codes_trouves = codes_df.intersection(codes_attendus)
        codes_manquants = codes_attendus - codes_df

        print(f"\nIndicateur : {name}")
        print(f"  Codes attendus : {codes_attendus}")
        print(f"  Codes trouvés  : {codes_trouves}")
        print(f"  Codes manquants: {codes_manquants}")

        df_res[name] = df_res['FORMATION_CODE'].isin(codes_attendus)

    # Appliquer les exclusions
    df_res['Formation_grand_public Nb_FPSC'] = df_res['Formation_grand_public Nb_FPSC'] & (~df_res['NIVOL_ID_FK'].isin(fps_nivols)) & (~df_res['NIVOL_ID_FK'].isin(agqs_nivols)) & (~df_res['NIVOL_ID_FK'].isin(fipsen_nivols))
    df_res['Formation_grand_public Nb_AGQS'] = df_res['Formation_grand_public Nb_AGQS'] & (~df_res['NIVOL_ID_FK'].isin(fps_nivols)) & (~df_res['NIVOL_ID_FK'].isin(fpsc_nivols))
    df_res['Formation_grand_public Nb_FIPSEN'] = df_res['Formation_grand_public Nb_FIPSEN'] & (~df_res['NIVOL_ID_FK'].isin(fps_nivols)) & (~df_res['NIVOL_ID_FK'].isin(fpsc_nivols))

    # Fonction de comptage
    def count_unique(group, col_name):
        return group.loc[group[col_name], 'NIVOL_ID_FK'].nunique()

    result = df_res.groupby(col_groupby).apply(
        lambda g: pd.Series({col: count_unique(g, col) for col in ['Formation_grand_public Nb_FPSC',
                                                                  'Formation_grand_public Nb_AGQS',
                                                                  'Formation_grand_public Nb_FIPSEN']})
    ).reset_index()

    # Somme globale par indicateur
    print("\n===== Somme globale par indicateur =====")
    totaux = result[[col for col, _ in [('Formation_grand_public Nb_FPSC', 'FPSC'),
                       ('Formation_grand_public Nb_AGQS', 'AGQS'),
                       ('Formation_grand_public Nb_FIPSEN', 'FIPSEN')]]].sum()

    for col in totaux.index:
        print(f"{col} : {totaux[col]}")

    return result


# ------------------------------
# Fonctions taux
# ------------------------------

def taux_recy(df_filtered, df_nb_aptes, filtres_bc, col_groupby, target_date):
    """
    Taux de recyclage PSE1, PSE2 et CI pour 2026 (seront aptes en 2026 grâce au recyclage)
    """
    target = pd.Timestamp(target_date)
    year = target.year
    df_res = df_filtered[df_filtered['FORMATION_RESULTAT'] == 'Apte'].copy()
    result = pd.DataFrame({col_groupby: df_res[col_groupby].unique()})
    result.set_index(col_groupby, inplace=True)

    nivols = calcul_secours_par_annee(df_res, filtres_bc, target_date)

    set_pse1 = set(nivols['LISTE_PSE1'])
    set_pse2 = set(nivols['LISTE_PSE2'])
    set_ci = set(nivols['LISTE_CI'])
    set_fpse = set(nivols['LISTE_FPSE'])


    mask = (
        (df_res['FORMATION_CODE'].isin(filtres_bc['PSE1']) & df_res['NIVOL_ID_FK'].isin(set_pse1)) |
        (df_res['FORMATION_CODE'].isin(filtres_bc['PSE2']) & df_res['NIVOL_ID_FK'].isin(set_pse2)) |
        (df_res['FORMATION_CODE'].isin(filtres_bc['CI']) & df_res['NIVOL_ID_FK'].isin(set_ci)) |
        (df_res['FORMATION_CODE'].isin(filtres_bc['FPSE']) & df_res['NIVOL_ID_FK'].isin(set_fpse))
    )

    df_res = df_res.loc[mask]

    for code, alias in [('RECPSE1', 'nb_recy_PSE1'),
                        ('RECPSE2', 'nb_recy_PSE2'),
                        ('RECCI', 'nb_recy_CI'),
                        ('RECFPSE', 'nb_recy_FPSE')]:
        taux = df_res.groupby(col_groupby).apply(
            lambda g: g[
                (g['FORMATION_CODE'].isin(filtres_bc[code])) &
                (g['DATE_FILTRE'].dt.year == year + 1)
            ]['NIVOL_ID_FK'].nunique()
        )
        result[alias] = taux

    result = pd.merge(result, df_nb_aptes, on = col_groupby, how = 'outer')

    for code, nb, alias in [('PSE1','Secours Nb_PSE1', f'Secours Taux_recy{year+1-2000}_PSE1'),
                        ('PSE2', 'Secours Nb_PSE2', f'Secours Taux_recy{year+1-2000}_PSE2'),
                        ('CI','Secours Nb_CI', f'Secours Taux_recy{year+1-2000}_CI'),
                        ('FPSE','Secours Nb_FPSE', f'Secours Taux_recy{year+1-2000}_FPSE')]:
        mask = result[nb] < result['nb_recy_'+code]
        print(f"nb_recy_{code} : {result['nb_recy_'+code].sum()}")


        if mask.any():
            lignes_erreur = result[mask][['nb_recy_'+code,nb]]
            print(f"{mask.sum()} ligne(s) ont {nb} < nb_recy_{code} :\n{lignes_erreur}")
        ratio = np.where(
          (result['nb_recy_'+code] == 0) | (result[nb] == 0),
          0,  # si l'un des deux est 0
          result['nb_recy_'+code] / result[nb]  # sinon le calcul normal
        )
        result[alias] = np.minimum(ratio, 1)


    result = result.reset_index()
    return result[[col_groupby, f'Secours Taux_recy{year+1-2000}_PSE1', f'Secours Taux_recy{year+1-2000}_PSE2', f'Secours Taux_recy{year+1-2000}_CI', f'Secours Taux_recy{year+1-2000}_FPSE']]

def taux_ren(df_filtered, df_nb_aptes, filtres_bc, col_groupby, target_date):
    """
    Taux de nouveaux PSE1, PSE2 et CI en 2025 (formation initiale en *annee*)
    """
    target = pd.Timestamp(target_date)
    year = target.year
    df_res = df_filtered[df_filtered['FORMATION_RESULTAT'] == 'Apte'].copy()
    result = pd.DataFrame({col_groupby: df_res[col_groupby].unique()})
    result.set_index(col_groupby, inplace=True)

    nivols = calcul_secours_par_annee(df_res, filtres_bc, target_date)

    set_pse1 = set(nivols['LISTE_PSE1'])
    set_pse2 = set(nivols['LISTE_PSE2'])
    set_ci = set(nivols['LISTE_CI'])
    set_fpse = set(nivols['LISTE_FPSE'])


    mask = (
        (df_res['FORMATION_CODE'].isin(filtres_bc['PSE1']) & df_res['NIVOL_ID_FK'].isin(set_pse1)) |
        (df_res['FORMATION_CODE'].isin(filtres_bc['PSE2']) & df_res['NIVOL_ID_FK'].isin(set_pse2)) |
        (df_res['FORMATION_CODE'].isin(filtres_bc['CI']) & df_res['NIVOL_ID_FK'].isin(set_ci)) |
        (df_res['FORMATION_CODE'].isin(filtres_bc['FPSE']) & df_res['NIVOL_ID_FK'].isin(set_fpse))
    )

    df_res = df_res.loc[mask]

    for code, alias in [('PSE1_i', 'nb_ren_PSE1'),
                        ('PSE2_i', 'nb_ren_PSE2'),
                        ('CI_i', 'nb_ren_CI'),
                        ('FPSE_i', 'nb_ren_FPSE')]:
        taux = df_res.groupby(col_groupby).apply(
            lambda g: g[
                g['FORMATION_CODE'].isin(filtres_bc[code]) &
                (g['DATE_FILTRE'].dt.year == year + 1)
            ]['NIVOL_ID_FK'].nunique()
        )
        result[alias] = taux

    result = pd.merge(result, df_nb_aptes, on = col_groupby, how = 'outer')

    for code, nb, alias in [('PSE1','Secours Nb_PSE1', f'Secours Taux_ren{year-2000}_PSE1'),
                        ('PSE2', 'Secours Nb_PSE2', f'Secours Taux_ren{year-2000}_PSE2'),
                        ('CI','Secours Nb_CI', f'Secours Taux_ren{year-2000}_CI'),
                        ('FPSE','Secours Nb_FPSE', f'Secours Taux_ren{year-2000}_FPSE')]:
        mask = result[nb] < result['nb_ren_'+code]
        print(f"nb_ren_{code} : {result['nb_ren_'+code].sum()}")

        if mask.any():
            lignes_erreur = result[mask][['nb_ren_'+code,nb]]
            print(f"{mask.sum()} ligne(s) ont {nb} < nb_recy_{code} :\n{lignes_erreur}")
        ratio = np.where(
          (result['nb_ren_'+code] == 0) | (result[nb] == 0),
          0,  # si l'un des deux est 0
          result['nb_ren_'+code] / result[nb]  # sinon le calcul normal
        )
        result[alias] = np.minimum(ratio, 1)

    result = result.reset_index()
    return result[[col_groupby, f'Secours Taux_ren{year-2000}_PSE1', f'Secours Taux_ren{year-2000}_PSE2', f'Secours Taux_ren{year-2000}_CI', f'Secours Taux_ren{year-2000}_FPSE']]

def taux_IS(client, df, filtres_bc, df_ref_structure, col_groupby, target_date = '2025-12-31'):
    """
    Taux d'intervenants secouristes (IS) i.e. sont formés PSE1 ou PSE2 ou CI; qui sont actifs dans pegass
    Numérateur : Nombre d'IS actifs dans pegass en 2025 (également présents dans l'ensemble PSE1, PSE2, CI 2024, 2025 de base contact formation_session_resultat, la raison pour cela étant qu'il est possible qu'il y ai des activités secouristes menée par des gens qui ne sont pas dans la base contact)
    Dénominateur : Nombre de PSE1, PSE2 et CI aptes en 2025 (donc formés 2024-2025)

    On enlève tous les nivols absents au 31-12-2025 dans pegass, même s'ils ont fait une activité en 2025
    """

    target = pd.Timestamp(target_date)
    year = target.year
    # Utiliser
    query_is = f"""WITH codes_actifs AS (
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
                          FROM `crf-pat.dataset_PAT_{year}.crf_pat_{year}_pegass_activite` AS act
                          INNER JOIN `crf-pat.dataset_PAT_{year}.crf_pat_{year}_pegass_activite_seance_inscription` AS insc
                              ON act.PEGASS_ACTIVITE_ID_PK = insc.PEGASS_ACTIVITE_ID_FK
                          WHERE act.ACTIVITE_BENEVOLE_ID_FK IN (SELECT code FROM codes_actifs) AND insc.PEGASS_ACTIVITE_SEANCE_INSCRIPTION_STATUT = 'Valide'
                            AND PEGASS_ACTIVITE_DATE_DEBUT >= DATE('{year}-01-01') AND PEGASS_ACTIVITE_DATE_DEBUT <= DATE('{target_date}')"""

    filtres_bc['IS'] = filtres_bc['PSE1'] + filtres_bc['PSE2']


    df_is = client.query(query_is).to_dataframe()
    df_is = df_is.rename(columns = {'PEGASS_ACTIVITE_SEANCE_INSCRIPTION_NIVOL_ID_FK' : 'NIVOL_ID_FK'})[['PEGASS_ACTIVITE_STRUCTURE_MENANT_ACTIVITE_ID_FK','NIVOL_ID_FK']].drop_duplicates()

    df_res = df[(df['FORMATION_RESULTAT'] == 'Apte')].copy()

    # df_res = df_res[(df_res['FORMATION_DATE_OBTENTION'].dt.year == 2025) | (df_res['FORMATION_DATE_OBTENTION'].dt.year == 2024)]


    df_res = df_res[(df_res['DATE_FILTRE'] >= target)]

    df_res = df_res[df_res['FORMATION_CODE'].isin(filtres_bc['IS'])]

    df_res = df_res.drop('DT_de_rattachement', axis = 1)
    df_is = pd.merge(df_res, df_is, on = 'NIVOL_ID_FK', how = 'inner')

    df_res = dt_rattachement(df_res, df_ref_structure)
    df_is = dt_rattachement(df_is, df_ref_structure)


    df_res = df_res.drop_duplicates([col_groupby,'NIVOL_ID_FK'])
    df_is = df_is.drop_duplicates([col_groupby,'NIVOL_ID_FK'])


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
      0,
      result["nb_bene_actifs"] / result["Nb_IS"]
    )
    mask = result["Nb_IS"] < result["nb_bene_actifs"]

    if mask.any():
        lignes_erreur = result[mask]
        print(
            f"{mask.sum()} ligne(s) ont Nb_IS < nb_bene_actifs :\n{lignes_erreur}"
        )
    return result[[col_groupby, "Secours Taux_IS_actifs"]]

# ------------------------------
# Fusion
# ------------------------------

def fusion_pofo_final(df_ref_structure, df_ref_structure_DT,
                    nb_apte_formation_PSE1_2_CI, nb_apte_formation_PSE1_2_CI_DT,
                    nb_apte_formation, nb_apte_formation_DT,
                    taux_rec, taux_rec_DT,
                    taux_nouveau_form, taux_nouveau_form_DT,
                    taux_is_actifs, taux_is_actifs_DT,
                    col_groupby):

    """
    Cette fonction permet de fusionner tous les dataframes en un, on utilise df_ref_structure comme référence et on fait un left join dessus pour avoir exactement les mêmes structures
    """
    # Fusion des DataFrames
    def merge_all(dfs):
        from functools import reduce
        return reduce(lambda left, right: left.merge(right, on=col_groupby, how='left'), dfs)

    indicateurs_base_contact = merge_all([df_ref_structure,
                                         nb_apte_formation_PSE1_2_CI,
                                         nb_apte_formation,
                                         taux_rec,
                                         taux_nouveau_form,taux_is_actifs])

    # Même pour DT
    for df in [nb_apte_formation_PSE1_2_CI_DT,
               nb_apte_formation_DT, taux_rec_DT, taux_nouveau_form_DT,taux_is_actifs_DT]:
        df.rename(columns={'DT_de_rattachement': 'n_structure'}, inplace=True)

    indicateurs_base_contact_DT = merge_all([df_ref_structure_DT,
                                            nb_apte_formation_PSE1_2_CI_DT,
                                            nb_apte_formation_DT,
                                            taux_rec_DT,
                                            taux_nouveau_form_DT,taux_is_actifs_DT])

    return indicateurs_base_contact, indicateurs_base_contact_DT


# ------------------------------
# Fonction principale
# ------------------------------

def clean_pofo(client, df_ref_structure, target_date="2025-12-31", half_year = False):
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

    year_gap = 1
    if half_year:
        year_gap = 2

    if year < 2025:
        bdd_year = 2025

    codes_filtres_bc = list({element for sous_liste in filtres_bc.values() for element in sous_liste})

    query_formation_session_resultat = f"""
        SELECT * FROM `crf-pat.dataset_PAT_2026.crf_pat_2026_formation_session_resultat`
        """ # On ne change pas le dataset car 2026 est supposé être mis à jour régulièrement, devra peut-être être changé ultérieurement
    df_formation_session_resultat = client.query(query_formation_session_resultat).to_dataframe()

    df_formation_session_resultat['FORMATION_DATE_OBTENTION'] = pd.to_datetime(df_formation_session_resultat['FORMATION_DATE_OBTENTION'], errors='coerce')
    df_formation_session_resultat['FORMATION_DATE_RECYCLAGE'] = pd.to_datetime(df_formation_session_resultat['FORMATION_DATE_RECYCLAGE'], errors='coerce')

    df_formation_session_resultat = df_formation_session_resultat[df_formation_session_resultat["FORMATION_CODE"].isin(codes_filtres_bc)]


    # dataframe date recyclage 
    df_formation_session_resultat_IS = df_formation_session_resultat.copy()

    df_formation_session_resultat_IS = df_formation_session_resultat_IS[(df_formation_session_resultat_IS['FORMATION_DATE_RECYCLAGE'].dt.year < year + year_gap) | (df_formation_session_resultat_IS['FORMATION_DATE_RECYCLAGE'].isna())]

    # Création de DATE_FILTRE
    df_formation_session_resultat_IS["DATE_FILTRE"] = df_formation_session_resultat_IS["FORMATION_DATE_RECYCLAGE"]

    # Si recyclage est nul :
    # année de FORMATION_DATE_OBTENTION + 1
    # date fixée au 31 décembre
    mask_recy_null = df_formation_session_resultat_IS["FORMATION_DATE_RECYCLAGE"].isna()

    df_formation_session_resultat_IS.loc[mask_recy_null, "DATE_FILTRE"] = (
        df_formation_session_resultat_IS.loc[mask_recy_null, "FORMATION_DATE_OBTENTION"]
        .apply(lambda d: pd.Timestamp(d.year + 1, 12, 31) if pd.notna(d) else pd.NaT)
    )

    # UNIQUEMENT POUR PSE1, PSE2, CI, FPSE, FPSC, AGQS, FIPSEN

    # Copier filtres_bc et supprimer des clés si nécessaire
    remove_keys = [
        # Ajoutez ici les clés à retirer de la copie, par exemple :
        "PSE1_i",
        "RECPSE1",
        "PSE2_i",
        "RECPSE2",
        "CI_i",
        "RECCI",
        "FPSE_i",
        "RECFPSE",
    ]

    filtres_bc_copy = {
        k: v.copy()
        for k, v in filtres_bc.items()
        if k not in remove_keys
    }

    # Définir le groupe de formation selon les clés de filtres_bc
    code_to_formation_group = {}
    for group_key, codes in filtres_bc_copy.items():
        for code in codes:
            if code not in code_to_formation_group:
                code_to_formation_group[code] = group_key

    df_formation_session_resultat_IS["FORMATION_GROUP"] = (
        df_formation_session_resultat_IS["FORMATION_CODE"].map(code_to_formation_group)
        .fillna(df_formation_session_resultat_IS["FORMATION_CODE"])
    )

    # UNIQUEMENT POUR PSE1, PSE2, CI, FPSE, FPSC, AGQS, FIPSEN
    # Suppression des nivol doublons
    # en conservant la ligne ayant la DATE_FILTRE la plus élevée
    df_formation_session_resultat_IS = (
        df_formation_session_resultat_IS.copy().sort_values("DATE_FILTRE")
        .drop_duplicates(subset=["NIVOL_ID_FK","FORMATION_GROUP"], keep="last")
        .reset_index(drop=True)
    )



    query_rattachement_benevole = f"""
        SELECT *
        FROM `crf-pat.dataset_PAT_{bdd_year}.crf_pat_{bdd_year}_rattachement_benevole`
        """

        #SELECT rattachement_benevole_nivol_id_fk, rattachement_benevole_structure_id_fk

    df_rattachement_benevole = client.query(query_rattachement_benevole).to_dataframe()
    liste_structure_garder = df_ref_structure['n_structure'].drop_duplicates().to_list()

    df_rattachement_benevole = df_rattachement_benevole[df_rattachement_benevole['rattachement_benevole_structure_id_fk'].isin(liste_structure_garder)]
    df_rattachement_benevole["rattachement_benevole_date_fin"] = pd.to_datetime(df_rattachement_benevole["rattachement_benevole_date_fin"])

    df_rattachement_benevole["rattachement_benevole_date_debut"] = pd.to_datetime(
    df_rattachement_benevole["rattachement_benevole_date_debut"],
    errors="coerce"
    )

    df_rattachement_benevole = df_rattachement_benevole.loc[
        ~(df_rattachement_benevole["rattachement_benevole_date_fin"] < target) | ~(df_rattachement_benevole["rattachement_benevole_date_debut"]  > target)
    ]
    
    df_rattachement_benevole = (
        df_rattachement_benevole
        .sort_values("rattachement_benevole_date_debut", ascending=False)
        .drop_duplicates(subset="rattachement_benevole_nivol_id_fk", keep="first")
        .copy()
    )

    df_rattachement_benevole = df_rattachement_benevole.drop_duplicates("rattachement_benevole_nivol_id_fk")
    
    df_rattachement_benevole = df_rattachement_benevole[["rattachement_benevole_nivol_id_fk","rattachement_benevole_structure_id_fk"]]


    df_formation_session_resultat_IS = pd.merge(
        df_formation_session_resultat_IS,
        df_rattachement_benevole,
        left_on="NIVOL_ID_FK",
        right_on="rattachement_benevole_nivol_id_fk",
        how="left"
    )

    df_formation_session_resultat_IS = df_formation_session_resultat_IS.rename(columns={"rattachement_benevole_structure_id_fk": "n_structure"})
    df_formation_session_resultat_IS = apply_rattachement_successif(df_ref_structure, df_formation_session_resultat_IS, col = 'n_structure')

    df_formation_session_resultat_IS = dt_rattachement(df_formation_session_resultat_IS, df_ref_structure)

    return df_formation_session_resultat_IS

def indicateurs_pofo(client, df_formation_session_resultat_IS, df_ref_structure, target_date="2025-12-31"):
    """
    Utilisation de toutes les fonctions du fichier pour calculer les indicateurs fonction par fonction.
    Les résultats sont stockés dans un dataframe différent à chaque fois, on a un calcul par structure et un par DT de rattachement pour obtenir les deux types d'agrégat.
    Tous les dataframes sont ensuite données à la fonction de fusion pour obtenir deux dataframes finaux : un par structure et un par DT, qui sont ensuite retournés 
    half_year : si les données sont calculés en milieu d'année (TRUE), on prend comme dénominateur le nombre d'apte PSE1, PSE2, CI, FPSC de 2 ans plus tôt, sinon 1 an plus tôt
    """
    target = pd.Timestamp(target_date)
    year = target.year

    df_filtered_IS = df_formation_session_resultat_IS.copy()
    df_filtered_IS = df_filtered_IS[df_filtered_IS['FORMATION_CODE'].isin(flatten(list(filtres_bc.values())))]

    # Calculs indicateurs
    nb_apte_formation_PSE1_2_CI = nb_bene_aptes_PSE1_2_CI(df_filtered_IS, filtres_bc, 'n_structure', target_date)
    nb_apte_formation_PSE1_2_CI_DT = nb_bene_aptes_PSE1_2_CI(df_filtered_IS, filtres_bc, 'DT_de_rattachement', target_date)

    nb_apte_formation = nb_bene_aptes_autres(df_filtered_IS, filtres_bc, 'n_structure', target_date)
    nb_apte_formation_DT = nb_bene_aptes_autres(df_filtered_IS, filtres_bc, 'DT_de_rattachement', target_date)

    # Pour calculer le taux de recyclage et le taux de renouvellement, on a besoin du nombre de personnes aptes à 
    # la formation PSE1, PSE2, CI en 2024, pour cela on refait les mêmes calculs mais en filtrant sur
    #  les formations obtenues l'année précédente au 31-12
    year_gap = 1

    date_31122025 = datetime(year - year_gap, 12, 31)
    df_formation_session_resultat_IS_prev = clean_pofo(client, df_ref_structure, target_date=f"{year - year_gap}-12-31")
    df_filtered_prev = df_formation_session_resultat_IS_prev.copy()
    df_filtered_prev = df_filtered_prev[df_filtered_prev['FORMATION_CODE'].isin(flatten(list(filtres_bc.values())))]

    nb_apte_formation_PSE1_2_CI_prev = nb_bene_aptes_PSE1_2_CI(df_filtered_prev, filtres_bc, 'n_structure', date_31122025)
    nb_apte_formation_PSE1_2_CI_DT_prev = nb_bene_aptes_PSE1_2_CI(df_filtered_prev, filtres_bc, 'DT_de_rattachement', date_31122025)

    taux_rec = taux_recy(df_filtered_IS, nb_apte_formation_PSE1_2_CI_prev, filtres_bc, 'n_structure', target_date)
    taux_rec_DT = taux_recy(df_filtered_IS, nb_apte_formation_PSE1_2_CI_DT_prev, filtres_bc, 'DT_de_rattachement', target_date)

    taux_nouveau_form = taux_ren(df_filtered_IS, nb_apte_formation_PSE1_2_CI_prev, filtres_bc, 'n_structure', target_date)
    taux_nouveau_form_DT = taux_ren(df_filtered_IS, nb_apte_formation_PSE1_2_CI_DT_prev, filtres_bc, 'DT_de_rattachement', target_date)

    taux_is_actifs = taux_IS(client, df_filtered_IS, filtres_bc, df_ref_structure, 'n_structure', target_date)
    taux_is_actifs_DT = taux_IS(client, df_filtered_IS, filtres_bc, df_ref_structure, 'DT_de_rattachement', target_date)

    indicateurs_base_contact_pd, indicateurs_base_contact_DT_pd = fusion_pofo_final(
      df_ref_structure['n_structure'].drop_duplicates().to_frame(),
      df_ref_structure[df_ref_structure['type_structure'] == "DELEGATION TERRITORIALE - DT"]['n_structure'].astype(str).drop_duplicates().to_frame(),
        nb_apte_formation_PSE1_2_CI, nb_apte_formation_PSE1_2_CI_DT,
        nb_apte_formation, nb_apte_formation_DT,
        taux_rec, taux_rec_DT,
        taux_nouveau_form, taux_nouveau_form_DT,
        taux_is_actifs, taux_is_actifs_DT,
        'n_structure'
    )

    indicateurs_base_contact_DT_pd = indicateurs_base_contact_DT_pd[indicateurs_base_contact_DT_pd['n_structure'] != '']

    return indicateurs_base_contact_pd, indicateurs_base_contact_DT_pd


def correction_indic_pofo_DT(df_ref_structure, indicateurs_base_contact, indicateurs_base_contact_DT, year):


    indicateurs_base_contact_DT['n_structure'] = indicateurs_base_contact_DT['n_structure'].astype(int)
    #On définit df_rattachement_structure2
    df_rattachement_structure2 = df_ref_structure[["n_structure","DT_de_rattachement"]].drop_duplicates()

    #On merge indic base contact avec rattachement structure
    indicateurs_base_contact_2= indicateurs_base_contact.merge(df_rattachement_structure2, on="n_structure", how="left")

    #On enlève le siège
    indicateurs_base_contact_2 = indicateurs_base_contact_2[~indicateurs_base_contact_2["DT_de_rattachement"].isna()]

    #Groupby par structure de rattachement
    indicateurs_base_contact_2 = (
        indicateurs_base_contact_2
        .groupby("DT_de_rattachement")
        .sum()
        .reset_index()
    )

    #Passage en Int pour les indicateurs
    cols_to_int = ['Secours Nb_PSE1', 'Secours Nb_PSE2',
        'Secours Nb_CI', 'Secours Nb_FPSE', 'Secours Nb_IS', 'Formation_grand_public Nb_FPSC',
        'Formation_grand_public Nb_AGQS', 'Formation_grand_public Nb_FIPSEN',
    ]

    indicateurs_base_contact_2[cols_to_int] = (
        indicateurs_base_contact_2[cols_to_int]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0)
        .astype(int)
    )

    indicateurs_base_contact_2 = indicateurs_base_contact_2[["DT_de_rattachement"] + cols_to_int]

    #On comment les 4 indicateurs différents
    indicateurs_base_contact_DT= indicateurs_base_contact_DT[['n_structure',#'Secours Nb_PSE1', 'Secours Nb_PSE2',
        #   'Secours Nb_CI', 'Secours Nb_FPSE', 'Secours Nb_IS', 'Formation_grand_public Nb_FPSC',
        #   'Formation_grand_public Nb_AGQS', 'Formation_grand_public Nb_FIPSEN',
          f'Secours Taux_recy{year+1-2000}_PSE1', f'Secours Taux_recy{year+1-2000}_PSE2',
          f'Secours Taux_recy{year+1-2000}_CI', f'Secours Taux_recy{year+1-2000}_FPSE', f'Secours Taux_ren{year-2000}_PSE1',
          f'Secours Taux_ren{year-2000}_PSE2', f'Secours Taux_ren{year-2000}_CI', f'Secours Taux_ren{year-2000}_FPSE', 'Secours Taux_IS_actifs']].copy()

    indicateurs_base_contact_DT['n_structure'] = pd.to_numeric(indicateurs_base_contact_DT['n_structure'], errors='coerce').fillna(0).astype(int)
    indicateurs_base_contact_DT = indicateurs_base_contact_DT.merge(df_rattachement_structure2, on="n_structure", how="left").copy()

    indicateurs_base_contact_DT = pd.merge(indicateurs_base_contact_DT, indicateurs_base_contact_2, on="DT_de_rattachement")
    indicateurs_base_contact_DT = indicateurs_base_contact_DT.drop(columns="DT_de_rattachement")

    return indicateurs_base_contact_DT