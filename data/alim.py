import pandas as pd
import numpy as np
import os
import re
import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *

# ### dans la section alim du code,, le dossier est ajouté mais pas l'appel à cette fonction et le return pour les 4 indicateurs alim et leur déclinaisoon DT, il n'y a pas de merge de ces indicateurs
# ## récupération des données
# def clean_alim(df_alim):
#   df_alim=df_alim[["Dispositif","Code U2A","Stucture rattachement",'N° structure']]

#   ## préparation BDD alim
#   if 'Code U2A' in df_alim.columns:
#     # Identifier les doublons dans la colonne 'Code U2A'
#     duplicates = df_alim[df_alim['Code U2A'].duplicated(keep=False)]

#   #   # Compter le nombre de doublons
#   #   num_duplicates = duplicates.shape[0]

#   #   if num_duplicates > 0:
#   #         print(f"Il y a {num_duplicates} lignes avec des doublons dans la colonne 'Code U2A'.")
#   #         print("Voici les lignes en doublon (affichant toutes les occurrences des valeurs dupliquées) :")
#   #         display(duplicates.sort_values(by='Code U2A'))
#   #   else:
#   #         print("Aucun doublon trouvé dans la colonne 'Code U2A'.")
#   # else:
#   #       print("La colonne 'Code U2A' n'existe pas dans le DataFrame df_alim.")
 
#   # Création d'une base de données sans doublons
#   df_alim_sans_doublons =df_alim.drop_duplicates(subset=['Code U2A'], keep='first')
#   # print(f"Taille du DataFrame après suppression des doublons : {df_alim_sans_doublons.shape}")
#   df_alim_sans_doublons = df_alim_sans_doublons.rename(columns={"N° structure": "n_structure"})
#   # Conversion de la colonne n_structure en string pour la cohérence avec df_ref_structure
#   df_alim_sans_doublons['n_structure'] = df_alim_sans_doublons['n_structure'].astype(str)
#   # Supprimer le '.0' des chaînes si elles proviennent de nombres flottants
#   df_alim_sans_doublons['n_structure'] = df_alim_sans_doublons['n_structure'].apply(lambda x: x[:-2] if x.endswith('.0') else x)
#   df_alim_sans_doublons['n_structure'] = df_alim_sans_doublons['n_structure'].astype(int)

#   return df_alim_sans_doublons

# def indicateurs_alim(df_alim_sans_doublons, df_ref_structure):
#     # U2A
#   # if 'Dispositif' in df_alim_sans_doublons.columns:
#   #     print("Nombre d'occurrences pour chaque type de 'Dispositif':")
#   #     display(df_alim_sans_doublons['Dispositif'].value_counts())
#   # else:
#   #     print("La colonne 'Dispositif' n'existe pas dans le DataFrame df_alim_sans_doublons.")
  
#   df_alim_U2A_sans_doublons = df_alim_sans_doublons.groupby("n_structure").size().reset_index(name="Aide_alimentaire Nb_U2A")

#   # Epicerie sociale
#   df_alim_epicerie_sociale= df_alim_sans_doublons[df_alim_sans_doublons['Dispositif'] == 'Epicerie sociale']
#   df_alim_epicerie_sociale.shape[0]
#   df_alim_epicerie_sociale = df_alim_epicerie_sociale.groupby("n_structure").size().reset_index(name="Aide_alimentaire Nb_epiceries_sociales")

#   # Accueil Alimentaire
#   df_alim_accueil_alimentaire= df_alim_sans_doublons[df_alim_sans_doublons['Dispositif'] .isin(['Accueil alimentaire', 'Accueil Alimentaire'])]
#   df_alim_accueil_alimentaire.shape[0]
#   df_alim_accueil_alimentaire = df_alim_accueil_alimentaire.groupby("n_structure").size().reset_index(name="Aide_alimentaire Nb_Centre_distribution_alimentaire")
  
#   # CRsr
#   df_alim_crsr= df_alim_sans_doublons[df_alim_sans_doublons['Dispositif'].isin(['Croix-Rouge sur Roues', 'CRSR Accueil alimentaire'])]
#   df_alim_crsr.shape[0]
#   df_alim_crsr = df_alim_crsr.groupby("n_structure").size().reset_index(name="Aide_alimentaire Nb_crsr")

#   return (
#     df_alim_U2A_sans_doublons, 
#     df_alim_epicerie_sociale, 
#     df_alim_accueil_alimentaire, 
#     df_alim_crsr,
#   )


# def indicateurs_alim_DT(
#     df_alim_U2A_sans_doublons, 
#     df_alim_epicerie_sociale, 
#     df_alim_accueil_alimentaire, 
#     df_alim_crsr, 
#     rattachement_court
# ):
#     """
#     Merge + groupby DT pour tous les DataFrames alimentation et retourne les 4 DataFrames modifiés.
#     """

