import os
import sys
sys.path.append(os.path.abspath("/Code-PAT/checks"))

from core import *
from helpers import *



def main():

    expected_word = "CONFIRMER"
    quit_word = "quit"
    print(f"Attention, exécuter ce script va supprimer la précédente version de la feuille sheet: pour continuer, taper le mot exact : {expected_word}")
    print(f"Pour arrêter le script, taper le mot : {quit_word}")

    while True:
        user_input = input("Saisie : ").strip()

        if user_input == expected_word:
            print("Confirmation validée, exécution du script...")
            break
        elif user_input == quit_word:
            raise SystemExit("Arrêt du script")
        else:
            print("Mot incorrect. Réessaie.")
    # URL du sheet de sortie des tests
    output_sheet_url = 'https://docs.google.com/spreadsheets/d/1hqt1aDeE0KIu-RtqApesh2tC4DTG0UkdOgYOMMTZZZQ/'


    # Initialisation du client gspread et import des dataframes all_data contenant l'output de la pipeline
    client = client_gspread()
    df_UL, df_DT = import_dataframes('https://docs.google.com/spreadsheets/d/1maXN8FgvkzZEjivAfj5uRdCSnWOa_OQdekEXVAVGrgg/', client)
    df = df_DT.copy()

    # Les colonnes à ignorer
    skip_columns = ['type_structure', 'adresse_physique_cp', 'code_insee', 'adresse_physique_commune', 'adresse_complete', 'date_demarrage_activite_ben_struct', 'date_arret_activite_struct', 'Structure_de_rattachement', 'Structure_de_rattachement.1', 'DT_de_rattachement', 'lon', 'lat']
    col_to_keep = ['n_structure', 'n_dept', 'nom_structure']

    df['n_structure'] = df['n_structure'].astype(str).apply(lambda x: x.replace('.0',''))
    df = df.loc[:, ~df.columns.isin(skip_columns)]

    df.loc[:, ~df.columns.isin(col_to_keep)] = ''
    df['Total'] = False 
    df['Source/Commentaire'] = df.loc[:, df.columns[3]]

    new_data = df.loc[1,df.columns]
    new_data['n_structure'] = 'Total'
    new_data['n_dept'] = ''
    new_data['nom_structure'] = 'CRF'
    new_data['Total'] = True

    new_data = new_data.to_frame().T

    # Ajouter la ligne total
    df = pd.concat([df, new_data], ignore_index=True, axis = 0)


    new_data = df.loc[1,df.columns]
    new_data['n_structure'] = 'Source/Commentaire'
    new_data['n_dept'] = ''
    new_data['nom_structure'] = ''
    new_data['Total'] = True

    new_data = new_data.to_frame().T

    # Ajouter la ligne 
    df = pd.concat([df, new_data], ignore_index=True, axis = 0)
    save_dataframe_to_sheet("1hqt1aDeE0KIu-RtqApesh2tC4DTG0UkdOgYOMMTZZZQ", client, df, sheet_name = 'Chiffres de référence')

if __name__ == "__main__":
    main()