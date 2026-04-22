import os
import sys
import pandas as pd
from typing import List, Dict
from functools import reduce

sys.path.append(os.path.abspath("./checks")) 

from helpers import *

from utils import *


def merge_left_on_df1(df1, l, on):

    def safe_merge(left, right):
        # Supprime les colonnes déjà présentes (sauf la clé)
        cols_to_drop = [col for col in right.columns if col in left.columns and col != on]
        right_clean = right.drop(columns=cols_to_drop)

        return left.merge(right_clean, how='left', on=on)

    return reduce(safe_merge, l, df1)

def traitement_all_data(liste_df_a_fusionner_toutes_structures, liste_df_a_fusionner_DT, df_ref_structure,df_ref_structure_DT):
  colonnes_indicateurs = ['n_structure',
    "Financier Prod_2023",
    "Financier ResNet_2023",
    "Financier ResCorrProd_2023",
    "Financier Prod_2024",
    "Financier ResNet_2024",
    "Financier ResCorrProd_2024",
    "Financier Prod_2025",
    "Financier ResNet_2025",
    "Financier ResCorrProd_2025",
    "Financier TresoBrute_2025",
    "Financier Mois_AvanceTreso_2025",
    "Financier caf_2025",
    "Structure Nb_Benevoles",
    "Structure Nb_nvx_Benevoles_2025",
    "Structure Nb_Adherents",
    "Structure Nb_formes_TCAS_2025",
    "Structure Nb_formes_CRB_2025",
    "Structure Taux_formation_CRB",
    "Structure Nb_nvx_formes_CRB_2025",
    "Structure Nb_formateurs_CRB_2025",
    "Dispositifs_d_urgence Structures_menant_activite_TCAU",
    "Dispositifs_d_urgence Structures_menant_activite_PSP",
    "Dispositifs_d_urgence Structures_menant_activite_GQS",
    "Dispositifs_d_urgence Nb_conventions_prefecture",
    "Dispositifs_d_urgence Nb_conventions_operateurs",
    "Dispositifs_d_urgence Nb_agrements",
    "Dispositifs_d_urgence Nb_declenchements",
    "Dispositifs_d_urgence Nb_operations",
    "Dispositifs_d_urgence Nb_personnes_prises_charge",
    "Dispositifs_d_urgence Nb_lots_CAI",
    "Dispositifs_d_urgence Nb_lots_CHU",
    "Dispositifs_d_urgence Nb_lots_CMCC",
    "Dispositifs_d_urgence Utilisation_RedCall",
    "Dispositifs_d_urgence Utilisation_Minutis",
    "Dispositifs_d_urgence Nb_exercices",
    "Dispositifs_d_urgence PST",
    "Dispositifs_d_urgence Nb_formes_TCAU_2025",
    "Dispositifs_d_urgence Nb_formes_TCEO_2025",
    "Dispositifs_d_urgence Nb_formes_IPSP_2025",
    "Dispositifs_d_urgence Nb_formes_IRR_2025",
    "Dispositifs_d_urgence Nb_formes_GQS_2025",
    "Dispositifs_d_urgence Taux_formation_TCAU_2025",
    "Dispositifs_d_urgence Taux_formation_IPSP_2025",
    "Dispositifs_d_urgence Taux_formation_GQS_2025",
    "Dispositifs_d_urgence Taux_formation_TCEO_2025",
    "Dispositifs_d_urgence Taux_formation_IRR_2025",
    "Formation_grand_public Nb_FPSC",
    "Formation_grand_public Structures_menant_activite",
    "Formation_grand_public Produits_2025",
    "Dispositifs_d_urgence Nb_formes_PSP_2025",
    "Secours Nb_sessions_PSE",
    "Secours Nb_sessions_CI",
    "Secours Nb_sessions_FPSE",
    "Formation_grand_public Nb_formes_PSC_2025",
    "Formation_grand_public Nb_sessions_PSC_2025",
    "Formation_grand_public Nb_FPSC",
    "Formation_grand_public Nb_formes_GQS_2025",
    "Formation_grand_public Nb_sessions_GQS_2025",
    "Formation_grand_public Nb_AGQS",
    "Formation_grand_public Nb_formes_IPSEN_2025",
    "Formation_grand_public Nb_sessions_IPSEN_2025",
    "Formation_grand_public Nb_FIPSEN",
    "Formation_grand_public Nb_formes_IPS_2025",
    "Formation_grand_public Nb_sessions_IPS_2025",
    "Formation_grand_public Nb_formes_PREVIC_2025",
    "Formation_grand_public Nb_sessions_PREVIC_2025",
    "Formation_grand_public Activite_Conso_Etat",
    "Formation_grand_public Activite_Conso_Non_Etat",
    "OCR Structures_menant_activite",
    "OCR Nb_deployees",
    "OCR Nb_referents",
    "nb_Maraude_Pegass",
    "Maraude Nb_maraudes_SIGMA",
    "Maraudes Structures_menant_activite",
    "Maraude Nb_benevoles_actifs",
    "Maraude Nb_benevoles_actifs_formes",
    "Maraude Nb_SOLIDAR",
    "Maraude Nb_SOLIDAR2020",
    "Maraude Nb_contacts",
    "Maraude Nb_personnes_rencontrees",
    "Secours Produits_DPS_2025",
    "Secours Structures_menant_activite",
    "Secours Nb_DPS_2025",
    "Secours Nb_agrements_DPS_2025",
    "Secours Taux_IS_actifs",
    "Secours Nb_PAPS_2025",
    "Secours Nb_DPS_PE_2025",
    "Secours Nb_DPS_ME_2025",
    "Secours Nb_DPS_GE_2025",
    "Secours Nb_PSE1",
    "Secours Nb_PSE2",
    "Secours Nb_CI",
    "Secours Taux_recy26_PSE1",
    "Secours Taux_recy26_PSE2",
    "Secours Taux_recy26_CI",
    "Secours Taux_ren25_PSE1",
    "Secours Taux_ren25_PSE2",
    "Secours Taux_ren25_CI",
    "Secours Nb_sessions_PSE",
    "Secours Nb_sessions_CI",
    "Secours Nb_sessions_FPSE",
    "AEO Structures_menant_activite",
    "AEO Structure_activite_fixe",
    "AEO Structure_activite_mobile",
    "AEO Nb_benevoles_actifs",
    "AEO Nb_responsables",
    "AEO Nb_AAD",
    "AEO Nb_FAAD",
    "AEO Nb_PA_AEO_AAD",
    "AEO Nb_personnes_domiciliees_crf",
    "AEO Nb_PA_dispos_mobiles",
    "AEO Structure_domiciliation_fixe",
    "AEO Structure_ecrivain_public_fixe",
    'Activités AAD facultatives',
    "Aide_alimentaire Nb_U2A",
    "Aide_alimentaire Nb_Centre_distribution_alimentaire",
    "Aide_alimentaire Nb_epiceries_sociales",
    "Aide_alimentaire Nb_crsr",
    "Textile Nb_dispositifs",
    "Textile Produit_2025",
    "Textile Resultat_2025",
    "IS Nb_benevoles_actifs",
    "Dispositifs_d_urgence Nb_agrements2",
    "Dispositifs_d_urgence Nb_operations2",
    "Dispositifs_d_urgence Nb_personnes_prises_charge2",
    "Dispositifs_d_urgence Nb_exercices2",
    "Dispositifs_d_urgence Nb_personnes_prises_charge2",
    "Secours Nb_agrements_DPS_2025_2",
    'Dispositifs_d_urgence Structures_menant_activite_TCAU',
    'Dispositifs_d_urgence Structures_menant_activite_PSP',
    'Dispositifs_d_urgence Structures_menant_activite_GQS'
  ]

  mask = df_ref_structure['n_structure'].to_list()

  print("TRAITEMENT DES INDICATEURS POUR TOUTES LES STRUCTURES")
  print('')
  for i,df in enumerate(liste_df_a_fusionner_toutes_structures):

    # Transformation des Series en DataFrame
    if type(liste_df_a_fusionner_toutes_structures[i]) != type(df_ref_structure):
      liste_df_a_fusionner_toutes_structures[i] = liste_df_a_fusionner_toutes_structures[i].to_frame()
    if len(liste_df_a_fusionner_toutes_structures[i].columns) < 2:
      liste_df_a_fusionner_toutes_structures[i] = liste_df_a_fusionner_toutes_structures[i].reset_index()

    # Uniformisation des types pour la clé n_structure
    
    if liste_df_a_fusionner_toutes_structures[i]['n_structure'].dtype != df_ref_structure['n_structure'].dtype:
      liste_df_a_fusionner_toutes_structures[i]['n_structure'] = liste_df_a_fusionner_toutes_structures[i]['n_structure'].astype(int)
    cleaned_dfs = []

    # Colonnes à supprimer
    cols_to_drop = [col for col in liste_df_a_fusionner_toutes_structures[i].columns if col not in colonnes_indicateurs]

    if cols_to_drop:
        print(f"🧹 DataFrame {i} : suppression des colonnes {cols_to_drop}")

    df_clean = liste_df_a_fusionner_toutes_structures[i].drop(columns=cols_to_drop)

    liste_df_a_fusionner_toutes_structures[i] = df_clean

    # Filtre des n_structure
    
    liste_df_a_fusionner_toutes_structures[i] = liste_df_a_fusionner_toutes_structures[i][liste_df_a_fusionner_toutes_structures[i]['n_structure'].isin(mask)]
  duplicates = find_duplicates_in_list_of_dfs(liste_df_a_fusionner_toutes_structures, column='n_structure')

  all_data  = merge_left_on_df1(df_ref_structure, liste_df_a_fusionner_toutes_structures, on = 'n_structure')

  
  print("TRAITEMENT DES INDICATEURS POUR LES DTs")
  print('')
  for i,df in enumerate(liste_df_a_fusionner_DT):

    # Transformation des Series en DataFrame
    if type(liste_df_a_fusionner_DT[i]) != type(df_ref_structure):
      liste_df_a_fusionner_DT[i] = liste_df_a_fusionner_DT[i].to_frame()
    if len(liste_df_a_fusionner_DT[i].columns) < 2:
      liste_df_a_fusionner_DT[i] = liste_df_a_fusionner_DT[i].reset_index()

    # Uniformisation des types pour la clé n_structure
    if 'n_structure' not in liste_df_a_fusionner_DT[i].columns:
      if 'DT_de_rattachement' in liste_df_a_fusionner_DT[i].columns:
        liste_df_a_fusionner_DT[i] = liste_df_a_fusionner_DT[i].rename(columns={'DT_de_rattachement': 'n_structure'})

    # Garder seulement les nombres
    if liste_df_a_fusionner_DT[i]['n_structure'].dtype == 'object':
      contient_lettres = liste_df_a_fusionner_DT[i]['n_structure'].astype(str).str.contains(r'[A-Za-z]', na=False).any()
      if contient_lettres:
        liste_df_a_fusionner_DT[i]['n_structure'] = liste_df_a_fusionner_DT[i]['n_structure'].apply(keep_integer).astype(int)
    
    if liste_df_a_fusionner_DT[i]['n_structure'].dtype != df_ref_structure['n_structure'].dtype:
      liste_df_a_fusionner_DT[i]['n_structure'] = liste_df_a_fusionner_DT[i]['n_structure'].astype(int)


    # Colonnes à supprimer
    cols_to_drop = [col for col in liste_df_a_fusionner_DT[i].columns if col not in colonnes_indicateurs]

    if cols_to_drop:
        print(f"🧹 DataFrame {i} : suppression des colonnes {cols_to_drop}")

    df_clean = liste_df_a_fusionner_DT[i].drop(columns=cols_to_drop)

   
    liste_df_a_fusionner_DT[i] = df_clean

    # Filtre des n_structure
    liste_df_a_fusionner_DT[i] = liste_df_a_fusionner_DT[i][liste_df_a_fusionner_DT[i]['n_structure'].isin(mask)]

  duplicates = find_duplicates_in_list_of_dfs(liste_df_a_fusionner_DT, column='n_structure')
  all_data_DT  = merge_left_on_df1(df_ref_structure_DT, liste_df_a_fusionner_DT, on = 'n_structure')
  


  return all_data, all_data_DT, liste_df_a_fusionner_toutes_structures, liste_df_a_fusionner_DT


