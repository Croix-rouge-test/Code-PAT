import os
import pandas as pd

import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *

from gspread_dataframe import get_as_dataframe

# Clean
def dept_clean(x):
  if x == '2A' or x == '2B':
    return str(x)
  else : return str(int(x))


def import_clean_donnees_financieres(financier, df_ref_structure):

    # ======================
    # IMPORT
    # ======================
    dt_prod = get_as_dataframe(financier.worksheet('Produits expl°'), skiprows=3, evaluate_formulas=True)
    dt_resnet = get_as_dataframe(financier.worksheet('Résultat'), skiprows=3, evaluate_formulas=True)



    # ======================
    # RENOMMAGE
    # ======================
    dt_prod = dt_prod.rename(columns = {'N° Structure' : 'n_structure',"Dptmt":"n_dept"})
    dt_resnet = dt_resnet.rename(columns = {'N° Structure' : 'n_structure', "Dptmt":"n_dept" })
    

    
    dt_prod = dt_prod[dt_prod['n_structure'] == 'D']
    dt_resnet = dt_resnet[dt_resnet['n_structure'] == 'D']

    dt_prod= dt_prod[['n_dept','Réalisé 2023 Total Année','Réalisé 2024 Total Année','Nom Structure']]\
        .rename(columns={'Réalisé 2024 Total Année': 'Financier Prod_2024', 'Réalisé 2023 Total Année': 'Financier Prod_2023'})\

    dt_prod['Nom Structure'] = 'DT - ' + dt_prod['Nom Structure']

    dt_resnet= dt_resnet[['n_dept','Réalisé 2023 Total Année','Réalisé 2024 Total Année','Nom Structure']]\
        .rename(columns={'Réalisé 2024 Total Année': 'Financier ResNet_2024', 'Réalisé 2023 Total Année': 'Financier ResNet_2023'})\

    dt_resnet['Nom Structure'] = 'DT - ' + dt_resnet['Nom Structure']




    # ======================
    # CLEAN COMMUN
    # ======================
    for df in [dt_prod, dt_resnet]:
        df['n_dept'] = df['n_dept'].apply(dept_clean)

    # Filtre structures
    valid_structures = set(df_ref_structure['n_structure'].drop_duplicates().values)

    DT_dept = df_ref_structure[df_ref_structure['type_structure'] == 'DELEGATION TERRITORIALE - DT'][['n_structure','n_dept']].drop_duplicates()

    dt_prod = pd.merge(dt_prod, DT_dept, on = 'n_dept').drop('n_dept',axis = 1).drop('Nom Structure', axis = 1)
    dt_resnet = pd.merge(dt_resnet, DT_dept, on = 'n_dept')



    df_financier_2023_2024 = pd.merge(dt_prod,dt_resnet, on = 'n_structure', how = 'outer')

    df_financier_2023_2024['Financier ResNet_2024'] = pd.to_numeric(
        df_financier_2023_2024['Financier ResNet_2024'],
        errors='coerce'
    ) 

    
    df_financier_2023_2024['Financier ResNet_2023'] = pd.to_numeric(
        df_financier_2023_2024['Financier ResNet_2023'],
        errors='coerce'
    ) 
    
    df_financier_2023_2024['Financier Prod_2024'] = pd.to_numeric(
        df_financier_2023_2024['Financier Prod_2024'],
        errors='coerce'
    ) 

    
    df_financier_2023_2024['Financier Prod_2023'] = pd.to_numeric(
        df_financier_2023_2024['Financier Prod_2023'],
        errors='coerce'
    ) 
    
    df_financier_2023_2024['Financier ResCorrProd_2024'] = df_financier_2023_2024['Financier ResNet_2024'] / df_financier_2023_2024['Financier Prod_2024']

    df_financier_2023_2024['Financier ResCorrProd_2023'] = df_financier_2023_2024['Financier ResNet_2023'] / df_financier_2023_2024['Financier Prod_2023']

    colonnes_futuna_vide = [
        "Financier Prod_2025",
        "Financier ResNet_2025",
        "Financier ResCorrProd_2025",
        "Financier Prod_2023",
        "Financier ResNet_2023",
        "Financier ResCorrProd_2023",
        "Financier Prod_2024",
        "Financier ResNet_2024",
        "Financier ResCorrProd_2024",
        "Financier caf_2025",
        "Financier TresoBrute_2025",
        "Financier Mois_AvanceTreso_2025"
    ]

    for col in colonnes_futuna_vide:
        df_financier_2023_2024.loc[df_financier_2023_2024['n_structure'] == 3884, col] = None
    
    df_financier_2023_2024.loc[df_financier_2023_2024['n_structure'] == 1285, 'Financier TresoBrute_2025'] = 661366

    # ======================
    # RETURN DICTIONNAIRE
    # ======================
    return df_financier_2023_2024


# def fusion_donnees_financieres(financial_data, df_ref_structure):

#     result = {}

#     for year in ["2024", "2023"]:

#         # ======================
#         # INPUTS
#         # ======================
#         dt_prod = financial_data[year]["dt_prod"]
#         dt_resnet = financial_data[year]["dt_resnet"]
#         dt_rescorr = financial_data[year]["dt_rescorr"]

#         dt_ul_prod = financial_data[year]["dt_ul_prod"]
#         dt_ul_resnet = financial_data[year]["dt_ul_resnet"]
#         dt_ul_rescorr = financial_data[year]["dt_ul_rescorr"]

#         # ======================
#         # DONNÉES PAR DT
#         # ======================
#         df_financier_DT = pd.merge(dt_prod, dt_resnet, on="n_dept", how="left")
#         df_financier_DT = pd.merge(df_financier_DT, dt_rescorr, on="n_dept", how="left")

#         # ======================
#         # DONNÉES PAR STRUCTURE
#         # ======================
#         df_financier_DT_UL = pd.merge(dt_ul_prod, dt_ul_resnet, on="n_structure", how="left")
#         df_financier_DT_UL = pd.merge(df_financier_DT_UL, dt_ul_rescorr, on="n_structure", how="left")

#         # ======================
#         # RATTACHEMENT DT
#         # ======================
#         df_financier_DT = pd.merge(
#             df_ref_structure[df_ref_structure['type_structure'] == "DELEGATION TERRITORIALE - DT"][['DT_de_rattachement','n_dept']].drop_duplicates(),
#             df_financier_DT,
#             on='n_dept',
#             how='inner'
#         )