#     # --- U2A ---
#     df_alim_U2A_DT = df_alim_U2A_sans_doublons.copy()
#     df_alim_U2A_DT["n_structure"] = df_alim_U2A_DT["n_structure"].astype("float64")
#     df_alim_U2A_DT = pd.merge(
#         df_alim_U2A_DT,
#         rattachement_court,
#         on="n_structure",
#         how="left"
#     )
#     df_alim_U2A_DT = df_alim_U2A_DT.groupby("DT_de_rattachement", as_index=False)["Aide_alimentaire Nb_U2A"].sum()

#     # --- Epicerie sociale ---
#     df_alim_epicerie_sociale_DT = df_alim_epicerie_sociale.copy()
#     df_alim_epicerie_sociale_DT["n_structure"] = df_alim_epicerie_sociale_DT["n_structure"].astype("float64")
#     df_alim_epicerie_sociale_DT = pd.merge(
#         df_alim_epicerie_sociale_DT,
#         rattachement_court,
#         on="n_structure",
#         how="left"
#     )
#     df_alim_epicerie_sociale_DT = df_alim_epicerie_sociale_DT.groupby("DT_de_rattachement", as_index=False)["Aide_alimentaire Nb_epiceries_sociales"].sum()

#     # --- Accueil alimentaire ---
#     df_alim_accueil_alimentaire_DT = df_alim_accueil_alimentaire.copy()
#     df_alim_accueil_alimentaire_DT["n_structure"] = df_alim_accueil_alimentaire_DT["n_structure"].astype("float64")
#     df_alim_accueil_alimentaire_DT = pd.merge(
#         df_alim_accueil_alimentaire_DT,
#         rattachement_court,
#         on="n_structure",
#         how="left"
#     )
#     df_alim_accueil_alimentaire_DT = df_alim_accueil_alimentaire_DT.groupby("DT_de_rattachement", as_index=False)["Aide_alimentaire Nb_Centre_distribution_alimentaire"].sum()

#     # --- CRSR ---
#     df_alim_crsr_DT = df_alim_crsr.copy()
#     df_alim_crsr_DT["n_structure"] = df_alim_crsr_DT["n_structure"].astype("float64")
#     df_alim_crsr_DT = pd.merge(
#         df_alim_crsr_DT,
#         rattachement_court,
#         on="n_structure",
#         how="left"
#     )
#     df_alim_crsr_DT = df_alim_crsr_DT.groupby("DT_de_rattachement", as_index=False)["Aide_alimentaire Nb_crsr"].sum()

#     return df_alim_U2A_DT, df_alim_epicerie_sociale_DT, df_alim_accueil_alimentaire_DT, df_alim_crsr_DT