def ajouter_colonnes_taux(df: pd.DataFrame, denominateur: str) -> pd.DataFrame:
    """
    Ajoute des colonnes calculées comme (colonne / denominateur).

    Les noms des nouvelles colonnes sont définis en dur dans la fonction.
    """
    colonnes = ["Dispositifs_d_urgence Nb_formes_TCAU_2025","Dispositifs_d_urgence Nb_formes_TCEO_2025",
    "Dispositifs_d_urgence Nb_formes_PSP_2025", "Dispositifs_d_urgence Nb_formes_IRR_2025", "Dispositifs_d_urgence Nb_formes_GQS_2025",
    "Structure Nb_formes_CRB_2025"]
    # ⚠️ noms hardcodés (modifie-les ici selon ton besoin)
    mapping_noms = {
        "Dispositifs_d_urgence Nb_formes_TCAU_2025": "Dispositifs_d_urgence Taux_formation_TCAU_2025",
        "Dispositifs_d_urgence Nb_formes_TCEO_2025": "Dispositifs_d_urgence Taux_formation_TCEO_2025",
        "Dispositifs_d_urgence Nb_formes_PSP_2025": "Dispositifs_d_urgence Taux_formation_PSP_2025",
        "Dispositifs_d_urgence Nb_formes_IRR_2025" : "Dispositifs_d_urgence Taux_formation_IRR_2025",
        "Dispositifs_d_urgence Nb_formes_GQS_2025" : "Dispositifs_d_urgence Taux_formation_GQS_2025",
        "Structure Nb_formes_CRB_2025" : "Structure Taux_formation_CRB"
    }

    for col in colonnes:
        if col not in df.columns:
            raise ValueError(f"Colonne absente du dataframe : {col}")
        if denominateur not in df.columns:
            raise ValueError(f"Colonne denominateur absente : {denominateur}")

        if col not in mapping_noms:
            raise ValueError(f"Aucun nom hardcodé prévu pour {col}")

        nouveau_nom = mapping_noms[col]
        df[nouveau_nom] = df[col] / df[denominateur]

    return df

