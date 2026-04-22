import os
import sys
sys.path.append(os.path.abspath("/Code-PAT/checks"))

from core import *
from helpers import *



def main():
    # URL du sheet de sortie des tests
    output_sheet_url = 'https://docs.google.com/spreadsheets/d/1maXN8FgvkzZEjivAfj5uRdCSnWOa_OQdekEXVAVGrgg/'

    # Initialisation du client gspread et import des dataframes all_data contenant l'output de la pipeline
    client = client_gspread()
    df_UL, df_DT = import_dataframes('https://docs.google.com/spreadsheets/d/1maXN8FgvkzZEjivAfj5uRdCSnWOa_OQdekEXVAVGrgg/', client)
    df_UL_sans_IN = df_UL[df_UL['n_structure'] != 1]

    # Les colonnes à ignorer
    skip_columns = ['n_structure', 'type_structure', 'nom_structure', 'adresse_physique_cp', 'code_insee', 'adresse_physique_commune', 'adresse_complete', 'n_dept', 'date_demarrage_activite_ben_struct', 'date_arret_activite_struct', 'Structure_de_rattachement', 'Structure_de_rattachement.1', 'DT_de_rattachement', 'lon', 'lat']
    columns = [col for col in df_DT.columns if not (('taux' in col) or ('Taux' in col) or ('menant_activite' in col)) and col in df_UL_sans_IN.columns and col not in skip_columns]

     # -------------------------------------------------------------------------
    # Tâche 1 — Comparaison des sommes globales df_UL vs df_DT (existant)
    # -------------------------------------------------------------------------
    compare_and_print(
        df_UL_sans_IN, df_DT, columns,
        'Données UL', 'Données DT',
        google_sheets_url=output_sheet_url,
        sheet_name='DT_vs_UL',
    )
 
    # -------------------------------------------------------------------------
    # Tâche 2 — Comparaison ligne par ligne df_DT vs df_UL groupé par DT
    # -------------------------------------------------------------------------
    compare_dt_and_export(
        df_DT=df_DT,
        df_UL=df_UL_sans_IN,
        columns=columns,
        dt_key_dt='n_structure',          # clé dans df_DT
        dt_col_ul='DT_de_rattachement',   # colonne DT dans df_UL
        extract_integer=True,             # extrait l'entier de DT_de_rattachement
        df_dt_name='Données DT',
        df_ul_name='Données UL (groupé)',
        google_sheets_url=output_sheet_url,
        sheet_name='DT_vs_UL_par_DT',
        show_all=True,                    # False = uniquement les écarts
    )
 
    # -------------------------------------------------------------------------
    # Tâche 3 — Comparaison feuilles de référence vs données source
    # -------------------------------------------------------------------------
    compare_reference_and_export(
        df_UL=df_UL_sans_IN,
        df_DT=df_DT,
        reference_url=reference_sheet_url,
        output_url=output_sheet_url,
        columns_ul=columns,               # None = toutes les colonnes communes
        columns_dt=columns,
        columns_total=columns,
        id_col_ul='n_structure',          # clé de jointure pour UL (None = par position)
        id_col_dt='n_structure',          # clé de jointure pour DT
        sheet_ul_ref='UL',                # onglets dans le sheet de référence
        sheet_dt_ref='DT',
        sheet_total_ref='Total',
        output_sheet_ul='Ref_vs_UL',      # onglets de sortie
        output_sheet_dt='Ref_vs_DT',
        output_sheet_total='Ref_vs_Total',
        show_all=True,                    # False = uniquement les écarts
    )

if __name__ == "__main__":
    main()