import os
import sys
import pandas as pd
from typing import List, Dict
from functools import reduce

sys.path.append(os.path.abspath("../checks")) 

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

def traitement_all_data(liste_df_a_fusionner_toutes_structures, liste_df_a_fusionner_DT, df_ref_structure,df_ref_structure_DT,year):
  colonnes_indicateurs = ['n_structure',
    f"Financier Prod_{year-3}",
    f"Financier ResNet_{year-3}",
    f"Financier ResCorrProd_{year-3}",
    f"Financier Prod_{year-2}",
    f"Financier ResNet_{year-2}",
    f"Financier ResCorrProd_{year-2}",
    "Structure Nb_Benevoles",
    f"Structure Nb_nvx_Benevoles_{year}",
    "Structure Nb_Adherents",
    f"Structure Nb_formes_CRB_{year}",
    "Structure Taux_formation_CRB",
    f"Structure Nb_nvx_formes_CRB_{year}",
    f"Structure Nb_formateurs_CRB_{year}",
    f"Structure Nb_formes_TCAS_{year}",
    "Structure Taux_nvx_Benevoles",

    "Dispositifs_d_urgence Nb_conventions_prefecture",
    "Dispositifs_d_urgence Nb_conventions_operateurs",
    "Dispositifs_d_urgence Nb_conventions_operateurs_publics",
    "Dispositifs_d_urgence Nb_conventions_operateurs_prives",
    "Dispositifs_d_urgence Nb_declenchements",
    "Dispositifs_d_urgence Nb_operations",
    "Dispositifs_d_urgence Nb_jours_operations",
    "Dispositifs_d_urgence Ope_secours",
    "Dispositifs_d_urgence Ope_soutien_pop",
    "Dispositifs_d_urgence Nb_personnes_prises_charge",
    "Dispositifs_d_urgence Nb_lots_CAI",
    "Dispositifs_d_urgence Nb_lots_CHU",
    "Dispositifs_d_urgence Nb_lots_CMCC",
    "Dispositifs_d_urgence Utilisation_RedCall",
    "Dispositifs_d_urgence Utilisation_Minutis",
    "Dispositifs_d_urgence Nb_exercices",
    "Dispositifs_d_urgence PST",
    f"Dispositifs_d_urgence Taux_formation_TCAU_{year}",
    f"Dispositifs_d_urgence Taux_formation_PSP_{year}",
    f"Dispositifs_d_urgence Taux_formation_GQS_{year}",
    f"Dispositifs_d_urgence Taux_formation_TCEO_{year}",
    f"Dispositifs_d_urgence Taux_formation_IRR_{year}",

    "Formation_grand_public Structures_menant_activite",
    "Formation_grand_public Activite_Conso_Etat",
    "Formation_grand_public Activite_Conso_Non_Etat",
    "Formation_grand_public Produits_2025",
    f"Formation_grand_public Nb_formes_PSC_{year}",
    f"Formation_grand_public Nb_formes_GQS_{year}",
    f"Formation_grand_public Nb_formes_IPSEN_{year}",
    f"Formation_grand_public Nb_formes_IPS_{year}",
    "Formation_grand_public Nb_FPSC",
    "Formation_grand_public Nb_AGQS",
    "Formation_grand_public Nb_FIPSEN",
    f"Formation_grand_public Nb_sessions_PSC_{year}",
    f"Formation_grand_public Nb_sessions_GQS_{year}",
    f"Formation_grand_public Nb_sessions_IPSEN_{year}",
    f"Formation_grand_public Nb_sessions_IPS_{year}",

    "OCR Nb_deployees",
    "OCR Structures_menant_activite",
    "OCR Nb_referents",

    "Maraude Nb_maraudes_PEGASS",
    "Maraude Nb_maraudes_SIGMA",
    "Maraudes Structures_menant_activite",
    "Maraude Nb_benevoles_actifs",
    "Maraude Nb_benevoles_actifs_formes",
    "Maraude Nb_SOLIDAR",
    "Maraude Nb_SOLIDAR2020",
    "Maraude Nb_contacts",
    "Maraude Nb_personnes_rencontrees",

    "Secours Nb_IS",
    "Secours Nb_PSE1",
    "Secours Nb_PSE2",
    "Secours Nb_CI",
    "Secours Nb_FPSE",
    f"Secours Taux_recy{year+1-2000}_PSE1",
    f"Secours Taux_recy{year+1-2000}_PSE2",
    f"Secours Taux_recy{year+1-2000}_CI",
    f"Secours Taux_recy{year+1-2000}_FPSE",
    f"Secours Taux_ren{year-2000}_PSE1",
    f"Secours Taux_ren{year-2000}_PSE2",
    f"Secours Taux_ren{year-2000}_CI",
    f"Secours Taux_ren{year-2000}_FPSE",
    "Secours Taux_IS_actifs",
    "Secours Nb_sessions_PSE",
    "Secours Nb_sessions_CI",
    "Secours Nb_sessions_FPSE",
    "Secours Nb_DPS_ps_2025",
    "Secours Nb_PAPS_ps_2025",
    "Secours Nb_DPS_PE_ps_2025",
    "Secours Nb_DPS_ME_ps_2025",
    "Secours Nb_DPS_GE_ps_2025",
    "Secours Nb_agrements_DPS_2025",
    "Secours Nb_PAPS_2025",
    "Secours Nb_DPS_PE_2025",
    "Secours Nb_DPS_ME_2025",
    "Secours Nb_DPS_GE_2026",
    "Secours Produits_DPS_2025",
    "Secours Structures_menant_activite",

    "AEO Structures_menant_activite",
    "AEO Structure_activite_fixe",
    "AEO Structure_activite_mobile",
    "AEO Nb_activites_fixes",
    "AEO Nb_activites_mobiles",
    "AEO Structure_ecrivain_public_fixe",
    "AEO Structure_domiciliation_fixe",
    "AEO Nb_benevoles_actifs",
    "AEO Nb_responsables",
    "AEO Nb_AAD",
    "AEO Nb_FAAD",
    "AEO Nb_PA_dispos_mobiles",
    "AEO Nb_personnes_domiciliees_crf",

    "Aide_alimentaire Nb_U2A",
    "Aide_alimentaire Nb_Centre_distribution_alimentaire",
    "Aide_alimentaire Nb_epiceries_sociales",
    "Aide_alimentaire Nb_crsr",
    "Aide_alimentaire nb_EBP",
    "Aide_alimentaire nb_PA",
    "Aide_alimentaire nb_tonnes",
    "Aide_alimentaire nb_distributions",
    "Aide_alimentaire nb_SAH",

    "Textile Structures_menant_activite",
    "Textile Nb_boutiques",
    "Textile Nb_vestiaires",
    "Textile Produit_2025",
    "Textile tracabilite_flux",
    "Textile Vente_solidaire",
    "Textile Animateurs_textile",

    f"Financier Prod_{year-1}",
    f"Financier ResNet_{year-1}",
    f"Financier Proportion_prodex_{year-1}",
    f"Financier TresoBrute_{year-1}",
    f"Financier Mois_AvanceTreso_{year-1}",
    f"Financier caf_{year-1}",

    "PAT Taux_nvx_formes_CRB",
    "PAT conv_pref",
    "PAT conv_total",
    "PAT conv_public",
    "PAT conv_prive",
    "PAT astreinte",
    "PAT CAI_CHU",
    "PAT CAI",
    "PAT CHU",
    "PAT coup_coeur",
    "PAT Dispos_urgence_nb_exercices",
    "PAT Dispos_urgence_PST",
    "PAT %_TCAU_PSP",
    "PAT Dispos_urgence_tauxformation_TCAU",
    "PAT Dispos_urgence_tauxformation_PSP",
    "PAT Dispos_urgence_tauxformation_GQS",

    "PAT FGP_Nb_formes_PSC",
    "PAT FGP_Nb_FPSC",
    "PAT FGP_Nb_AGQS",
    "PAT FGP_Nb_sessions_PSC",
    "PAT FGP_Nb_sessions_GQS",
    "PAT FGP_Nb_sessions_IPS",
    "PAT FGP_Nb_sessions_IPSEN",

    "PAT OCR_Nb_OCR",

    "PAT Maraudes_Nb_maraudes",
    "PAT Maraudes_Formes_SOLIDAR2020",

    "PAT DPS_Nb_IS",
    "PAT DPS_Nb_DPS",
    "PAT DPS_CA",

    "PAT AEO_Structure_menant_activite",
    "PAT AEO_Nb_aeo_fixe",
    "PAT AEO_Nb_aeo_mobile"
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


def ajouter_colonnes_taux(df: pd.DataFrame, denominateur: str, year: int) -> pd.DataFrame:
    """
    Ajoute des colonnes calculées comme (colonne / denominateur).

    Les noms des nouvelles colonnes sont définis en dur dans la fonction.
    """
    colonnes = [f"Dispositifs_d_urgence Nb_formes_TCAU_{year}","Dispositifs_d_urgence Nb_formes_TCEO_{year}",
    f"Dispositifs_d_urgence Nb_formes_PSP_{year}", f"Dispositifs_d_urgence Nb_formes_IRR_{year}", f"Dispositifs_d_urgence Nb_formes_GQS_{year}",
    f"Structure Nb_formes_CRB_{year}"]
    # ⚠️ noms hardcodés (modifie-les ici selon ton besoin)
    mapping_noms = {
        f"Dispositifs_d_urgence Nb_formes_TCAU_{year}": f"Dispositifs_d_urgence Taux_formation_TCAU_{year}",
        f"Dispositifs_d_urgence Nb_formes_TCEO_{year}": f"Dispositifs_d_urgence Taux_formation_TCEO_{year}",
        f"Dispositifs_d_urgence Nb_formes_PSP_{year}": f"Dispositifs_d_urgence Taux_formation_PSP_{year}",
        f"Dispositifs_d_urgence Nb_formes_IRR_{year}" : f"Dispositifs_d_urgence Taux_formation_IRR_{year}",
        f"Dispositifs_d_urgence Nb_formes_GQS_{year}" : f"Dispositifs_d_urgence Taux_formation_GQS_{year}",
        f"Structure Nb_formes_CRB_{year}" : f"Structure Taux_formation_CRB_{year}"
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

def vision_conso(df_alldata, df_alldata_DT, year):
  # sélection des colonnes pour vision consolidée FPG

  formations_certifiantes = [
      f'Formation_grand_public Nb_formes_PSC_{year}',
      f'Formation_grand_public Nb_formes_GQS_{year}',
      f'Formation_grand_public Nb_sessions_PSC_{year}',
      f'Formation_grand_public Nb_sessions_GQS_{year}'
  ]

  df_alldata['Formation_grand_public Activite_Conso_Etat'] = (
      df_alldata[formations_certifiantes]
      .fillna(0)
      .sum(axis=1)
      .gt(0)
      .map({True: 'Action menée', False: 'Non menée'})
  )



  formations_non_certifiantes = [
      f'Formation_grand_public Nb_formes_IPSEN_{year}',
      f'Formation_grand_public Nb_formes_IPS_{year}',
      #f'Formation_grand_public Nb_formes_PREVIC_{year}',
      f'Formation_grand_public Nb_sessions_IPSEN_{year}',
      f'Formation_grand_public Nb_sessions_IPS_{year}',
      #f'Formation_grand_public Nb_sessions_PREVIC_{year}'
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
      #'Textile Nb_dispositifs',
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


def ajouter_au_all_data(all_data, df, nom_bloc="", cle="n_structure"):

    if df is None or df.empty:
        print(f"⚠️ {nom_bloc} : dataframe vide ou absent")
        return all_data

    if cle not in df.columns:
        raise ValueError(f"❌ {nom_bloc} : la colonne {cle} est absente")

    all_data = all_data.set_index(cle)
    df = df.set_index(cle)

    # Colonnes déjà existantes → mise à jour sans changer l'ordre
    colonnes_existantes = [
        c for c in df.columns if c in all_data.columns
    ]

    if colonnes_existantes:
        print(f"⚠️ {nom_bloc} : remplacement colonnes {colonnes_existantes}")
        all_data.update(df[colonnes_existantes])

    # Nouvelles colonnes
    nouvelles_colonnes = [
        c for c in df.columns if c not in all_data.columns
    ]

    if nouvelles_colonnes:
        all_data = all_data.join(df[nouvelles_colonnes])

    all_data = all_data.reset_index()

    print(f"✅ {nom_bloc} ajouté au all_data")

    return all_data