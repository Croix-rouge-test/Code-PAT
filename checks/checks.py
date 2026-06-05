import os
import sys
sys.path.append(os.path.abspath("/Code-PAT/checks"))

from core import *
from helpers import *



def main():
    # URL du sheet de sortie des tests
    output_sheet_url = 'https://docs.google.com/spreadsheets/d/1hqt1aDeE0KIu-RtqApesh2tC4DTG0UkdOgYOMMTZZZQ/'

    # Initialisation du client gspread et import des dataframes all_data contenant l'output de la pipeline
    client = client_gspread()
    df_UL, df_DT = import_dataframes('https://docs.google.com/spreadsheets/d/1pmEUcLvVOK3t7TWmXL6cN0uTWJ9kPgIwd2x3hy14Alk/', client)
    df_UL_sans_IN = df_UL[df_UL['n_structure'] != 1]

    df_UL["n_structure"] = pd.to_numeric(df_UL["n_structure"], errors="coerce").astype("Int64")
    df_DT["n_structure"] = pd.to_numeric(df_DT["n_structure"], errors="coerce").astype("Int64")

    df_IN = df_UL[df_UL['n_structure'] == 1].copy()

    liste_activite_map = ['AEO Structure_activite_mobile', 'OCR Structures_menant_activite',
                        'Secours Structures_menant_activite',
                        'Maraudes Structures_menant_activite',
                        'Formation_grand_public Structures_menant_activite',
                        'Textile Structures_menant_activite'
                        ]
    
    df_IN['Textile tracabilite_flux'] = df_IN['Textile tracabilite_flux'].map({'Oui': 1}).fillna(0)
    
    for col in liste_activite_map:
        df_IN[col] = (
            df_IN[col]
            .map({'Action menée': 1})
            .fillna(0)
        )

    df_IN['AEO Structures_menant_activite'] = (
        df_IN['AEO Structures_menant_activite']
        .map({'Activité AEO/AAD menée': 1})
        .fillna(0)
    )

    df_DT_avec_IN = pd.concat(
        [df_DT, df_IN.reindex(columns=df_DT.columns)],
        ignore_index=True
    )

    # Les colonnes à ignorer
    skip_columns = ['n_structure','n_structure-ratt', 'type_structure', 'nom_structure', 'adresse_physique_cp', 'code_insee', 'adresse_physique_commune', 
                    'adresse_complete', 'n_dept', 'date_demarrage_activite_ben_struct', 'date_arret_activite_struct', 'Structure_de_rattachement','Rattachements_successifs', 'Structure_de_rattachement.1', 
                    'DT_de_rattachement', 'lon', 'lat', 'Formation_grand_public Activite_Conso_Etat', 'Formation_grand_public Activite_Conso_Non_Etat', 
                    'OCR Structures_menant_activite', 'Secours Structures_menant_activite', 'Secours Structures_menant_activite_formes', 'Secours Structures_menant_activite_sessions', 
                    'Maraudes Structures_menant_activite', 'AEO Structures_menant_activite', 'Formation_grand_public Structures_menant_activite' , 'AEO Structure_activite_mobile', 
                    'Dispositifs_d_urgence Utilisation_RedCall', 'AEO Structure_activite_fixe', 'Activités AAD facultatives' , 'Financier ResNet_2023', 'Financier ResNet_2024', 'Financier ResNet_2025',
                    'Financier ResNet_2026', 'Financier ResNet_2027', 'Financier ResNet_2028', 'Financier ResNet_2029','Financier ResCorrProd_2023', 'Financier ResCorrProd_2024', 'Financier ResCorrProd_2025',
                    'Financier ResCorrProd_2026', 'Financier ResCorrProd_2027', 'Financier ResCorrProd_2028', 'Financier ResCorrProd_2029']

    columns = [col for col in df_UL_sans_IN.columns if col not in skip_columns]
    columns_sans_taux = [col for col in df_DT.columns if not (('taux' in col) or ('Taux' in col) or ('menant_activite' in col)) and col in df_UL_sans_IN.columns and col not in skip_columns]

    # -------------------------------------------------------------------------
    # Tâche 1 — Comparaison des sommes globales df_UL vs df_DT (existant)
    # -------------------------------------------------------------------------
    compare_and_print(
        df_UL, df_DT_avec_IN, columns_sans_taux,
        'Données UL', 'Données DT',
        google_sheets_url=output_sheet_url,
        sheet_name='DT_vs_UL',
    )
 
    # -------------------------------------------------------------------------
    # Tâche 2 — Comparaison ligne par ligne df_DT vs df_UL groupé par DT
    # -------------------------------------------------------------------------
    compare_dt_and_export(
        df_DT=df_DT.drop(columns=['Textile tracabilite_flux'] + liste_activite_map),
        df_UL=df_UL_sans_IN.drop(columns=['Textile tracabilite_flux'] + liste_activite_map),  # on enlève les colonnes d'activités et de tracabilité qui ne sont pas dans DT
        columns=columns_sans_taux,
        dt_key_dt='n_structure',          # clé dans df_DT
        dt_col_ul='DT_de_rattachement',   # colonne DT dans df_UL
        extract_integer=True,             # extrait l'entier de DT_de_rattachement
        df_dt_name='Données DT',
        df_ul_name='Données UL (groupé)',
        google_sheets_url=output_sheet_url,
        sheet_name='DT_vs_UL_agg_par_DT',
        show_all=True,                    # False = uniquement les écarts
    )
 
    # # -------------------------------------------------------------------------
    # # Tâche 3 — Comparaison feuilles de référence vs données source
    # # -------------------------------------------------------------------------
    compare_reference_and_export(
        df_DT=df_DT_avec_IN,
        reference_url=output_sheet_url,
        output_url=output_sheet_url,
        columns_dt=columns,
        columns_total=columns,
        id_col_dt='n_structure',          # clé de jointure pour DT
        sheet_dt_ref='Chiffres de référence',
        output_sheet_dt='Ref_vs_DT',
        output_sheet_total='Ref_vs_Total',
        show_all=True,                    # False = uniquement les écarts
    )

if __name__ == "__main__":
    main()