#         df_financier_DT = df_financier_DT.drop_duplicates(['DT_de_rattachement'])

#         df_financier_DT_UL = apply_rattachement_successif(
#             df_ref_structure,
#             df_financier_DT_UL,
#             col='n_structure'
#         )

#         # ======================
#         # CAS PARTICULIER 4381
#         # ======================
#         mask = df_financier_DT_UL['n_structure'] == 4381
#         df_subset = df_financier_DT_UL.loc[mask].copy()

#         if not df_subset.empty:

#             # filtrer UL / DT
#             mask_dt_ul = df_subset['libelle_structure'].str.contains('DT|UL', case=False, na=False)
#             df_dt_ul = df_subset.loc[mask_dt_ul]

#             prod_col = f'Financier Prod_{year}'
#             resnet_col = f'Financier ResNet_{year}'
#             rescorr_col = f'Financier ResCorrProd_{year}'


#             # agrégations
#             prod_sum = df_subset[prod_col].sum()
#             resnet_sum = df_subset[resnet_col].sum()

#             rescorr = (
#                 resnet_sum / prod_sum
#                 if len(df_subset) > 1 and prod_sum != 0
#                 else df_subset[rescorr_col].iloc[0]
#             )

#             # mise à jour
#             df_financier_DT_UL.loc[mask, prod_col] = prod_sum
#             df_financier_DT_UL.loc[mask, resnet_col] = resnet_sum
#             df_financier_DT_UL.loc[mask, rescorr_col] = rescorr

#         df_financier_DT_UL = df_financier_DT_UL.drop_duplicates(subset=['n_structure'], keep='first')

#         df_financier_DT = df_financier_DT.rename(columns={'DT_de_rattachement':'n_structure'})
#         df_financier_DT['n_structure'] = df_financier_DT['n_structure'].astype(str).apply(keep_integer).astype(int)

#         df_financier_DT_UL['n_structure'] = df_financier_DT_UL['n_structure'].astype(int)

#         # ======================
#         # STOCKAGE RESULTAT
#         # ======================
#         result[year] = {
#             "df_financier_DT": df_financier_DT,
#             "df_financier_DT_UL": df_financier_DT_UL
#         }

#     return result

