import os
import re
import pandas as pd
import numpy as np

import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *


def clean_OCR(df_OCR):
    cols_OCR = [
        "Année",
        "Statut",
        "Nom du Département",
        'Structure CRf\n(Ville)',
        "Nom Commune de l'établissement",
        "nom_structure"
    ]

    df_OCR[cols_OCR] = df_OCR[cols_OCR].astype(str)
    """
    mapping = {
    "DT46": "DT DU LOT",
    "DT64": "DT DES PYRENEES ATLANTIQUES",
    "DT22": "DT DES COTES D'ARMOR",
    "DT18": "DT DU CHER",
    "DT 28 ": "DT D'EURE ET LOIR",
    "DT 37": "DT D'INDRE ET LOIRE",
    "DT 42 ? ": "DT DE LA LOIRE",
    "DT 69": "DT DU RHONE",
    "DT 73": "DT DE LA SAVOIE",
    "DT 70": "DT DE HAUTE SAONE",
    "DT 88": "DT DES VOSGES",
    "UL de Vannes": "UL DU PAYS DE VANNES",
    "AT Haut-Allier": "AL LE HAUT ALLIER",
    "UL Villefranche sur Saône": "UL BEAUJOLAIS VALS DE SAONE",
    "UL d'Orthez": "UL DES TROIS RIVIERES",
    "Arras": "UL D'ARRAS",
    "UL de Carpentras": "UL SUD VENTOUX"
    }
  
    # Remplacer les valeurs vides (NaN ou chaînes vides)
    df_OCR['Structure CRf\n(Ville)'] = df_OCR['Structure CRf\n(Ville)'].fillna('nan')

    mask = df_OCR['Structure CRf\n(Ville)'].str.strip() == 'nan'

    df_OCR.loc[mask, 'Structure CRf\n(Ville)'] = (
        'DT ' + df_OCR.loc[mask, 'Nom du Département']
    )

    df_OCR["Structure CRf\n(Ville)"] = df_OCR["Structure CRf\n(Ville)"].replace(mapping)
    """

    return df_OCR


def clean_PST(df_PST):
    df_PST = df_PST.rename(columns={"PST constitué ": "PST constitué"})


    df_PST["N° Département"] = df_PST["Territoire"].str.extract(r"DT\s+(\d+)")
    df_PST["Nom structure DT"] = "DT " + df_PST["Territoire"].str.extract(r"-\s*(.+)")


    cols_PST = [
        "Territoire",
        "PST constitué",
        "N° Département",
        "Nom structure DT"
    ]


    df_PST[cols_PST] = df_PST[cols_PST].astype(str)


    return df_PST


def clean_declenchement(df_declenchement):
    df = df_declenchement.copy()
    df = df[df['Département concerné'] != 'NE PAS SUPPRIMER']
    df = df[df["Horodateur"] != "26/08/2025"]
    # Conversion de la date
    df['Horodateur'] = pd.to_datetime(
        df['Horodateur'],
         format='%d/%m/%Y %H:%M:%S'
    )

    # Filtre
    df_filtre = df[
        (df['Horodateur'].dt.year == 2026) &
        (df['Typologie'].isin(['Opérations', 'Fonctionnement / Sureté / Sécurité', 'Fonctionnement et vie des DT/Sûreté/Sécurité', 'Etablissements', 'Exercices']))
    ]

    df_filtre[["n_dept", "DT"]] = df_filtre["Département concerné"].str.split(" - ", expand=True)
    df_filtre["DT"] = "DT " + df_filtre["DT"]

    return df_filtre



def clean_exercices(df_declenchement):
    df = df_declenchement.copy()
    df = df[(df['Département concerné'] != 'NE PAS SUPPRIMER') & (df['Département concerné'] != 'Instances Nationales / Campus') & (df['Département concerné'] != 'Autre')]

    df = df[df["Horodateur"] != "26/08/2025"]
    # Conversion de la date
    df['Horodateur'] = pd.to_datetime(
        df['Horodateur'],
         format='%d/%m/%Y %H:%M:%S'
    )

    # Filtre
    df_filtre = df[
        (df['Horodateur'].dt.year == 2026) & (df['Typologie'].isin(['Exercice']))
    ]

    df_filtre[["n_dept", "DT"]] = df_filtre["Département concerné"].str.split(" - ", expand=True)
    df_filtre["DT"] = "DT " + df_filtre["DT"]

    return df_filtre



