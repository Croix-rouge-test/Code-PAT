import pandas as pd
import os
import re
import sys
sys.path.append(os.path.abspath("/Code-PAT"))
from utils import *



# besoin de formatter le code en fonction
def clean_adherent(df_adherent):
  df_adherent = df_adherent [["Département de la structure","Id de la structure","Nivol du contact","Année de l'adhésion du contact"]]

  # Convert 'Année de l'adhésion du contact' to numeric, coercing errors
  df_adherent["Année de l'adhésion du contact"] = pd.to_numeric(df_adherent["Année de l'adhésion du contact"], errors='coerce')

  # Print unique values
  print("Unique values in 'Année de l'adhésion du contact':", df_adherent["Année de l'adhésion du contact"].unique())
  print("Data type of 'Année de l'adhésion du contact':", df_adherent["Année de l'adhésion du contact"].dtype)

  # Compter le nombre de doublons
  if 'Nivol du contact' in df_adherent.columns:
    duplicates = df_adherent[df_adherent['Nivol du contact'].duplicated(keep=False)]
    num_duplicates = duplicates.shape[0]

  #   if num_duplicates > 0:
  #       print(f"Il y a {num_duplicates} lignes avec des doublons dans la colonne 'Nivol du contact'.")
  #       print("Voici les lignes en doublon (affichant toutes les occurrences des valeurs dupliquées) :")
  #       display(duplicates.sort_values(by='Nivol du contact'))
  #   else:
  #       print("Aucun doublon trouvé dans la colonne 'Nivol du contact'.")
  # else:
  #     print("La colonne 'Nivol du contact' n'existe pas dans le DataFrame df_adherent.")

  # BDD sans doublons
  df_adherent_sans_doublons =df_adherent.drop_duplicates(subset=["Nivol du contact"], keep='first')
  print(f"Taille du DataFrame après suppression des doublons : {df_adherent_sans_doublons.shape}")

  # Conversion de la colonne n_structure en string pour la cohérence avec df_ref_structure
  df_adherent_sans_doublons = df_adherent_sans_doublons.rename(columns={"Id de la structure": "n_structure"})
  df_adherent_sans_doublons['n_structure'] = df_adherent_sans_doublons['n_structure'].astype(str)
  # Supprimer le '.0' des chaînes si elles proviennent de nombres flottants
  df_adherent_sans_doublons['n_structure'] = df_adherent_sans_doublons['n_structure'].apply(lambda x: x[:-2] if x.endswith('.0') else x)
  return df_adherent_sans_doublons

def indicateurs_adherent(df_adherent_sans_doublons, df_ref_structure):
  # Nb d'adhérents
  df_adherent_sans_doublons = df_adherent_sans_doublons.groupby("n_structure").size().reset_index(name="Structure Nb_Adherents")

  return df_adherent_sans_doublons


def indicateurs_adherent_DT(df_adherent_sans_doublons, rattachement_court):
    df_adherent_sans_doublons['n_structure'] = df_adherent_sans_doublons['n_structure'].astype('float64')
    # Merge données avec rattachement_court
    adherent_sans_doublons = pd.merge(
    df_adherent_sans_doublons,
    rattachement_court,
    on="n_structure",
    how="left"
    )

    # Groupby sur DT_de_rattachement
    Nb_adherent_DT = (adherent_sans_doublons.groupby('DT_de_rattachement')['Structure Nb_Adherents'].sum().reset_index())
    return Nb_adherent_DT