def textile_calc(df_raw_ProdResTextile_c, df_ref_structure):

    # Nettoyage des DF et sélection des colonnes pertinentes

    df_ProdResTextile_clean = df_raw_ProdResTextile_c.iloc[:, [0, 1, 22, 28]].copy()

    df_ProdResTextile_clean.columns = ["n_structure", "nom_structure",
        "Textile Produit_2025",
        "Textile Vente_solidaire"
    ]

    # Supprimer la ligne "03959 DT DE LA REUNION" : car doublon
    df_ProdResTextile_clean = df_ProdResTextile_clean[
        ~df_ProdResTextile_clean["nom_structure"]
        .astype(str)
        .str.contains(r"03959\s+DT DE LA REUNION", case=False, na=False, regex=True)
    ].copy()

    df_ProdResTextile_clean.replace({"n_structure": {"ORDD02A": 3965}}, inplace=True)
    df_ProdResTextile_clean.replace({"n_structure": {"ORDD02B": 3967}}, inplace=True)


    df_ProdResTextile_clean = df_ProdResTextile_clean[~df_ProdResTextile_clean["n_structure"].isna()]

    df_ProdResTextile_clean["n_structure"] = (
        df_ProdResTextile_clean["n_structure"]
        .astype(str)
        .str.replace(r"\D", "", regex=True)
        .replace("", pd.NA)
        .replace("-", pd.NA)
    )

    df_ProdResTextile_clean["n_structure"] = pd.to_numeric(
        df_ProdResTextile_clean["n_structure"],
        errors="coerce"
    ).astype("Int64")


    #Transforme les données en valeurs numériques, en supprimant les espaces, les caractères spéciaux et en gérant les erreurs de conversion

    cols = ["Textile Vente_solidaire"]

    for col in cols:
        df_ProdResTextile_clean[col] = (
            df_ProdResTextile_clean[col]
            .astype(str)
            .str.replace(" ", "", regex=False)
            .str.replace("\u00a0", "", regex=False)  # espaces insécables
            .str.replace("%", "", regex=False)
            .str.replace("−", "-", regex=False)   # important
            .str.replace("–", "-", regex=False)   # important
            .str.replace(r"[^\d-]", "", regex=True)
            .replace("-", pd.NA)
        )
    df_ProdResTextile_clean["Textile Vente_solidaire"] = pd.to_numeric(
    df_ProdResTextile_clean["Textile Vente_solidaire"],
    errors="coerce"
    )

    df_ProdResTextile_clean["Textile Produit_2025"] = (
        df_ProdResTextile_clean["Textile Produit_2025"]
        .astype(str)
        .str.replace("−", "-", regex=False)   # important
        .str.replace("–", "-", regex=False)   # important
        .str.replace(r"[^\d-]", "", regex=True)
        .replace("-", pd.NA)
    )

    df_ProdResTextile_clean["Textile Produit_2025"] = pd.to_numeric(
        df_ProdResTextile_clean["Textile Produit_2025"],
        errors="coerce"
    )

    #On supprimme les doubles lignes vides
    cols = ["Textile Produit_2025", "Textile Vente_solidaire"]

    # Remplacer les valeurs vides ou " - " par NA
    df_ProdResTextile_clean[cols] = (
        df_ProdResTextile_clean[cols]
        .replace(r"^\s*-\s*$", pd.NA, regex=True)
        .replace(r"^\s*$", pd.NA, regex=True)
    )

    # Garder les lignes où au moins une des deux colonnes est renseignée
    df_ProdResTextile_clean = df_ProdResTextile_clean[
        df_ProdResTextile_clean[cols].notna().any(axis=1)
    ].copy()

    df_ProdResTextile_clean= df_ProdResTextile_clean[
        (
            df_ProdResTextile_clean["Textile Produit_2025"].notna()
            & (df_ProdResTextile_clean["Textile Produit_2025"] != " - ")
        )
        |
        (
            df_ProdResTextile_clean["Textile Vente_solidaire"].notna()
            & (df_ProdResTextile_clean["Textile Vente_solidaire"] != " - ")
        )
    ].copy()


    #On supprimme les DR avec "REGION"
    df_ProdResTextile_clean = df_ProdResTextile_clean[
        ~df_ProdResTextile_clean["nom_structure"].str.contains("REGION", case=False, na=False)
    ].copy()

    #Création des DF Structures et DT 

    df_ProdResTextile_clean_structure = df_ProdResTextile_clean[
        ~df_ProdResTextile_clean["nom_structure"].str.contains("DELEGATIONS", case=False, na=False)
    ].copy()

    df_ProdResTextile_clean_DT = df_ProdResTextile_clean[
        df_ProdResTextile_clean["nom_structure"].str.contains("DELEGATIONS", case=False, na=False)
    ].copy()

    df_ProdResTextile_clean_DT = df_ProdResTextile_clean_DT[['nom_structure', 'Textile Produit_2025',
        'Textile Vente_solidaire']]


    #RENAME DES DTs

    df_ProdResTextile_clean_DT["nom_structure"] = (
        df_ProdResTextile_clean_DT["nom_structure"]
        .astype(str)
        .str.strip()
    )

    df_ProdResTextile_clean_DT.replace({
        "nom_structure": {
            "DELEGATIONS DES ALPES DE HAUTE PROVENCE": "DT DES ALPES DE HAUTE PROVENCE",
            "DELEGATIONS DES ALPES MARITIMES": "DT DES ALPES MARITIMES",
            "DELEGATIONS DES ARDENNES": "DT DES ARDENNES",
            "DELEGATIONS DU BAS RHIN": "DT DU BAS RHIN",
            "DELEGATIONS DES BOUCHES DU RHONE": "DT DES BOUCHES DU RHONE",
            "DELEGATIONS DU CALVADOS": "DT DU CALVADOS",
            "DELEGATIONS DU CANTAL": "DT DU CANTAL",
            "DELEGATIONS DE CHARENTE": "DT DE LA CHARENTE",
            "DELEGATIONS DE CHARENTE MARITIME": "DT DE CHARENTE MARITIME",
            "DELEGATIONS DU CHER": "DT DU CHER",
            "DELEGATIONS DE COTE D'OR": "DT DE LA COTE D'OR",
            "DELEGATIONS DES COTES D'ARMOR": "DT DES COTES D'ARMOR",
            "DELEGATIONS DES DEUX SEVRES": "DT DES DEUX SEVRES",
            "DELEGATIONS DU DOUBS": "DT DU DOUBS",
            "DELEGATIONS DU FINISTERE": "DT DU FINISTERE",
            "DELEGATIONS DU GARD": "DT DU GARD",
            "DELEGATIONS DU GERS": "DT DU GERS",
            "DELEGATIONS DU HAUT RHIN": "DT DU HAUT RHIN",
            "DELEGATIONS DE HAUTE GARONNE": "DT DE HAUTE GARONNE",
            "DELEGATIONS DE HAUTE SAVOIE": "DT DE LA HAUTE SAVOIE",
            "DELEGATIONS DES HAUTES ALPES": "DT DES HAUTES ALPES",
            "DELEGATIONS DES HAUTES PYRENEES": "DT DES HAUTES PYRENEES",
            "DELEGATIONS DES HAUTS DE SEINE": "DT DES HAUTS DE SEINE",
            "DELEGATIONS D'ILLE ET VILAINE": "DT DE L'ILLE ET VILAINE",
            "DELEGATIONS DU JURA": "DT DU JURA",
            "DELEGATIONS DE LA CORREZE": "DT DE LA CORREZE",
            "DELEGATIONS DE LA CORSE DU SUD": "DT DE LA CORSE DU SUD",
            "DELEGATIONS DE LA CREUSE": "DT DE LA CREUSE",
            "DELEGATIONS DE LA DORDOGNE": "DT DE LA DORDOGNE",
            "DELEGATIONS DE LA DROME": "DT DE LA DROME",
            "DELEGATIONS DE LA GIRONDE": "DT DE LA GIRONDE",
            "DELEGATIONS DE LA GUADELOUPE": "DT DE LA GUADELOUPE",
            "DELEGATIONS DE LA GUYANE": "DT DE LA GUYANE",
            "DELEGATIONS DE LA HAUTE CORSE": "DT DE LA HAUTE CORSE",
            "DELEGATIONS DE LA HAUTE LOIRE": "DT DE LA HAUTE LOIRE",
            "DELEGATIONS DE LA HAUTE MARNE": "DT DE LA HAUTE MARNE",
            "DELEGATIONS DE LA HAUTE SAONE": "DT DE HAUTE SAONE",
            "DELEGATIONS DE LA HAUTE VIENNE": "DT DE LA HAUTE VIENNE",
            "DELEGATIONS DE LA LOIRE": "DT DE LA LOIRE",
            "DELEGATIONS DE LA LOZERE": "DT DE LA LOZERE",
            "DELEGATIONS DE LA MANCHE": "DT DE LA MANCHE",
            "DELEGATIONS DE LA MARNE": "DT DE LA MARNE",
            "DELEGATIONS DE LA MARTINIQUE": "DT DE LA MARTINIQUE",
            "DELEGATIONS DE LA MAYENNE": "DT DE LA MAYENNE",
            "DELEGATIONS DE LA MEURTHE-ET-M": "DT DE MEURTHE ET MOSELLE",
            "DELEGATIONS DE LA MEUSE": "DT DE LA MEUSE",
            "DELEGATIONS DE LA MOSELLE": "DT DE LA MOSELLE",
            "DELEGATIONS DE LA NIEVRE": "DT DE LA NIEVRE",
            "DELEGATIONS DE LA REUNION": "DT DE LA REUNION",
            "DELEGATIONS DE LA SAONE ET LOI": "DT DE SAONE ET LOIRE",
            "DELEGATIONS DE LA SARTHE": "DT DE LA SARTHE",
            "DELEGATIONS DE LA SAVOIE": "DT DE LA SAVOIE",
            "DELEGATIONS DE LA SOMME": "DT DE LA SOMME",
            "DELEGATIONS DE LA VENDEE": "DT DE VENDEE",
            "DELEGATIONS DE LA VIENNE": "DT DE LA VIENNE",
            "DELEGATIONS DE L'AIN": "DT DE L'AIN",
            "DELEGATIONS DE L'AISNE": "DT DE L'AISNE",
            "DELEGATIONS DE L'ALLIER": "DT DE L'ALLIER",
            "DELEGATIONS DES LANDES": "DT DES LANDES",
            "DELEGATIONS DE L'ARDECHE": "DT DE L'ARDECHE",
            "DELEGATIONS DE L'ARIEGE": "DT DE L'ARIEGE",
            "DELEGATIONS DE L'AUBE": "DT DE L'AUBE",
            "DELEGATIONS DE L'AUDE": "DT DE L'AUDE",
            "DELEGATIONS DE L'AVEYRON": "DT DE L'AVEYRON",
            "DELEGATIONS DE L'ESSONNE": "DT DE L'ESSONNE",
            "DELEGATIONS DE L'EURE": "DT DE L'EURE",
            "DELEGATIONS DE L'EURE ET LOIRE": "DT D'EURE ET LOIR",
            "DELEGATIONS DE L'HERAULT": "DT DE L'HERAULT",
            "DELEGATIONS DE L'INDRE": "DT DE L'INDRE",
            "DELEGATIONS DE L'INDRE ET LOIRE": "DT D'INDRE ET LOIRE",
            "DELEGATIONS DE L'ISERE": "DT DE L'ISERE",
            "DELEGATIONS DU LOIR ET CHER": "DT DU LOIR ET CHER",
            "DELEGATIONS DE LOIRE ATLANTIQUE": "DT DE LA LOIRE ATLANTIQUE",
            "DELEGATIONS DU LOIRET": "DT DU LOIRET",
            "DELEGATIONS DE L'OISE": "DT DE L'OISE",
            "DELEGATIONS DE L'ORNE": "DT DE L'ORNE",
            "DELEGATIONS DU LOT": "DT DU LOT",
            "DELEGATIONS DU LOT ET GARONNE": "DT DU LOT ET GARONNE",
            "DELEGATIONS DE L'YONNE": "DT DE L'YONNE",
            "DELEGATIONS DU MAINE ET LOIRE": "DT DU MAINE ET LOIRE",
            "DELEGATIONS DE MAYOTTE": "DT DE MAYOTTE",
            "DELEGATIONS DU MORBIHAN": "DT DU MORBIHAN",
            "DELEGATIONS DU NORD": "DT DU NORD",
            "DELEGATIONS DE NOUVELLE CALEDONIE": "DT DE NOUVELLE CALEDONIE",
            "DELEGATIONS DE PARIS": "DT DE PARIS",
            "DELEGATIONS DU PAS DE CALAIS": "DT DU PAS DE CALAIS",
            "DELEGATIONS DU PUY DE DOME": "DT DU PUY DE DOME",
            "DELEGATIONS DES PYRENEES ORIENTALES": "DT DES PYRENEES ORIENTALES",
            "DELEGATIONS DES PYRENEES-ATLANTIQUES": "DT DES PYRENEES ATLANTIQUES",
            "DELEGATIONS DU RHONE": "DT DU RHONE",
            "DELEGATIONS DE SAINT BARHELEMY": "DT DE ST BARTHELEMY",
            "DELEGATIONS DE SAINT-MARTIN": "DT DE ST MARTIN",
            "DELEGATIONS DE SEINE ET MARNE": "DT DE LA SEINE ET MARNE",
            "DELEGATIONS DE SEINE MARITIME": "DT DE LA SEINE MARITIME",
            "DELEGATIONS DE SEINE SAINT DEN": "DT DE SEINE SAINT DENIS",
            "DELEGATIONS DU TARN": "DT DU TARN",
            "DELEGATIONS DU TARN ET GARONNE": "DT DU TARN ET GARONNE",
            "DELEGATIONS TERRITOIRE DE BELFORT": "DT DU TERRITOIRE DE BELFORT",
            "DELEGATIONS DU VAL DE MARNE": "DT DU VAL DE MARNE",
            "DELEGATIONS DU VAL D'OISE": "DT DU VAL D'OISE",
            "DELEGATIONS DU VAR": "DT DU VAR",
            "DELEGATIONS DU VAUCLUSE": "DT DU VAUCLUSE",
            "DELEGATIONS DES VOSGES": "DT DES VOSGES",
            "DELEGATIONS DES YVELINES": "DT DES YVELINES",
        }
    }, inplace=True)

    #Correction des N° structure non pertinents (surtout les maisons)
    #Pour le numero de l'AL AL ILE ROUSSE
    df_ProdResTextile_clean_structure.replace({"n_structure": {3983: 4960}}, inplace=True)

    df_ProdResTextile_clean_structure.replace({"n_structure": {716: 4921}}, inplace=True)
    df_ProdResTextile_clean_structure.replace({"n_structure": {728: 4946}}, inplace=True)
    df_ProdResTextile_clean_structure.replace({"n_structure": {730: 4947}}, inplace=True)

    #Merge avec le ref structure pour récupérer les Noms de structures officiels 
    df_ProdResTextile_clean_structure = pd.merge(df_ProdResTextile_clean_structure, df_ref_structure[["n_structure", "nom_structure"]], on="n_structure", how="left")

    #Drop les lignes où le nom de structure n'a pas été trouvé dans le ref structure (structures salariées)
    df_ProdResTextile_clean_structure = df_ProdResTextile_clean_structure.dropna(
        subset=["nom_structure_y"]
    )

    #Récupération du n de structure officiel à partir du ref structure
    df_ProdResTextile_clean_structure = pd.merge(df_ProdResTextile_clean_structure, df_ref_structure[["n_structure", "nom_structure"]], left_on="nom_structure_y", right_on="nom_structure", how="left")

    df_ProdResTextile_clean_structure = df_ProdResTextile_clean_structure[["n_structure_y","Textile Produit_2025", "Textile Vente_solidaire",]]
    df_ProdResTextile_clean_structure.rename(columns={"n_structure_y": "n_structure"}, inplace=True)

    # Ajouter 22513 + 20 à la structure 725
    df_ProdResTextile_clean_structure.loc[
        df_ProdResTextile_clean_structure["n_structure"] == 725,
        "Textile Produit_2025"
    ] += 22513.0 + 20.0

    # Ajouter 17594 à la structure 4381
    df_ProdResTextile_clean_structure.loc[
        df_ProdResTextile_clean_structure["n_structure"] == 4381,
        "Textile Produit_2025"
    ] += 17594.0

    df_ProdResTextile_clean_DT = pd.merge(df_ProdResTextile_clean_DT, df_ref_structure[df_ref_structure['type_structure'] == "DELEGATION TERRITORIALE - DT"][['n_structure','nom_structure']].drop_duplicates(), left_on="nom_structure", right_on="nom_structure", how="left")

    return df_ProdResTextile_clean_structure, df_ProdResTextile_clean_DT