def clean_redcall(df_redcall):
    df = df_redcall.drop(columns=["Type", "Coûts", "Devise"])

    cols_to_sum = [
        "Déclenchements",
        "Communications",
        "Messages",
        "Questions",
        "Réponses",
        "Erreurs"
    ]

    df_grouped = (
        df
        .groupby("Nom de la structure", as_index=False)[cols_to_sum]
        .sum()
    )

    df_grouped["Total"] = df_grouped[
        ["Communications", "Messages", "Questions"]
    ].sum(axis=1)

    df_grouped["Utilisation_Redcall"] = (
        df_grouped["Total"]
        .gt(0)
        .map({True: "Oui", False: "Non"})
    )

    return df_grouped





def clean_CAIconv(df_CAICHUCMCC_conventions):

    df = df_CAICHUCMCC_conventions.copy()

    # FONCTION NORMALISATION
    def clean_departement(series):
        return (
            series
            .str.replace(
                "DELEGATION DEPARTEMENTALE",
                "DELEGATION TERRITORIALE",
                regex=False
            )
            .str.strip()
        )

    # 1. CAI / CHU / CMCC
    cols_cai = [
        'Departement',
        'Nombre de CAI (conforme guide CHU)',
        'Nombre de CHU (conforme guide CHU)',
        'Nombre Lots CMCC'
    ]

    df_cai = df[cols_cai].copy()

    # nettoyage aussi ici
    df_cai["Departement"] = clean_departement(df_cai["Departement"])

    # 2. CONVENTIONS CLEAN
    df = df.rename(columns={'Préfecture': 'Prefecture'})

    cols_conv = [
        'DT Annuaire Opé',
        'Departement',
        'Prefecture',
        'Tripartite',
        'Recherche de personnes',
        'SDIS / BMPM / BSPP',
        'SNCF',
        'SAMU',
        'Gendarmerie',
        'CUMP',
        'Communes',
        'Autoroutes',
        'Autres'
    ]

    df = df[cols_conv].copy()

    # nettoyage aussi ici
    df["Departement"] = clean_departement(df["Departement"])

    # 3. PUBLIC / PRIVÉ

    colonnes_publiques = [
        'Prefecture',
        'Tripartite',
        'Recherche de personnes',
        'SDIS / BMPM / BSPP',
        'SNCF',
        'SAMU',
        'Gendarmerie',
        'CUMP',
        'Communes'
    ]

    colonnes_oui_non = [
        'Prefecture',
        'Tripartite',
        'Recherche de personnes',
        'SDIS / BMPM / BSPP',
        'SNCF',
        'SAMU',
        'Gendarmerie',
        'CUMP',
        'Communes',
        'Autoroutes',
        'Autres'
    ]

    # remplace Oui -> 1 sinon 0 (vectorisé)
    df_bool = df[colonnes_oui_non].eq("Oui").astype(int)

    df["Dispositifs_d_urgence Nb_conventions_operateurs_publics"] = df_bool[colonnes_publiques].sum(axis=1)
    df["Dispositifs_d_urgence Nb_conventions_operateurs_prives"] = df_bool.sum(axis=1) - df["Dispositifs_d_urgence Nb_conventions_operateurs_publics"]
    df["Dispositifs_d_urgence Nb_conventions_operateurs"] = df["Dispositifs_d_urgence Nb_conventions_operateurs_prives"] + df["Dispositifs_d_urgence Nb_conventions_operateurs_publics"]

    # 4. FUSION
    df_final = df.merge(
        df_cai,
        on="Departement",
        how="left"
    )

    return df_final




def clean_raw_Textile(df_raw_Textile, df_ref_structure):
    # Filtre sur le statut
    df = df_raw_Textile[df_raw_Textile["statut"] == "A jour"]

    boutiques = [
        "Boutique - La Boutique",
        "Boutique  - Mobile",
        "Boutique - Bébé",
        "Boutique - Chez Henry",
        "Boutique - Recylcerie / Meuble",
        "La Boutique",
    ]

    vestiaires = [
        "Vestiaire"
    ]

    types_conserves = boutiques + vestiaires

    df = df[
        df["Type de point apport"].isin(types_conserves)
    ].copy()

    # VARIABLE TYPE DISPOSITIF

    df["type_dispositif_textile"] = "Autre"

    df.loc[
        df["Type de point apport"].isin(boutiques),
        "type_dispositif_textile"
    ] = "Boutique"

    df.loc[
        df["Type de point apport"].isin(vestiaires),
        "type_dispositif_textile"
    ] = "Vestiaire"

    # RATTACHEMENT STRUCTURE

    df = df.rename(
        columns={"Code structure": "n_structure"}
    )

    df = apply_rattachement_successif(
        df_ref_structure,
        df,
        col="n_structure"
    )

    return df