def ajouter_colonne_somme(df: pd.DataFrame, col1: str, col2: str) -> pd.DataFrame:
  
    # nom hardcodé de la nouvelle colonne
    nom_nouvelle_colonne = "AEO Nb_PA_AEO_AAD"
    
    df[nom_nouvelle_colonne] = df[col1] + df[col2]
    return df

def vision_conso(df_alldata, df_alldata_DT):
  # sélection des colonnes pour vision consolidée FPG

  formations_certifiantes = [
      'Formation_grand_public Nb_formes_PSC_2025',
      'Formation_grand_public Nb_formes_GQS_2025',
      'Formation_grand_public Nb_sessions_PSC_2025',
      'Formation_grand_public Nb_sessions_GQS_2025'
  ]

  df_alldata['Formation_grand_public Activite_Conso_Etat'] = (
      df_alldata[formations_certifiantes]
      .fillna(0)
      .sum(axis=1)
      .gt(0)
      .map({True: 'Action menée', False: 'Non menée'})
  )



  formations_non_certifiantes = [
      'Formation_grand_public Nb_formes_IPSEN_2025',
      'Formation_grand_public Nb_formes_IPS_2025',
      'Formation_grand_public Nb_formes_PREVIC_2025',
      'Formation_grand_public Nb_sessions_IPSEN_2025',
      'Formation_grand_public Nb_sessions_IPS_2025',
      'Formation_grand_public Nb_sessions_PREVIC_2025'
  ]

  df_alldata['Formation_grand_public Activite_Conso_Non_Etat'] = (
      df_alldata[formations_non_certifiantes]
      .fillna(0)
      .sum(axis=1)
      .gt(0)
      .map({True: 'Action menée', False: 'Non menée'})
  )



  # df_alldata['vision_territoriale_activite_DPS'] = (
  #     df_alldata['Secours Nb_DPS_2025']
  #     .fillna(0)
  #     .sum(axis=1)
  #     .gt(0)
  #     .map({True: 'Action menée', False: 'Non menée'})
  # )


  formations_secours = [
      'Secours Nb_PSE1',
      'Secours Nb_PSE2',
      'Secours Nb_CI'
  ]

  # df_alldata['vision_territoriale_formation_DPS'] = (
  #     df_alldata['formations_secours']
  #     .fillna(0)
  #     .sum(axis=1)
  #     .gt(0)
  #     .map({True: 'Action menée', False: 'Non menée'})
  # )




  # Ajout du 'Action non menée' sur les autres colonnes

  colonnes_non_menee = [
      'OCR Nb_deployees',
      'Maraude Nb_maraudes_SIGMA',
      # 'Secours Nb_DPS_2025',
      'Textile Nb_dispositifs',
      'Aide_alimentaire Nb_U2A'
  ]

  df_alldata[colonnes_non_menee] = df_alldata[colonnes_non_menee].astype(str)
  df_alldata[colonnes_non_menee] = (
      df_alldata[colonnes_non_menee]
      .fillna('Non menée')
  )



  # Nb de structures menant l'activité

  colonnes_nb_structure = [
    (('OCR Nb_deployees',), 'OCR Structures_menant_activite'),
    (('Secours Nb_DPS_2025','Secours Nb_PAPS_2025','Secours Nb_DPS_PE_2025','Secours Nb_DPS_ME_2025','Secours Nb_DPS_GE_2025'), 'Secours Structures_menant_activite'),
    (('Secours Nb_PSE1','Secours Nb_PSE2','Secours Nb_CI'), 'Secours Structures_menant_activite_formes'),
    (('Secours Nb_sessions_PSE','Secours Nb_sessions_CI','Secours Nb_sessions_FPSE'), 'Secours Structures_menant_activite_sessions'),
    (('nb_Maraude_Pegass',), 'Maraudes Structures_menant_activite'),
    # (('Dispositifs_d_urgence Nb_formes_TCAU_2025',), 'Dispositifs_d_urgence Structures_menant_activite_TCAU'),
    # (('Dispositifs_d_urgence Nb_formes_PSP_2025',), 'Dispositifs_d_urgence Structures_menant_activite_PSP'),
    # (('Dispositifs_d_urgence Nb_formes_GQS_2025',), 'Dispositifs_d_urgence Structures_menant_activite_GQS'),

  ]
  colonnes_actions = [col_output for _, col_output in colonnes_nb_structure]

  for cols_input, col_output in colonnes_nb_structure:
      
      # garantir un tuple même si une seule colonne
      if isinstance(cols_input, str):
          cols_input = (cols_input,)
      
      # conversion numérique
      df_alldata[list(cols_input)] = df_alldata[list(cols_input)].apply(
          pd.to_numeric, errors='coerce'
      )
      
      # 1 si au moins une valeur > 0
      df_alldata[col_output] = (df_alldata[list(cols_input)] > 0).any(axis=1).astype(int)

  df_grouped = (
    df_alldata[['DT_de_rattachement'] + colonnes_actions]
    .groupby('DT_de_rattachement')[colonnes_actions]
    .sum()
    .reset_index()
  )



  for _, col_output in colonnes_nb_structure:
    df_alldata[col_output] = df_alldata[col_output].map({
        1: 'Action menée',
        0: 'Action non menée'
    })
 

  df_grouped = df_grouped[colonnes_actions + ['DT_de_rattachement']]

  df_alldata_DT = pd.merge(df_alldata_DT, df_grouped, on='DT_de_rattachement', how='left')

  #Partie structure menant activite AEO

  df_alldata["AEO Structure_activite_mobile"] = df_alldata["AEO Structure_activite_mobile"].astype(object)
  df_alldata.loc[df_alldata["AEO Structure_activite_mobile"].notna(), ["AEO Structure_activite_mobile"]] = "Activité AEO/AAD en dispositif mobile"
  
  
  fixe = df_alldata["AEO Structure_activite_fixe"]
  mobile = df_alldata["AEO Structure_activite_mobile"]
  
  df_alldata["AEO Structures_menant_activite"] = (
      fixe.fillna("").astype(str).str.strip()
      + " | " +
      mobile.fillna("").astype(str).str.strip()
  ).str.strip(" |")
  
  df_alldata["AEO Structures_menant_activite"] =df_alldata["AEO Structures_menant_activite"].replace('Activités AEO/AAD menée en fixe | Activité AEO/AAD en dispositif mobile',"Activité AEO en site fixe et en dispositif mobile")
  
  df_alldata["AEO Structures_menant_activite"] =df_alldata["AEO Structures_menant_activite"].replace('Activités AEO/AAD menée en fixe',"Activité AEO en site fixe")

  df_alldata["AEO Structures_menant_activite"] =df_alldata["AEO Structures_menant_activite"].replace("Activité AEO/AAD en dispositif mobile","Activité AEO en dispositif mobile")
  
  df_alldata["AEO Structures_menant_activite"] =df_alldata["AEO Structures_menant_activite"].replace('','Activité AEO non menée')

  df_grouped = (
      df_alldata[['DT_de_rattachement',"AEO Structures_menant_activite"]]
      .groupby('DT_de_rattachement')["AEO Structures_menant_activite"]
      .apply(lambda x: (x != "Activité AEO non menée").sum())
      .reset_index()
  )

  df_alldata_DT = pd.merge(df_alldata_DT, df_grouped, on='DT_de_rattachement', how='left')  




  # Structures menant activité

  df_alldata['Formation_grand_public Activite_Conso_Etat'] = df_alldata['Formation_grand_public Activite_Conso_Etat'].fillna('')
  df_alldata['Formation_grand_public Activite_Conso_Non_Etat'] = df_alldata['Formation_grand_public Activite_Conso_Non_Etat'].fillna('')
  df_alldata['Formation_grand_public Structures_menant_activite'] = df_alldata[['Formation_grand_public Activite_Conso_Etat', 'Formation_grand_public Activite_Conso_Non_Etat']].apply(
      lambda row: 1
      if (row['Formation_grand_public Activite_Conso_Etat'] == "Action menée") or (row['Formation_grand_public Activite_Conso_Non_Etat'] == "Action menée")
      else 0 ,
      axis=1
  )

  df_grouped = (
      df_alldata[['DT_de_rattachement','Formation_grand_public Structures_menant_activite']]
      .groupby('DT_de_rattachement')['Formation_grand_public Structures_menant_activite']
      .sum()
      .reset_index()
  )
  df_alldata['Formation_grand_public Structures_menant_activite'] = df_alldata['Formation_grand_public Structures_menant_activite'].map({1: 'Action menée', 0: 'Action non menée'})

  df_alldata_DT = pd.merge(df_alldata_DT, df_grouped, on='DT_de_rattachement', how='left')  

  return df_alldata, df_alldata_DT