def import_clean_donnees_financieres_bigquery(financier_sheet,financier_textile,financier_DPS, df_ref_structure):
    
    donnees_2023_2024 = import_clean_donnees_financieres(financier_sheet,df_ref_structure)

    # query_donnees_financieres = """
    #     SELECT *
    #     FROM `crf-pat.dataset_PAT_2025.donnees_financieres_2025`
    #     """
    # financier = client.query(query_donnees_financieres).to_dataframe().rename(columns={'N__Dept':'n_dept','N_structure':'n_structure','Type_structure':'type_structure'})
    
    df_ref_structure['n_dept'] = df_ref_structure['n_dept'].apply(dept_clean)

    financier = get_as_dataframe(financier_sheet.worksheet('Données'), evaluate_formulas=True)

    financier.columns = [
        ''.join(c if c.isalnum() else '_' for c in str(col))
        for col in financier.columns
    ]
    financier = financier.rename(columns={'N__Dept':'n_dept','N_structure':'n_structure','Type_structure':'type_structure'})
        #SELECT rattachement_benevole_nivol_id_fk, rattachement_benevole_structure_id_fk
    df_financier = financier.rename(columns={'Produits_d_exploitation_2025' : 'Financier Prod_2025','Résultat_net_par_structure' : 'Financier ResNet_2025', 'Résultat_corrélé_au_Chiffres_d_affaire' : 'Financier ResCorrProd_2025'})
    df_financier = df_financier[['n_structure','Financier Prod_2025', 'Financier ResNet_2025', 'Financier ResCorrProd_2025']].apply(pd.to_numeric, errors='coerce')



    df_financier_DT = financier[(financier['type_structure'] == 'DELEGATION DEPARTEMENTALE - DD') | (financier['type_structure'] == 'DELEGATION TERRITORIALE - DT')]
    df_financier_DT = df_financier_DT.rename(columns={'Produits_d_exploitation_consolidés__DT_' : 'Financier Prod_2025','Résultat_net_consolidé_par_DT' : 'Financier ResNet_2025'})
    df_financier_DT = df_financier_DT[['n_structure','Financier Prod_2025', 'Financier ResNet_2025']].apply(pd.to_numeric, errors='coerce')
    df_financier_DT['Financier ResCorrProd_2025'] = df_financier_DT['Financier ResNet_2025']/df_financier_DT['Financier Prod_2025']

    #  Financier TresoBrute_2025
    tresobrute = get_as_dataframe(financier_sheet.worksheet('Tréso'), skiprows=2, evaluate_formulas=True)
    tresobrute = tresobrute.iloc[:tresobrute.shape[0]-1]
    tresobrute = tresobrute[(tresobrute['Trésorerie brute'] != '31/12/2025') & (tresobrute['Avance de tréso en mois'] != '31/12/2025') & (tresobrute['N° Structure'].notna())]
    tresobrute.loc[tresobrute['N° Dptmt'].notna(), 'N° Dptmt'] = tresobrute.loc[tresobrute['N° Dptmt'].notna(), 'N° Dptmt'].apply(dept_clean)
    
    # Split tresobrute into structure and DT data before filtering
    tresobrute_structures = tresobrute[tresobrute['N° Structure'] != 'D'].copy()
    tresobrute_dt = tresobrute[tresobrute['N° Structure'] == 'D'].copy()
    
    df_tresobrute = tresobrute_structures.copy()
    df_tresobrute['Trésorerie brute'] = df_tresobrute['Trésorerie brute'].apply(pd.to_numeric, errors='coerce')
    df_tresobrute = df_tresobrute.rename(columns={'N° Structure': 'n_structure','N° Dptmt': 'n_dept','Trésorerie brute' : 'Financier TresoBrute_2025' , 'Avance de tréso en mois' : 'Financier Mois_AvanceTreso_2025'})
    df_tresobrute['n_structure'] = df_tresobrute['n_structure'].astype(int)

    df_tresobrute_DT = pd.merge(
        tresobrute_dt.rename(columns={
            'N° Structure': 'n_structure',
            'N° Dptmt': 'n_dept',
            'Trésorerie brute': 'Financier TresoBrute_2025',
            'Avance de tréso en mois': 'Financier Mois_AvanceTreso_2025'
        })[['n_dept', 'Financier TresoBrute_2025', 'Financier Mois_AvanceTreso_2025']],
        
        df_ref_structure[~df_ref_structure['type_structure'].isin(['REGION - DR' , 'INSTANCES NATIONALES - IN', 'IMPLANTATION LOCALE HORS AL - IL'])][['n_dept','DT_de_rattachement']].drop_duplicates(),
        
        on='n_dept',
        how='inner'
    )

    df_tresobrute_DT = df_tresobrute_DT.rename(columns={
        'DT_de_rattachement': 'n_structure'
    })

    # Conversion numérique
    df_tresobrute_DT['Financier TresoBrute_2025'] = pd.to_numeric(
        df_tresobrute_DT['Financier TresoBrute_2025'], errors='coerce'
    )
    df_tresobrute_DT['Financier Mois_AvanceTreso_2025'] = pd.to_numeric(
        df_tresobrute_DT['Financier Mois_AvanceTreso_2025'], errors='coerce'
    )

    # nettoyage n_structure
    df_tresobrute_DT = df_tresobrute_DT[df_tresobrute_DT['n_structure'].notna()]
    df_tresobrute_DT['n_structure'] = df_tresobrute_DT['n_structure'].astype(str).apply(keep_integer).astype(int)
        
    
    # query_caf = """
    # SELECT *
    # FROM `crf-pat.dataset_PAT_2025.caf_2025`
    # """
    
    #     #SELECT rattachement_benevole_nivol_id_fk, rattachement_benevole_structure_id_fk
    # caf = client.query(query_donnees_financieres).to_dataframe().rename(columns={'Dptmt':'n_dept','N__Structure':'n_structure','Nom_Structure':'nom_structure'})
    
    caf = get_as_dataframe(financier_sheet.worksheet('CAF'), skiprows=3, evaluate_formulas=True)

    # Filtre brute pour enlever structure dupiquée

    caf = caf[(caf['N° Smartview'] != 'AS3968HA')]

    caf.columns = [
        ''.join(c if c.isalnum() else '_' for c in str(col))
        for col in caf.columns
    ]
    
    caf = caf.rename(columns={'Dptmt':'n_dept','N__Structure':'n_structure','Nom_Structure':'nom_structure'})
    caf = caf[caf['n_structure'].notna()]
    caf['n_dept'] = caf['n_dept'].apply(dept_clean)

    df_caf = caf.rename(columns={'Réalisé_2025_Total_Année' : 'Financier caf_2025'})
    df_caf = df_caf[['n_structure','Financier caf_2025']].apply(pd.to_numeric, errors='coerce')
    df_caf = df_caf[(df_caf['n_structure'].notna()) & (df_caf['n_structure'] != 'D')]
    df_caf['n_structure'] = df_caf['n_structure'].astype(int)


    df_caf_DT = pd.merge(caf[(caf['n_structure'] == 'D')], df_ref_structure[~df_ref_structure['type_structure'].isin(['REGION - DR' , 'INSTANCES NATIONALES - IN', 'IMPLANTATION LOCALE HORS AL - IL'])][['n_dept','DT_de_rattachement']].drop_duplicates(), on='n_dept', how='inner').rename(columns={'Réalisé_2025_Total_Année' : 'Financier caf_2025'})
    df_caf_DT = df_caf_DT[['DT_de_rattachement','Financier caf_2025']]
    df_caf_DT['Financier caf_2025'] = df_caf_DT['Financier caf_2025'].apply(pd.to_numeric, errors='coerce')
    # df_caf_DT = df_caf_DT.groupby('DT_de_rattachement').agg({'Financier caf_2025':'sum'}).reset_index()
    df_caf_DT = df_caf_DT.rename(columns={'DT_de_rattachement':'n_structure'})
    df_caf_DT = df_caf_DT[df_caf_DT['n_structure'].notna()]
    df_caf_DT['n_structure'] = df_caf_DT['n_structure'].apply(keep_integer).astype(int)

    # Textile DPS
    df_financier_textile_struct, df_financier_textile_DT = textile_calc(financier_textile, df_ref_structure)
    df_financier_dps, df_financier_dps_DT = indicateur_financier_DPS_2025(financier_DPS,df_ref_structure)


    df_financier = pd.merge(df_ref_structure['n_structure'].drop_duplicates(), df_financier, on='n_structure', how='left')
    df_financier_DT = pd.merge(df_ref_structure[df_ref_structure['type_structure'] == 'DELEGATION TERRITORIALE - DT']['n_structure'].drop_duplicates(), df_financier_DT, on='n_structure', how='left')



    df_financier_DT = pd.merge(df_financier_DT, donnees_2023_2024, on='n_structure', how='left')

    df_financier['n_structure'] = df_financier['n_structure'].astype(int)
    df_financier_DT['n_structure'] = df_financier_DT['n_structure'].astype(int)
    
    df_financier = pd.merge(df_financier,df_caf, on='n_structure', how='left')
    df_financier_DT = pd.merge(df_financier_DT,df_caf_DT, on='n_structure', how='left')

    df_financier = pd.merge(df_financier,df_tresobrute, on='n_structure', how='left')
    df_financier_DT = pd.merge(df_financier_DT,df_tresobrute_DT, on='n_structure', how='left')

    df_financier = pd.merge(df_financier,df_financier_dps, on='n_structure', how='left')
    df_financier_DT = pd.merge(df_financier_DT,df_financier_dps_DT, on='n_structure', how='left')

    df_financier = pd.merge(df_financier,df_financier_textile_struct, on='n_structure', how='left')
    df_financier_DT = pd.merge(df_financier_DT,df_financier_textile_DT, on='n_structure', how='left')

    df_financier_DT = df_financier_DT.drop('n_dept_x', axis = 1).drop('n_dept_y', axis = 1).drop('Nom Structure', axis = 1).drop('nom_structure', axis = 1)

    return df_financier, df_financier_DT, financier