def clean_CR_operations(df):
    for i,col in enumerate(df.columns):
        if col[len(col)-1] == " ":
            df = df.rename(columns={col: col[:-1]})
   
    # Colonnes à conserver
    columns_to_keep = [
        "Horodateur",
        "Typologie",
        "Département concerné par l'opération ou l'exercice :",
        "DT",
        "Date et heure du début de l'opération :",
        "Date et heure de la fin de l'opération :",
        "Origine du déclenchement :",
        "Description de l'événement :",
        "Agrément concerné :",
        "Nombre de personnes accompagnées ou prises en charge :",
    ]

    # Sélection des colonnes
    df_clean = df[columns_to_keep].copy()

    # Conversion en datetime
    start_col = "Date et heure du début de l'opération :"

    df_clean[start_col] = pd.to_datetime(
        df_clean[start_col],
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce"
    )

    # Filtre année 2026
    df_clean = df_clean[df_clean[start_col].dt.year == 2026]

    # Extraction du nom du département
    dep_col = "Département concerné par l'opération ou l'exercice :"

    df_clean["Département"] = (
        df_clean[dep_col]
        .str.split(" - ", expand=True)[1]
        .str.strip()
    )

    df_clean["Num_departement"] = (
    df_clean[dep_col]
    .str.split(" - ", expand=True)[0]
    .str.strip()
    )

    return df_clean








def clean_OCR_PST_DEC_RED_CAI_CONV(
    df_OCR,
    df_PST,
    df_declenchement,
    df_CAICHUCMCC_conventions,
    df_raw_Textile,
    df_CRope,
    df_ref_structure
):
    df_OCR_clean = clean_OCR(df_OCR)
    df_PST_clean = clean_PST(df_PST)
    df_declenchement_clean = clean_declenchement(df_declenchement)
    df_exercices_clean = clean_exercices(df_declenchement)
    # df_redcall_clean = clean_redcall(df_redcall)
    df_CAIconv_clean = clean_CAIconv(df_CAICHUCMCC_conventions)
    df_raw_Textile_clean = clean_raw_Textile(df_raw_Textile, df_ref_structure)
    df_CRope_clean = clean_CR_operations(df_CRope)

    return (
        df_OCR_clean,
        df_PST_clean,
        df_declenchement_clean,
        df_exercices_clean,
        df_CAIconv_clean,
        df_raw_Textile_clean,
        df_CRope_clean
    )






def indicateurs_OCR_nb_deployees(df_OCR, df_ref_structure):
    df = df_OCR.copy()

    df = df[df["Statut"].isin(["En cours", "Projet", "Terminée"])]
    df = df[df["Année"] == "2025-2026"]

    df = df[
        ["Année", "Statut", "Nom du Département", "Numéro du Département", "nom_structure"]
    ]
    df = df.rename(columns={"nom_structure": "nom_structure_OCR"})


    # Création du dictionnaire de correspondance
    mapping_dict = (
        df_ref_structure
        .set_index("nom_structure")["n_structure"]
        .to_dict()
    )

    # Si la colonne n_structure n'existe pas encore
    if "n_structure" not in df.columns:
           df["n_structure"] = ""

    mask = df["n_structure"].eq("")

    df.loc[mask, "n_structure"] = (
            df.loc[mask, "nom_structure_OCR"]
            .map(mapping_dict)
    )

    df = (
    df.groupby("n_structure")
    .size()
    .reset_index(name="OCR Nb_deployees")
    )

    return df








