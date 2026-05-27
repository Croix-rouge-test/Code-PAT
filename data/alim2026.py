import numpy as np
import pandas as pd


def calcul_u2a(df_ref_structure, df_U2A_statut, df_U2A_actions):
    
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

    df_U2A_ayants_droits = df_U2A_ayants_droits[
        ["CD_U2A", "Aide_alimentaire nb_PA"]
    ].drop_duplicates()

    df_U2A_Poids_distributions = df_U2A_Poids_distributions[
        ["CD_U2A", "Aide_alimentaire nb_tonnes"]
    ].drop_duplicates()


    #Définition du statut actif ou non actif en fonction du nombre de distributions réalisées (seuil à 17 distributions, soit 5 distribution pour 6 semaines)
    df_U2A_distribution["Aide_alimentaire statut_U2A"] = np.where(
        df_U2A_distribution["Aide_alimentaire nb_distributions"] >= 17,
        "Actif",
        "Non actif"
    )


    #On merge les différents DF d'indicateurs d'U2A pour avoir un DF global avec tous les indicateurs

    df_U2A_merged = (
        df_U2A_distribution
        .merge(df_U2A_ayants_droits, on="CD_U2A", how="outer")
        .merge(df_U2A_Poids_distributions, on="CD_U2A", how="outer")
    )

    #On merge le DF avec le DF de statut pour avoir un DF final avec les indicateurs et le statut d'activité des U2A
    df_U2A_final = df_U2A_merged.merge(
        df_U2A_statut,
        left_on="CD_U2A",
        right_on="Code U2A",
        how="inner"
    )


    df_U2A_final['Structure de rattachement'] = (
        df_U2A_final['Structure de rattachement']
        .str.replace("UNITE LOCALE", "UL", regex=False)
        .str.replace("ANTENNE LOCALE", "AL", regex=False)
        .str.replace("DD", "DT", regex=False)
        .str.replace("INSTANCES NATIONALES", "IN", regex=False)
    )


    df_U2A_final = df_U2A_final.merge(df_ref_structure, left_on='Structure de rattachement', right_on='nom_structure', how='left')

    #Rename les type de dispositifs 

    df_U2A_final["Aide_alimentaire Nb_Centre_distribution_alimentaire"] = (df_U2A_final["Action menée"] == "Accueil alimentaire").astype(int)

    df_U2A_final["Aide_alimentaire Nb_epiceries_sociales"] = (df_U2A_final["Action menée"] == 'Epicerie sociale').astype(int)

    df_U2A_final["Aide_alimentaire Nb_crsr"] = (df_U2A_final["Action menée"].isin(['CRsr ACAL', 'CRsr ES'])).astype(int)

    df_U2A_final["Aide_alimentaire Nb_U2A"] = 1 


    df_U2A_final = df_U2A_final[df_U2A_final["Aide_alimentaire statut_U2A"] == "Actif"]


    df_U2A_Structure = df_U2A_final[["n_structure-ratt", 'Aide_alimentaire Nb_U2A','Aide_alimentaire Nb_Centre_distribution_alimentaire', 'Aide_alimentaire Nb_epiceries_sociales', 'Aide_alimentaire Nb_crsr', 'Aide_alimentaire nb_distributions', 'Aide_alimentaire nb_tonnes', 'Aide_alimentaire nb_PA']]


    df_U2A_Structure = (
        df_U2A_Structure
        .groupby("n_structure-ratt", as_index=False)
        .sum(numeric_only=True)
    )

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

    return df_U2A_final, df_U2A_Structure, df_struct_DT, df_U2A_DT