def verifications_financiers(df_financier, df_financier_DT, df_ref_structure, financier, financier_2025):
    print('Vérifications par structure :')
    verifier_colonne_structure(df_financier, "n_structure", df_ref_structure)

    print('')
    # =========================
    # 🔹 PRODUITS & RÉSULTAT
    # =========================
    financier_struct_verif = financier[
        ['Produits_d_exploitation_2025', 'Résultat_net_par_structure']
    ].apply(pd.to_numeric, errors='coerce').sum()

    if round(financier_struct_verif['Produits_d_exploitation_2025'], 2) != round(df_financier['Financier Prod_2025'].sum(), 2):
        print(f"❌ Problème Produits : {financier_struct_verif['Produits_d_exploitation_2025']} vs {df_financier['Financier Prod_2025'].sum()}")
    elif round(financier_struct_verif['Résultat_net_par_structure'], 2) != round(df_financier['Financier ResNet_2025'].sum(), 2):
        print(f"❌ Problème Résultat : {financier_struct_verif['Résultat_net_par_structure']} vs {df_financier['Financier ResNet_2025'].sum()}")
    else:
        print("✅ Produits & Résultat OK")

    # =========================
    # 🔹 TRÉSORERIE STRUCTURE
    # =========================
    treso = get_as_dataframe(financier_2025.worksheet('Tréso'), skiprows=2, evaluate_formulas=True)
    treso = treso.iloc[:treso.shape[0]-2]
    treso = treso[
        (treso['Trésorerie brute'] != '31/12/2025') &
        (treso['Avance de tréso en mois'] != '31/12/2025') &
        (treso['N° Structure'].notna()) &
        (treso['N° Structure'] != 'D')
    ]

    treso['Trésorerie brute'] = pd.to_numeric(treso['Trésorerie brute'], errors='coerce')

    total_treso_source = treso['Trésorerie brute'].sum()
    total_treso_df = df_financier['Financier TresoBrute_2025'].sum()

    if round(total_treso_source, 2) != round(total_treso_df, 2):
        print(f"❌ Trésorerie structure KO : {total_treso_source} vs {total_treso_df}")
    else:
        print("✅ Trésorerie structure OK")

    # =========================
    # 🔹 CAF STRUCTURE
    # =========================
    caf = get_as_dataframe(financier_2025.worksheet('CAF'), skiprows=3, evaluate_formulas=True)
    caf.columns = [''.join(c if c.isalnum() else '_' for c in str(col)) for col in caf.columns]
    caf = caf.rename(columns={'N__Structure': 'n_structure','Réalisé_2025_Total_Année': 'CAF_2025'})
    caf_struct = caf[(caf['n_structure'].notna()) & (caf['n_structure'] != 'D')]
    caf_struct['CAF_2025'] = pd.to_numeric(caf_struct['CAF_2025'], errors='coerce')

    total_caf_source = caf_struct['CAF_2025'].sum()
    total_caf_df = df_financier['Financier caf_2025'].sum()

    if round(total_caf_source, 2) != round(total_caf_df, 2):
        print(f"❌ CAF structure KO : {total_caf_source} vs {total_caf_df}")
    else:
        print("✅ CAF structure OK")

    # =========================
    # 🔹 Vérifications DT
    # =========================
    print('')
    print('Vérifications par DT :')
    verifier_colonne_structure(
        df_financier_DT,
        "n_structure",
        df_ref_structure[df_ref_structure['type_structure'].str.contains('DT')]
    )
    print('')

    # =========================
    # 🔹 TRÉSORERIE DT
    # =========================
    treso_dt = pd.merge(
        treso[['N° Dptmt','Trésorerie brute']].copy(),
        df_ref_structure[['n_dept','DT_de_rattachement']].drop_duplicates(),
        left_on='N° Dptmt',
        right_on='n_dept',
        how='inner'
    )
    treso_dt = treso_dt.groupby('DT_de_rattachement', as_index=False).agg({'Trésorerie brute':'sum'})
    total_treso_DT_source = treso_dt['Trésorerie brute'].sum()
    total_treso_DT_df = df_financier_DT['Financier TresoBrute_2025'].sum()

    if round(total_treso_DT_source, 2) != round(total_treso_DT_df, 2):
        print(f"❌ Trésorerie DT KO : {total_treso_DT_source} vs {total_treso_DT_df}")
    else:
        print("✅ Trésorerie DT OK")

    # =========================
    # 🔹 CAF DT
    # =========================
    caf_dt = pd.merge(
        caf[['n_structure','n_dept','CAF_2025']].copy(),
        df_ref_structure[['n_dept','DT_de_rattachement']].drop_duplicates(),
        on='n_dept',
        how='inner'
    )
    caf_dt = caf_dt[caf_dt['n_structure'] == 'D']
    caf_dt = caf_dt.groupby('DT_de_rattachement', as_index=False).agg({'CAF_2025':'sum'})

    total_caf_DT_source = caf_dt['CAF_2025'].sum()
    total_caf_DT_df = df_financier_DT['Financier caf_2025'].sum()

    if round(total_caf_DT_source, 2) != round(total_caf_DT_df, 2):
        print(f"❌ CAF DT KO : {total_caf_DT_source} vs {total_caf_DT_df}")
    else:
        print("✅ CAF DT OK")
    


    