def calcul_u2a(df_ref_structure, df_U2A_statut, df_U2A_actions, df_contact):
    
    df_ref_structure = df_ref_structure[["nom_structure", "n_structure", "n_structure-ratt", "DT_de_rattachement"]]

    #Sélection des actions d'U2A qui nous intéressent pour les indicateurs (CRSR, accueil alimentaire, épicerie sociale)

    Liste_U2A = ["Accueil alimentaire","Epicerie sociale", "CRsr ACAL","CRsr ES"]
        #"Panier d'urgence", 'Restaurant social','Accueil de jour', 

    df_U2A_statut = df_U2A_statut[df_U2A_statut['Action menée'].isin(Liste_U2A)]

    #Récupération de la date de dernière distribution pour les différentes U2A

    df_U2A_statut["Date de dernière distribution"] = pd.to_datetime(
        df_U2A_statut["Date de dernière distribution"],
        errors="coerce",
        dayfirst=True)


    #FILTRES pour ne garder que les U2A qui ont eu une distribution récente (après le 31 Décembre 2025)

    df_U2A_statut = df_U2A_statut[df_U2A_statut['Date de dernière distribution']>'2025-12-31']

    df_U2A_statut = df_U2A_statut[['Code U2A', "Nom de l'U2A", 'Structure de rattachement', 'Action menée', 'Date de dernière distribution']]

    df_U2A_statut = df_U2A_statut.drop_duplicates(subset=['Code U2A', 'Action menée'], keep='first')


    #FILTRE pour ne garder que les modalités qui nous intéressent

    Liste_action = ['Nombre de distributions', 'Poids net distribué (en Kg)', "Nombre d'ayants-droit accompagnés servis"]

    df_U2A_actions = df_U2A_actions[df_U2A_actions['Noms de mesures'].isin(Liste_action)]

    #création d'un DF par indicateur pour faciliter les traitements et les visualisations

    df_U2A_distribution = df_U2A_actions[df_U2A_actions['Noms de mesures'] == 'Nombre de distributions' ]

    df_U2A_ayants_droits = df_U2A_actions[df_U2A_actions['Noms de mesures'] == "Nombre d'ayants-droit accompagnés servis" ]

    df_U2A_Poids_distributions = df_U2A_actions[df_U2A_actions['Noms de mesures'] == 'Poids net distribué (en Kg)' ]



    #Vérif que pas de doublons dans les CD_U2A

    df_U2A_Poids_distributions["CD_U2A"].duplicated().sum()

    df_U2A_ayants_droits["CD_U2A"].duplicated().sum()

    df_U2A_distribution["CD_U2A"].duplicated().sum()


    # pour chaque DF, on garde que les U2A ayant des valeurs positives

    df_U2A_distribution = df_U2A_distribution [df_U2A_distribution['Valeurs de mesures'] > 0 ]

    df_U2A_ayants_droits = df_U2A_ayants_droits [df_U2A_ayants_droits['Valeurs de mesures'] > 0 ]

    df_U2A_Poids_distributions = df_U2A_Poids_distributions [df_U2A_Poids_distributions['Valeurs de mesures'] > 0 ]


    #On renomme les colonnes pour que ça coorrsponde aux intitulés du All Data

    df_U2A_distribution.rename(columns={'Valeurs de mesures': 'Aide_alimentaire nb_distributions'}, inplace=True)

    df_U2A_ayants_droits.rename(columns={'Valeurs de mesures': 'Aide_alimentaire nb_PA'}, inplace=True)

    df_U2A_Poids_distributions.rename(columns={'Valeurs de mesures': 'Aide_alimentaire nb_tonnes'}, inplace=True)


    #Etant donné qu'on a vérifié plus haut que pas de doublons, on peut drop duplicate les N°U2A ( mais ce n'est pas forcémzent nécessaire) 

    df_U2A_distribution = df_U2A_distribution[
        ["CD_U2A", "Aide_alimentaire nb_distributions"]
    ].drop_duplicates()

    # df_U2A_ayants_droits = df_U2A_ayants_droits[
    #     ["CD_U2A", "Aide_alimentaire nb_PA"]
    # ].drop_duplicates()

    df_U2A_Poids_distributions = df_U2A_Poids_distributions[
        ["CD_U2A", "Aide_alimentaire nb_tonnes"]
    ].drop_duplicates()


    #Définition du statut actif ou non actif en fonction du nombre de distributions réalisées (seuil à 17 distributions, soit 5 distribution pour 6 semaines)
    df_U2A_distribution["Aide_alimentaire statut_U2A"] = np.where(
        df_U2A_distribution["Aide_alimentaire nb_distributions"] >= 17,
        "Actif",
        "Non actif"
    )


     #Calcul du nombre d'ayant droits
    Liste_U2A_contact = ["Accueil alimentaire","Epicerie sociale", "CRsr ACAL","CRsr ES"]
        #"Panier d'urgence", 'Restaurant social','Accueil de jour', 
    df_contact = df_contact[df_contact['Action'].isin(Liste_U2A_contact)]

    df_contact["Nb. AD uniques"] = pd.to_numeric(
        df_contact["Nb. AD uniques"],
        errors="coerce"
    ).fillna(0)



    # Somme des ayants droit par U2A
    df_U2A_ayants_droits  = (
        df_contact
        .groupby("U2a", as_index=False)["Nb. AD uniques"]
        .sum()
        .rename(columns={
            "U2a": "CD_U2A",
            "Nb. AD uniques": "Aide_alimentaire nb_PA"
        })
    )
  

    # #On merge les différents DF d'indicateurs d'U2A pour avoir un DF global avec tous les indicateurs

    # df_U2A_merged = (
    #     df_U2A_distribution
    #     .merge(df_U2A_ayants_droits, on="CD_U2A", how="outer")
    #     .merge(df_U2A_Poids_distributions, on="CD_U2A", how="outer")
    # )

    # #On merge le DF avec le DF de statut pour avoir un DF final avec les indicateurs et le statut d'activité des U2A
    # df_U2A_final = df_U2A_merged.merge(
    #     df_U2A_statut,
    #     left_on="CD_U2A",
    #     right_on="Code U2A",
    #     how="inner"
    # )


    df_U2A_statut = df_U2A_statut.copy()

    df_U2A_statut["Structure de rattachement"] = (
        df_U2A_statut["Structure de rattachement"]
        .str.replace("UNITE LOCALE", "UL", regex=False)
        .str.replace("ANTENNE LOCALE", "AL", regex=False)
        .str.replace("DD", "DT", regex=False)
        .str.replace("INSTANCES NATIONALES", "IN", regex=False)
    )

    df_U2A_statut_ref = df_U2A_statut.merge(
        df_ref_structure,
        left_on="Structure de rattachement",
        right_on="nom_structure",
        how="left",
        validate="many_to_one"
    )

    #Rename les type de dispositifs 

    df_U2A_statut_ref[
        "Aide_alimentaire Nb_Centre_distribution_alimentaire"
    ] = (
        df_U2A_statut_ref["Action menée"]
        == "Accueil alimentaire"
    ).astype(int)

    df_U2A_statut_ref[
        "Aide_alimentaire Nb_epiceries_sociales"
    ] = (
        df_U2A_statut_ref["Action menée"]
        == "Epicerie sociale"
    ).astype(int)

    df_U2A_statut_ref[
        "Aide_alimentaire Nb_crsr"
    ] = (
        df_U2A_statut_ref["Action menée"]
        .isin(["CRsr ACAL", "CRsr ES"])
    ).astype(int)

    df_U2A_statut_ref["Aide_alimentaire Nb_U2A"] = 1

    #On merge les différents DF d'indicateurs d'U2A pour avoir un DF global avec tous les indicateurs

    df_U2A_merged = (
        df_U2A_distribution
        .merge(df_U2A_ayants_droits, on="CD_U2A", how="outer")
        .merge(df_U2A_Poids_distributions, on="CD_U2A", how="outer")
    )
    
    df_U2A_statut_ref.drop_duplicates("Code U2A")

    #On merge le DF avec le DF de statut pour avoir un DF final avec les indicateurs et le statut d'activité des U2A
    df_U2A_final = df_U2A_merged.merge(
        df_U2A_statut_ref,
        left_on="CD_U2A",
        right_on="Code U2A",
        how="inner"
    )

    df_U2A_final = df_U2A_final[df_U2A_final["Aide_alimentaire statut_U2A"] == "Actif"]


    df_U2A_Structure = df_U2A_final[["n_structure-ratt", 'Aide_alimentaire Nb_U2A','Aide_alimentaire Nb_Centre_distribution_alimentaire', 'Aide_alimentaire Nb_epiceries_sociales', 'Aide_alimentaire Nb_crsr', 'Aide_alimentaire nb_distributions', 'Aide_alimentaire nb_tonnes', 'Aide_alimentaire nb_PA']]


    df_U2A_Structure = (
        df_U2A_Structure
        .groupby("n_structure-ratt", as_index=False)
        .sum(numeric_only=True)
    )

 

    # #On merge le DF avec le DF de statut pour avoir un DF final avec les indicateurs et le statut d'activité des U2A
    # df_U2A_Structure = df_U2A_merged.merge(
    #     df_U2A_statut,
    #     left_on="CD_U2A",
    #     right_on="Code U2A",
    #     how="inner"
    # )

    #Calcul du nombre de structures ayant des U2A par DT de rattachement

    df_struct_DT = df_U2A_Structure[["n_structure-ratt"]]
    df_struct_DT["Aide_alimentaire Nb_struct"] = 1

    df_struct_DT =pd.merge(df_struct_DT, df_ref_structure[["n_structure-ratt", "DT_de_rattachement"]], on="n_structure-ratt", how="left")

    df_struct_DT = df_struct_DT[["DT_de_rattachement", "Aide_alimentaire Nb_struct"]]

    df_struct_DT  = (
        df_struct_DT 
        .groupby("DT_de_rattachement", as_index=False)
        .sum(numeric_only=True)
    )

    df_U2A_DT = df_U2A_final[
        ['DT_de_rattachement',
        'Aide_alimentaire Nb_U2A',
        'Aide_alimentaire Nb_Centre_distribution_alimentaire',
        'Aide_alimentaire Nb_epiceries_sociales', 
        'Aide_alimentaire Nb_crsr', 
        'Aide_alimentaire nb_distributions', 
        'Aide_alimentaire nb_tonnes', 
        'Aide_alimentaire nb_PA']
        ]
    
    df_U2A_DT = (
        df_U2A_DT
        .groupby('DT_de_rattachement', as_index=False)
        .sum(numeric_only=True)
    )

    df_U2A_DT =pd.merge(df_U2A_DT, df_struct_DT, on="DT_de_rattachement", how="left")

    
    df_U2A_final = df_U2A_final.rename(columns={"n_structure-ratt": "n_structure"})
    df_U2A_Structure = df_U2A_Structure.rename(columns={"n_structure-ratt": "n_structure"})
    df_struct_DT = df_struct_DT.rename(columns={"n_structure-ratt": "n_structure"})
    df_U2A_DT = df_U2A_DT.rename(columns={"n_structure-ratt": "n_structure"})

    return df_U2A_final, df_U2A_Structure, df_struct_DT, df_U2A_DT