def indicateurs_PST(df_PST, df_ref_structure):
    df = df_PST.copy()

    df = df[
        ["Territoire", "PST constitué", "Nom structure DT", "N° Département"]
    ]

    df = rapprochement_libelles(
        df_ref_structure,
        df,
        "Nom structure DT"
    )

    mask = df["n_structure"].isna() | (df["n_structure"] == "")

    df["N° Département"] = df["N° Département"].astype(str)
    df_ref_structure["n_dept"] = df_ref_structure["n_dept"].astype(str)

    mapping_dict = (
        df_ref_structure[
            df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"
        ]
        .set_index("n_dept")["n_structure"]
        .to_dict()
    )

    df.loc[mask, "n_structure"] = df.loc[mask, "N° Département"].map(mapping_dict)

    df["PST constitué"] = (
        df["PST constitué"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    def statut_pst(valeur):
        if valeur == "oui":
            return "Oui"
        elif valeur == "en cours":
            return "En cours"
        else:
            return "Non"


    df["Dispositifs_d_urgence PST"] = df["PST constitué"].apply(statut_pst)

    df.loc[
        df["Territoire"] == "DT  42 - Loire",
        ["n_structure", "nom_structure"]
    ] = [47, "DT DE LA LOIRE"]

    return df






def indicateurs_declenchements(df_declenchement2, df_ref_structure):
    df = df_declenchement2.copy()

    df["DT"] = df["DT"].astype(str)
    df["n_dept"] = df["n_dept"].astype(str)

    df = rapprochement_libelles(df_ref_structure[df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"], df, "DT")
    
    mask = df["n_structure"] == ""
    mapping_dict = (
        df_ref_structure[
            df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"
        ]
        .set_index("n_dept")["n_structure"]
        .to_dict()
    )

    df.loc[mask, "n_structure"] = df.loc[mask, "n_dept"].map(mapping_dict)
    
    df = df.dropna(subset=["n_structure"])

    df.loc[
        df["Département"] == "42 - Loire",
        ["n_structure", "nom_structure"]
    ] = [47, "DT DE LA LOIRE"]
    
    df = df["n_structure"].value_counts().reset_index()
    df = df.rename(columns={"count": "Dispositifs_d_urgence Nb_declenchements"})

    return df




def indicateurs_exercices(df_exercices2, df_ref_structure):
    df = df_exercices2.copy()

    df["DT"] = df["DT"].astype(str)
    df["n_dept"] = df["n_dept"].astype(str)

    df = rapprochement_libelles(df_ref_structure[df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"], df, "DT")
    
    mask = df["n_structure"] == ""
    mapping_dict = (
        df_ref_structure[
            df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"
        ]
        .set_index("n_dept")["n_structure"]
        .to_dict()
    )

    df.loc[mask, "n_structure"] = df.loc[mask, "n_dept"].map(mapping_dict)
    
    df = df.dropna(subset=["n_structure"])

    df.loc[
        df["Département"] == "42 - Loire",
        ["n_structure", "nom_structure"]
    ] = [47, "DT DE LA LOIRE"]
    
    df = df["n_structure"].value_counts().reset_index()
    df = df.rename(columns={"count": "Dispositifs_d_urgence Nb_exercices"})

    return df





def indicateurs_redcall(df_RC_grouped, df_ref_structure):
    df = df_RC_grouped[
        ["Nom de la structure", "Utilisation_Redcall"]
    ]
    df = df[~df["Nom de la structure"].isin(["ANNUAIRE NATIONAL", "REGION OCCITANIE"])]
    df['Nom de la structure'] = df['Nom de la structure'].replace('UNITE LOCALE DU BRIONNAIS', 'UNITE LOCALE DE LA CLAYETTE - MARCIGNY')
    df = df[df['Nom de la structure'] != 'INSTANCES NATIONALES']
    df["Utilisation_Redcall"] = df["Utilisation_Redcall"].astype(str)
    df = rapprochement_libelles(df_ref_structure, df, "Nom de la structure")

    df = apply_rattachement_successif(df_ref_structure, df, col = 'n_structure')

    df = df.groupby("n_structure", as_index=False).agg(
        Utilisation_Redcall=("Utilisation_Redcall", lambda s: "Oui" if (s == "Oui").any() else "")
    )

    df = df.rename(columns = {"Utilisation_Redcall" : "Dispositifs_d_urgence Utilisation_RedCall"})

    return df






def indicateurs_bilanus2025(
    df_CAICHUCMCC_conventions,
    df_ref_structure
):

    # 1. SÉLECTION COLONNES
    colonnes = [
        "Departement",
        'Nombre de CAI (conforme guide CHU)',
        'Nombre de CHU (conforme guide CHU)',
        'Nombre Lots CMCC',
        "Prefecture",
        "Dispositifs_d_urgence Nb_conventions_operateurs_publics",
        "Dispositifs_d_urgence Nb_conventions_operateurs_prives",
        "Dispositifs_d_urgence Nb_conventions_operateurs"
    ]

    df = df_CAICHUCMCC_conventions[colonnes].copy()

    # 2. NORMALISATION LIBELLÉS
    df["Departement"] = (
        df["Departement"]
        .str.replace(
            "DELEGATION TERRITORIALE",
            "DT",
            regex=False
        )
        .str.strip()
    )

    # 2. RAPPROCHEMENT LIBELLÉS
    df = rapprochement_libelles(
        df_ref_structure,
        df,
        "Departement"
    )

    # 3. RENOMMAGE FINAL
    df = df.rename(columns={
        "Nombre de CAI (conforme guide CHU)": "Dispositifs_d_urgence Nb_lots_CAI",
        "Nombre de CHU (conforme guide CHU)": "Dispositifs_d_urgence Nb_lots_CHU",
        "Nombre Lots CMCC": "Dispositifs_d_urgence Nb_lots_CMCC",
        "Prefecture": "Dispositifs_d_urgence Nb_conventions_prefecture"
    })

    return df






def indicateurs_raw_Textile(df_raw_Textile):

    # INDICATEUR NB BOUTIQUES

    indic_boutiques = (
        df_raw_Textile[
            df_raw_Textile["type_dispositif_textile"]
            == "Boutique"
        ]
        .groupby("n_structure")
        .size()
        .reset_index(name="Textile Nb_boutiques")
    )

    # INDICATEUR NB VESTIAIRES

    indic_vestiaires = (
        df_raw_Textile[
            df_raw_Textile["type_dispositif_textile"]
            == "Vestiaire"
        ]
        .groupby("n_structure")
        .size()
        .reset_index(name="Textile Nb_vestiaires")
    )

    # FUSION

    df_final = indic_boutiques.merge(
        indic_vestiaires,
        on="n_structure",
        how="outer"
    )

    # Remplacer NaN par 0
    indic_cols = [
        "Textile Nb_boutiques",
        "Textile Nb_vestiaires"
    ]

    df_final[indic_cols] = (
        df_final[indic_cols]
        .fillna(0)
        .astype(int)
    )

    return df_final






def indicateurs_CRope(df, df_ref_structure):
    """
    Calcule les indicateurs DUO par département / structure.

    Indicateurs :
    - Dispositifs_d_urgence Nb_operations
    - Dispositifs_d_urgence Nb_jours_operations
    - Dispositifs_d_urgence Ope_secours
    - Dispositifs_d_urgence Ope_soutien_pop
    - Dispositifs_d_urgence Nb_personnes_prises_charge
    """

    df["Num_departement"] = df["Num_departement"].replace({
        "01": "1",
        "02": "2",
        "03": "3",
        "04": "4",
        "05": "5",
        "07": "7",
        "09": "9",
        "08": "8",
        "06": "6"
    })

    # Si la colonne n_structure n'existe pas encore
    if "n_structure" not in df.columns:
        df["n_structure"] = ""

    mask = df["n_structure"] == ""

    mapping_dict = (
        df_ref_structure[
            df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"
        ]
        .set_index("n_dept")["n_structure"]
        .to_dict()
    )

    df.loc[mask, "n_structure"] = (
        df.loc[mask, "Num_departement"]
        .map(mapping_dict)
    )

    # PREPARATION DES DONNEES

    start_col = "Date et heure du début de l'opération :"
    end_col = "Date et heure de la fin de l'opération :"

    # Conversion datetime
    df[start_col] = pd.to_datetime(df[start_col], errors="coerce", dayfirst=True)
    df[end_col] = pd.to_datetime(df[end_col], errors="coerce", dayfirst=True)

    df = df[df["Date et heure du début de l'opération :"].dt.year == 2026]
    df = df[df["Typologie"] == "Opérations"]

    # Calcul durée en jours
    df["nb_jours_operation"] = (
        (df[end_col] - df[start_col]).dt.total_seconds() / 86400
    )

    # Sécurisation
    df["nb_jours_operation"] = (
        df["nb_jours_operation"]
        .fillna(0)
        .clip(lower=0)
    )

    # Conversion nombre personnes
    people_col = "Nombre de personnes accompagnées ou prises en charge :"

    df[people_col] = pd.to_numeric(
        df[people_col],
        errors="coerce"
    ).fillna(0)

    # INDICATEUR NB OPERATIONS

    df_operations = (
        df[df["Typologie"].str.contains("Opérations", na=False)]
        .groupby("n_structure")
        .size()
        .reset_index(name="Dispositifs_d_urgence Nb_operations")
    )

    # INDICATEUR NB JOURS OPERATIONS

    df_jours = (
        df[df["Typologie"].str.contains("Opérations", na=False)]
        .groupby("n_structure")["nb_jours_operation"]
        .sum()
        .reset_index(name="Dispositifs_d_urgence Nb_jours_operations")
    )

    # INDICATEUR OPE SECOURS (Agrément A)

    agrement_col = "Agrément concerné :"

    df_secours = (
        df[
            df[agrement_col]
            .str.contains("Agrément A", na=False)
        ]
        .groupby("n_structure")
        .size()
        .reset_index(name="Dispositifs_d_urgence Ope_secours")
    )

    # INDICATEUR OPE SOUTIEN POP (Agrément B)

    df_soutien = (
        df[
            df[agrement_col]
            .str.contains("Agrément B", na=False)
        ]
        .groupby("n_structure")
        .size()
        .reset_index(name="Dispositifs_d_urgence Ope_soutien_pop")
    )

    # INDICATEUR NB PERSONNES PRISES EN CHARGE

    df_personnes = (
        df.groupby("n_structure")[people_col]
        .sum()
        .reset_index(
            name="Dispositifs_d_urgence Nb_personnes_prises_charge"
        )
    )

    # MERGE FINAL

    df_final = df_operations.merge(
        df_jours,
        on="n_structure",
        how="outer"
    )

    df_final = df_final.merge(
        df_secours,
        on="n_structure",
        how="outer"
    )

    df_final = df_final.merge(
        df_soutien,
        on="n_structure",
        how="outer"
    )

    df_final = df_final.merge(
        df_personnes,
        on="n_structure",
        how="outer"
    )

    return df_final





def indicateurs_tracabilite_textile(df_tracabilite_textile, df_ref_structure):

    df = df_tracabilite_textile[["Code structure","Remonte des données chaque trimestre" ]].copy()

    df = df.rename(columns={"Remonte des données chaque trimestre": "Textile tracabilite_flux" })

    # 3. MERGE AVEC REF STRUCTURE
    df = df_ref_structure.merge(
        df,
        left_on="n_structure",
        right_on="Code structure",
        how="left"
    )
    df = df.drop(columns=["n_structure"]).rename(columns={"n_structure-ratt": "n_structure"})

    df['tracabilite_bool'] = df['Textile tracabilite_flux'] == 'Oui'

    # 2. On effectue le groupby
    # Si au moins un 'Oui' (True) existe, le résultat sera True
    resultat = df.groupby('n_structure')['tracabilite_bool'].any().reset_index()

    # 3. On reconvertit en 'Oui'/'Non'
    resultat['Textile tracabilite_flux'] = resultat['tracabilite_bool'].map({True: 'Oui', False: 'Non'})

    # 4. Nettoyage (optionnel)
    resultat = resultat.drop(columns=['tracabilite_bool'])

    df_final = pd.merge(resultat, df_ref_structure[['n_structure', 'DT_de_rattachement']].copy().drop_duplicates(), on='n_structure')

    return df_final





def indicateurs_OCR_PST_DEC_RED_CAI_CONV(
    df_OCR,
    df_PST,
    df_declenchement_clean,
    df_exercices_clean,
    df_CAICHUCMCC_conventions,
    df_raw_Textile,
    df_CRope_clean,
    df_tracabilite_textile,
    df_ref_structure
):
    df_OCR_Nb_deployees = indicateurs_OCR_nb_deployees(df_OCR, df_ref_structure)
    df_Dispositifs_d_urgence_PST = indicateurs_PST(df_PST, df_ref_structure)
    df_declenchement_VF = indicateurs_declenchements(df_declenchement_clean, df_ref_structure)
    df_exercices_VF = indicateurs_exercices(df_exercices_clean, df_ref_structure)
    # df_redcall2 = indicateurs_redcall(df_RC_grouped, df_ref_structure)
    df_CAICHUCMCC_conventionsVF = indicateurs_bilanus2025(df_CAICHUCMCC_conventions, df_ref_structure)
    df_raw_TextileVF = indicateurs_raw_Textile(df_raw_Textile)
    # df_raw_ProdResTextile = indicateurs_ProdResTextile(df_raw_ProdResTextile , df_ref_structure)
    df_CRopeVF = indicateurs_CRope(df_CRope_clean, df_ref_structure)
    df_tracabilite_textileVF = indicateurs_tracabilite_textile(df_tracabilite_textile, df_ref_structure)

    return (
        df_OCR_Nb_deployees,
        df_Dispositifs_d_urgence_PST,
        df_declenchement_VF,
        df_exercices_VF,
        df_CAICHUCMCC_conventionsVF,
        df_raw_TextileVF,
        df_CRopeVF,
        df_tracabilite_textileVF
    )




def indicateurs_OCR_DT(df_OCR_Nb_deployees, rattachement_court):
    df_OCR_Nb_deployees['n_structure'] = df_OCR_Nb_deployees['n_structure'].astype(int)
    # Merge données avec rattachement_court
    OCR_Nb_deployees = pd.merge(
    df_OCR_Nb_deployees,
    rattachement_court,
    on="n_structure",
    how="left"
    )

    # Groupby sur DT_de_rattachement
    Nb_OCR_DT = (OCR_Nb_deployees.groupby('DT_de_rattachement')['OCR Nb_deployees'].sum())
    return Nb_OCR_DT






def indicateurs_redcall_DT(df_redcall2, rattachement_court):
    df_redcall2['n_structure'] = df_redcall2['n_structure'].astype(int)
    # Merge données avec rattachement_court
    redcall = pd.merge(df_redcall2, rattachement_court, on="n_structure", how="left")


    # Groupby sur DT_de_rattachement
    RedCall_DT = (redcall.groupby('DT_de_rattachement')['Dispositifs_d_urgence Utilisation_RedCall'].max())
    return RedCall_DT






def OCR_RedCall_DT(df_OCR_Nb_deployees, df_redcall2, rattachement_court):
    Nb_OCR_DT = indicateurs_OCR_DT(df_OCR_Nb_deployees, rattachement_court).reset_index()
    RedCall_DT = indicateurs_redcall_DT(df_redcall2, rattachement_court)

    return (
        Nb_OCR_DT,
        RedCall_DT,
    )



def Textile_DT(df_raw_Textile, rattachement_court):
    df_raw_Textile['n_structure'] = df_raw_Textile['n_structure'].astype('float64')
    # Merge données avec rattachement_court
    textile = pd.merge(df_raw_Textile, rattachement_court, on="n_structure", how="left")

    # Groupby sur DT_de_rattachement
    Textile_DT = (textile.groupby('DT_de_rattachement')[["Textile Nb_boutiques","Textile Nb_vestiaires"]].sum())
    Textile_DT = Textile_DT.reset_index()
    return Textile_DT

def tracabilite_textile_DT(df_tracabilite_textileVF):
    df_tracabilite_textileVF_DT = df_tracabilite_textileVF.copy()
    df_tracabilite_textileVF_DT['Textile tracabilite_flux'] = df_tracabilite_textileVF_DT['Textile tracabilite_flux'].apply(lambda x: 1 if x == 'Oui' else 0)
    df_tracabilite_textileVF_DT = df_tracabilite_textileVF_DT.groupby('DT_de_rattachement', as_index=False)['Textile tracabilite_flux'].sum()
    return df_tracabilite_textileVF_DT

def crope_DT(df_CRopeVF, rattachement_court):
    df_CRopeVF_DT = pd.merge(df_CRopeVF, rattachement_court, on='n_structure', how="left")

    df_CRoPeVF_DT = (
        df_CRopeVF_DT
        .groupby("DT_de_rattachement", as_index=False)
        .sum(numeric_only=True)
    )

    df_CRopeVF_DT.drop(columns=["n_structure"], inplace=True)
    return df_CRopeVF_DT


def verif_textile(df_raw_Textile_c, df_raw_Textile, df_Textile_DT, df_ref_structure,rattachement_court):
  df_t = df_raw_Textile_c[df_raw_Textile_c["statut"] == "A jour"]
  df_t = df_t[df_t["Type de point apport"].isin(['Boutique - La Boutique','Vestiaire','Boutique  - Mobile', 'Boutique - Bébé','Boutique - Chez Henry','Boutique - Recylcerie / Meuble','La Boutique'])]



  if df_Textile_DT.reset_index()['Textile Nb_boutiques'].sum() == df_t.shape[0]:
    print('✅ df_Textile_DT est bien calculé (suomme de l indicateur == au nombre de lignes des données)')
  else:
    print('❌ df_Textile_DT n\'est pas bien calculé (suomme de l indicateur != au nombre de lignes des données), différence :', df_Textile_DT.reset_index()['Textile Nb_boutiques'].sum() - df_raw_Textile_c.shape[0])

  if df_raw_Textile['Textile Nb_boutiques'].sum() == df_t.shape[0]:
    print('✅ df_Textile_DT est bien calculé (suomme de l indicateur == au nombre de lignes des données)')
  else:
    print('❌ df_Textile_DT n\'est pas bien calculé (suomme de l indicateur != au nombre de lignes des données), différence :', df_Textile_DT.reset_index()['Textile Nb_boutiques'].sum() - df_raw_Textile_c.shape[0])

  if df_Textile_DT.reset_index()['Textile Nb_vestiaires'].sum() == df_t.shape[0]:
    print('✅ df_Textile_DT est bien calculé (suomme de l indicateur == au nombre de lignes des données)')
  else:
    print('❌ df_Textile_DT n\'est pas bien calculé (suomme de l indicateur != au nombre de lignes des données), différence :', df_Textile_DT.reset_index()['Textile Nb_vestiaires'].sum() - df_raw_Textile_c.shape[0])

  if df_raw_Textile['Textile Nb_vestiaires'].sum() == df_t.shape[0]:
    print('✅ df_Textile_DT est bien calculé (suomme de l indicateur == au nombre de lignes des données)')
  else:
    print('❌ df_Textile_DT n\'est pas bien calculé (suomme de l indicateur != au nombre de lignes des données), différence :', df_Textile_DT.reset_index()['Textile Nb_vestiaires'].sum() - df_raw_Textile_c.shape[0])

  verifier_colonne_structure(df_raw_Textile, "n_structure", df_ref_structure)
  # verifier_colonne_structure(df_raw_ProdResTextile, "n_structure", df_ref_structure)
  verifier_colonne_structure(df_Textile_DT.reset_index(), "DT_de_rattachement", rattachement_court)
  # verifier_colonne_structure(df_Textile_financier_DT, "DT_de_rattachement", rattachement_court)




############################################
######## OBSOLETE - VERSION 2024 ###########
############################################


def clean_ProdResTextile(df_raw_ProdResTextile):
    df = df_raw_ProdResTextile.iloc[:-1]

    # Renommer les colonnes
    df.columns.values[0] = 'code_comptable'
    df.columns.values[1] = 'libelle'
    df.columns.values[22] = 'Textile Produit_2024'
    df.columns.values[24] = 'Textile Resultat_2024'

    # Conserver les lignes liées aux DT
    df = df[df['code_comptable'].str.contains("DD", na=False)]

# Extraire le département
    def extraire_et_nettoyer_code_departement(texte):
        code = texte[-3:] # Extraire les 3 derniers caractères
        code = code.lstrip('0') # Supprimer les zéros initiaux
        return code

    df['Code Département'] = df['code_comptable'].apply(extraire_et_nettoyer_code_departement)

    return df


def indicateurs_ProdResTextile(df_raw_ProdResTextile, df_ref_structure):
    # Mapping sur le département
    mapping_dict = df_ref_structure[df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"].set_index('n_dept')['n_structure'].to_dict()
    df_raw_ProdResTextile['n_structure'] = df_raw_ProdResTextile['Code Département'].map(mapping_dict)
    verifier_mapping(df_raw_ProdResTextile, "n_structure", "libelle" ,df_ref_structure)

    # Conservation des colonnes utiles
    df = df_raw_ProdResTextile[["n_structure","Textile Produit_2024", "Textile Resultat_2024"]]

    # Suppression des espaces et "-"
    df['Textile Produit_2024'] = df['Textile Produit_2024'].str.replace(r"\s+", "", regex=True)
    df['Textile Produit_2024'] = df['Textile Produit_2024'].str.replace("-", "")
    df['Textile Resultat_2024'] = df['Textile Resultat_2024'].str.replace(r"\s+", "", regex=True)
    df['Textile Resultat_2024'] = df['Textile Resultat_2024'].str.replace("-", "")
    df = df.rename(columns = {'Textile Produit_2024' : 'Textile Produit_2025', 'Textile Resultat_2024' : 'Textile Resultat_2025'})

    return df


def Textile_financier_DT(df_raw_ProdResTextile, rattachement_court):
    df_raw_ProdResTextile['n_structure'] = df_raw_ProdResTextile['n_structure'].astype('float64')
    # Merge données avec rattachement_court
    textile_financier = pd.merge(df_raw_ProdResTextile, rattachement_court, left_on="n_structure", right_on="n_structure", how="left")

    # Groupby sur DT_de_rattachement
    Textile_financier__DT = (
    textile_financier
        .groupby('DT_de_rattachement')[['Textile Produit_2025', 'Textile Resultat_2025']]
        .sum()
        .reset_index()
    )

    return Textile_financier__DT