#################################################################
# 
# DPS, FGP et Textile
# 
# ###############################################################

def indicateur_financier_DPS_2025(financier_DPS, df_ref_structure):

    structures = df_ref_structure['n_structure'].drop_duplicates().tolist()
    df_financier_DPS = financier_DPS.copy().rename(columns={"N_structure":"n_structure","Produits d'exploitation 2025" : "Secours Produits_DPS_2025"})
    df_financier_DPS = df_financier_DPS[['n_structure','Secours Produits_DPS_2025']].apply(pd.to_numeric, errors='coerce')
    df_financier_DPS = df_financier_DPS[df_financier_DPS['n_structure'].isin(structures)]

    DTs = df_ref_structure[df_ref_structure['type_structure'] == "DELEGATION TERRITORIALE - DT"]['n_structure'].drop_duplicates().tolist()
    df_financier_DPS_DT = financier_DPS.copy().rename(columns={"N_structure":"n_structure","Produits d'exploitation consolidés (DT)" : "Secours Produits_DPS_2025"})
    df_financier_DPS_DT = df_financier_DPS_DT[['n_structure','Secours Produits_DPS_2025']].apply(pd.to_numeric, errors='coerce')
    df_financier_DPS_DT = df_financier_DPS_DT[df_financier_DPS_DT['n_structure'].isin(DTs)]

    return df_financier_DPS, df_financier_DPS_DT




