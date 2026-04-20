import os
import sys
sys.path.append(os.path.abspath("/Code-PAT/checks"))

from core import *
from helpers import *



def main():

    # Initialisation du client gspread et import des dataframes all_data contenant l'output de la pipeline
    client = client_gspread()
    df_UL, df_DT = import_dataframes('https://docs.google.com/spreadsheets/d/1maXN8FgvkzZEjivAfj5uRdCSnWOa_OQdekEXVAVGrgg/', client)
    df_UL_sans_IN = df_UL[df_UL['n_structure'] != 1]

    # Les colonnes à ignorer
    skip_columns = ['n_structure', 'type_structure', 'nom_structure', 'adresse_physique_cp', 'code_insee', 'adresse_physique_commune', 'adresse_complete', 'n_dept', 'date_demarrage_activite_ben_struct', 'date_arret_activite_struct', 'Structure_de_rattachement', 'Structure_de_rattachement.1', 'DT_de_rattachement', 'lon', 'lat']
    columns = [col for col in df_DT.columns if not (('taux' in col) or ('Taux' in col) or ('menant_activite' in col)) and col in df_UL_sans_IN.columns and col not in skip_columns]
    
    # Comparaison des sommes des colonnes sélectionnées entre df_UL et df_DT
    compare_and_print(df_UL_sans_IN, df_DT, columns, 'Données UL', 'Données DT')

if __name__ == "__main__":
    main()