def indicateur_financier_FGP_2024(financier_FGP, df_ref_structure):
  mapping_dict = df_ref_structure[df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"].set_index('n_dept')['n_structure'].to_dict()

  # Suppression de la ligne nationnale
  df_financier_FGP_DT = financier_FGP[financier_FGP["Nom Structure"] != "Total"]
  df_financier_FGP_DT = df_financier_FGP_DT[df_financier_FGP_DT["N° Structure"] != "Source: Smartview-Mise à jour 24 mars 2025"]
  df_financier_FGP_DT = df_financier_FGP_DT.dropna(subset=["Nom Structure"])
  df_financier_FGP_DT = df_financier_FGP_DT.rename(columns={"N° Structure": "n_dept"})
  df_financier_FGP_DT = df_financier_FGP_DT.iloc[:df_financier_FGP_DT.shape[0]-2]
  df_financier_FGP_DT["n_dept"] = df_financier_FGP_DT["n_dept"].astype('str')

  df_ref_structure["n_dept"] = df_ref_structure["n_dept"].astype('str')

    
  df_financier_FGP_DT["Nom Structure"] = "DT " + df_financier_FGP_DT["Nom Structure"].astype(str)
  df_financier_FGP_DT['n_dept'] = df_financier_FGP_DT['n_dept'].apply(dept_clean)
  df_financier_FGP_DT = pd.merge(df_ref_structure[df_ref_structure['type_structure'] == "DELEGATION TERRITORIALE - DT"][['DT_de_rattachement','n_dept']].drop_duplicates(), df_financier_FGP_DT, on = 'n_dept', how = 'inner')

  df_financier_FGP_DT = df_financier_FGP_DT.drop_duplicates(['DT_de_rattachement'])
  # financier_FGP = rapprochement_libelles(
  #     df_ref_structure,
  #     financier_FGP,
  #     "Nom Structure"
  # )
  df_financier_FGP_DT = df_financier_FGP_DT.rename(columns={
    'Réalisé 2024 Total Année': 'Formation_grand_public CA_2024' ,
    'DT_de_rattachement' : 'n_structure'
  })
  # Conserver les colonnes utiles

  df_financier_FGP_DT = df_financier_FGP_DT[["n_structure",'n_dept',"Formation_grand_public CA_2024"]]
  df_financier_FGP_DT = df_financier_FGP_DT.rename(columns = {'Formation_grand_public CA_2024' : 'Formation_grand_public Produits_2025'})


  #verifier_mapping(financier_FGP, "n_structure", "Nom Structure" ,df_ref_structure)
  return df_financier_FGP_DT








def financier_FGP_DT(df_financier_FGP_indicateur, rattachement_court):
    df_financier_FGP_indicateur['n_structure'] = df_financier_FGP_indicateur['n_structure'].astype('float64')
    # Merge données avec rattachement_court
    df_financier_FGP = pd.merge(
    df_financier_FGP_indicateur,
    rattachement_court,
    on="n_structure",
    how="left"
    )




    # Groupby sur DT_de_rattachement
    financier_FGP_DT = (df_financier_FGP.groupby('DT_de_rattachement')['Formation_grand_public Produits_2025'].sum())
    return financier_FGP_DT



def indicateur_financier_Textile_2025(financier_Textile, df_ref_structure):

    structures = df_ref_structure['n_structure'].drop_duplicates().tolist()
    df_financier_Textile = financier_Textile.copy().rename(columns={"N_structure":"n_structure","Produits d'exploitation 2025" : "Textile Produit_2025"})
    df_financier_Textile = df_financier_Textile[['n_structure','Textile Produit_2025']].apply(pd.to_numeric, errors='coerce')
    df_financier_Textile = df_financier_Textile[df_financier_Textile['n_structure'].isin(structures)]

    DTs = df_ref_structure[df_ref_structure['type_structure'] == "DELEGATION TERRITORIALE - DT"]['n_structure'].drop_duplicates().tolist()
    df_financier_Textile_DT = financier_Textile.copy().rename(columns={"N_structure":"n_structure","Produits d'exploitation consolidés (DT)" : "Textile Produit_2025"})
    df_financier_Textile_DT = df_financier_Textile_DT[['n_structure','Textile Produit_2025']].apply(pd.to_numeric, errors='coerce')
    df_financier_Textile_DT = df_financier_Textile_DT[df_financier_Textile_DT['n_structure'].isin(DTs)]

    return df_financier_Textile, df_financier_Textile_DT


############################################
######## OBSOLETE - VERSION 2024 ###########
############################################

def indicateur_financier_DPS_2024(financier_DPS, df_ref_structure):
    # Filtrer sur la bonne année
  df_Secours_ProduitsDPS = financier_DPS[financier_DPS['annee'] == 2024]

  # Filtrer sur l'activité DPS
  df_Secours_ProduitsDPS = df_Secours_ProduitsDPS[df_Secours_ProduitsDPS['imputation_comptable'] == "ACTA204"]

  # Extraire le département
  def extraire_et_nettoyer_code_departement(texte):
      code = texte[-3:] # Extraire les 3 derniers caractères
      code = code.lstrip('0') # Supprimer les zéros initiaux
      return code
  df_Secours_ProduitsDPS['Code Département'] = df_Secours_ProduitsDPS['code_comptable'].apply(extraire_et_nettoyer_code_departement)

  # Suppression de la ligne nationnale
  df_Secours_ProduitsDPS = df_Secours_ProduitsDPS[df_Secours_ProduitsDPS["libelle"] != "TOTAL DELEGATION"]

  # Suppression des doublons (corse)
  df_Secours_ProduitsDPS = df_Secours_ProduitsDPS.drop_duplicates(subset=['Code Département'], keep='first')

  # Conserver les colonnes utiles
  df_Secours_ProduitsDPS = df_Secours_ProduitsDPS[["code_comptable","libelle","Code Département","annee","imputation_comptable","PRODUITS DES POSTES SECOURS"]]

  # Mapping sur le département
  mapping_dict = df_ref_structure[df_ref_structure["type_structure"] == "DELEGATION TERRITORIALE - DT"].set_index('n_dept')['n_structure'].to_dict()
  df_Secours_ProduitsDPS['n_structure'] = df_Secours_ProduitsDPS['Code Département'].map(mapping_dict)
  verifier_mapping(df_Secours_ProduitsDPS, "n_structure", "libelle" ,df_ref_structure)

  # Transformation des str en int
  financier_DPS['PRODUITS DES POSTES SECOURS'] = (
      financier_DPS['PRODUITS DES POSTES SECOURS']
          .astype(str)
          .str.replace("€", "", regex=False)
          .str.replace("\u202f", "", regex=False)  # espace insécable fin
          .str.replace(" ", "", regex=False)
          .replace("nan", 0)
          .replace("", 0)
          .pipe(pd.to_numeric, errors="coerce")
          .fillna(0)
          .astype(int)
  )

  # Conserver les colonnes utiles
  df_Secours_ProduitsDPS = df_Secours_ProduitsDPS[["n_structure","PRODUITS DES POSTES SECOURS"]]

  # Modification du nom de colonne
  df_Secours_ProduitsDPS = df_Secours_ProduitsDPS.rename(columns={"PRODUITS DES POSTES SECOURS":"Secours Produits_DPS_2025"})

  return df_Secours_ProduitsDPS



def financier_DPS_DT(df_financier_DPS_indicateur, rattachement_court):
    df_financier_DPS_indicateur['n_structure'] = df_financier_DPS_indicateur['n_structure'].astype('float64')
    # Merge données avec rattachement_court
    df_financier_DPS = pd.merge(
    df_financier_DPS_indicateur,
    rattachement_court,
    on="n_structure",
    how="left"
    )




    # Groupby sur DT_de_rattachement
    financier_DPS_DT = (df_financier_DPS.groupby('DT_de_rattachement')['Secours Produits_DPS_2025'].sum())
    return financier_DPS_DT















