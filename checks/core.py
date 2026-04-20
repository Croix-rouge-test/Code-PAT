import os
import sys
import json
import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from gspread_dataframe import get_as_dataframe
import re
from utils import save_dataframe_to_sheet



sys.path.append(os.path.abspath("/Code-PAT/checks"))

from core import *
from helpers import *


def client_gspread():
    # Chemin vers votre fichier de clé JSON
    CREDENTIALS_JSON_url = r'service_account\old.json'

    with open(CREDENTIALS_JSON_url, 'r') as f:
        CREDENTIALS_JSON = json.load(f)
    

    SCOPES = ['https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/spreadsheets.readonly']


    # Authentification
    credentials = service_account.Credentials.from_service_account_info(CREDENTIALS_JSON, scopes=SCOPES)

    # Initialisation des services
    slides_service = build('slides', 'v1', credentials=credentials)
    drive_service = build('drive', 'v3', credentials=credentials)
    gspread_client  = gspread.authorize(credentials)

    return gspread_client

def import_dataframes(url,gspread_client):
    df_UL = get_as_dataframe(gspread_client.open_by_url(url).worksheet('UL'))
    df_DT = get_as_dataframe(gspread_client.open_by_url(url).worksheet('DT'))
    return df_UL, df_DT

def col_sum(df, column):
    """
    Calcule la somme d'une colonne dans un dataframe.
    
    Args:
        df (pd.DataFrame): Le dataframe source.
        column (str): Le nom de la colonne à sommer.
    
    Returns:
        float: La somme de la colonne.
    """
    return df[column].sum()


def _calculate_difference(value1, value2):
    """
    Calcule la différence absolue et relative entre deux valeurs.
    
    Args:
        value1 (float): Première valeur (référence pour le calcul de pourcentage).
        value2 (float): Deuxième valeur à comparer.
    
    Returns:
        dict: Dictionnaire contenant:
            - 'difference': différence absolue (value2 - value1)
            - 'percentage': différence en pourcentage (0 si value1 = 0)
            - 'is_equal': bool indiquant si les valeurs sont égales
    """
    difference = value2 - value1
    
    # Éviter la division par zéro pour le calcul de pourcentage
    if value1 == 0:
        percentage = 0.0 if value2 == 0 else float('inf')
    else:
        percentage = (difference / abs(value1)) * 100
    
    return {
        'difference': difference,
        'percentage': percentage,
        'is_equal': abs(difference) < 1e-9  # Tolérance pour les comparaisons de floats
    }


def compare_dataframe_columns(df1, df2, columns=None):
    """
    Compare les sommes des colonnes de deux dataframes.
    
    Args:
        df1 (pd.DataFrame): Premier dataframe (référence).
        df2 (pd.DataFrame): Deuxième dataframe à comparer.
        columns (list, optional): Liste des colonnes à comparer. 
                                 Si None, compare toutes les colonnes numériques communes.
    
    Returns:
        dict: Dictionnaire avec les résultats de comparaison pour chaque colonne.
              Format: {
                  'column_name': {
                      'sum_df1': float,
                      'sum_df2': float,
                      'difference': float,
                      'percentage': float,
                      'is_equal': bool
                  }
              }
    
    Raises:
        ValueError: Si les dataframes sont vides ou n'ont pas de colonnes communes.
    """
    if df1.empty or df2.empty:
        raise ValueError("Les dataframes ne peuvent pas être vides.")
    
    # Déterminer les colonnes à comparer
    if columns is None:
        # Colonnes numériques communes
        numeric_cols1 = df1.select_dtypes(include=['number']).columns
        numeric_cols2 = df2.select_dtypes(include=['number']).columns
        columns = list(set(numeric_cols1) & set(numeric_cols2))
    
    if not columns:
        raise ValueError("Aucune colonne commune à comparer trouvée.")
    
    results = {}
    for col in columns:
        try:
            sum1 = df1[col].sum()
            sum2 = df2[col].sum()
            diff_info = _calculate_difference(sum1, sum2)
            
            results[col] = {
                'sum_df1': sum1,
                'sum_df2': sum2,
                'difference': diff_info['difference'],
                'percentage': diff_info['percentage'],
                'is_equal': diff_info['is_equal']
            }
        except (KeyError, TypeError):
            # Ignore les colonnes qui ne peuvent pas être converties en nombres
            continue
    
    return results


def _format_value(value):
    """
    Formate une valeur numérique pour l'affichage.
    
    Args:
        value (float): La valeur à formater.
    
    Returns:
        str: Valeur formatée avec 2 décimales.
    """
    if isinstance(value, float) and value == float('inf'):
        return "∞"
    return f"{value:,.2f}"


def _get_status_marker(is_equal, difference):
    """
    Retourne un marqueur de statut basé sur l'égalité et la différence.
    
    Args:
        is_equal (bool): Si les valeurs sont égales.
        difference (float): La différence entre les valeurs.
    
    Returns:
        str: Marqueur de statut (✓, ✗ ou ⚠).
    """
    if is_equal:
        return "✓ ÉGAL"
    elif difference > 0:
        return "✗ AUGMENTATION"
    else:
        return "✗ DIMINUTION"


def print_comparison_report(comparison_results, df1_name="DataFrame1", df2_name="DataFrame2"):
    """
    Affiche un rapport formaté de la comparaison des colonnes.
    
    Args:
        comparison_results (dict): Résultats de compare_dataframe_columns().
        df1_name (str): Nom du premier dataframe pour l'affichage.
        df2_name (str): Nom du deuxième dataframe pour l'affichage.
    
    Returns:
        None: Affiche le rapport en console.
    """
    if not comparison_results:
        print("Aucun résultat à afficher.")
        return
    
    print("\n" + "="*80)
    print(f"RAPPORT DE COMPARAISON: {df1_name} vs {df2_name}")
    print("="*80)
    
    for column, data in comparison_results.items():
        status = _get_status_marker(data['is_equal'], data['difference'])
        print(f"\n📊 Colonne: {column}")
        print(f"   {df1_name}: {_format_value(data['sum_df1'])}")
        print(f"   {df2_name}: {_format_value(data['sum_df2'])}")
        print(f"   Différence: {_format_value(data['difference'])} ({_format_value(data['percentage'])}%)")
        print(f"   Statut: {status}")
    
    print("\n" + "="*80 + "\n")


def _extract_spreadsheet_id(url):
    """
    Extrait l'ID du Google Sheet à partir de son URL.
    
    Args:
        url (str): URL du Google Sheet (ex: https://docs.google.com/spreadsheets/d/{ID}/edit#gid=0)
    
    Returns:
        str: L'ID du spreadsheet ou l'URL originale si déjà un ID
    """
    # Si c'est déjà un ID (pas une URL), on le retourne
    if not url.startswith('http'):
        return url
    
    # Extrait l'ID de l'URL
    match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
    if match:
        return match.group(1)
    return url


def _format_comparison_results_to_dataframe(comparison_results, df1_name="DataFrame1", df2_name="DataFrame2"):
    """
    Convertit les résultats de comparaison en DataFrame pour export.
    
    Args:
        comparison_results (dict): Résultats de compare_dataframe_columns().
        df1_name (str): Nom du premier dataframe.
        df2_name (str): Nom du deuxième dataframe.
    
    Returns:
        pd.DataFrame: DataFrame formaté avec les résultats.
    """
    data = []
    
    for column, result in comparison_results.items():
        status = _get_status_marker(result['is_equal'], result['difference'])
        data.append({
            'Colonne': column,
            f'Somme {df1_name}': result['sum_df1'],
            f'Somme {df2_name}': result['sum_df2'],
            'Différence': result['difference'],
            'Pourcentage': result['percentage'],
            'Statut': status
        })
    
    return pd.DataFrame(data)


def compare_and_print(df1, df2, columns=None, df1_name="DataFrame1", df2_name="DataFrame2", 
                      google_sheets_url=None, sheet_name=None):
    """
    Fonction wrapper qui compare et affiche le rapport en une seule appel.
    Optionnellement, exporte les résultats dans un Google Sheet.
    
    Args:
        df1 (pd.DataFrame): Premier dataframe (référence).
        df2 (pd.DataFrame): Deuxième dataframe à comparer.
        columns (list, optional): Liste des colonnes à comparer.
        df1_name (str): Nom du premier dataframe pour l'affichage.
        df2_name (str): Nom du deuxième dataframe pour l'affichage.
        google_sheets_url (str, optional): URL ou ID du Google Sheet pour export.
        sheet_name (str, optional): Nom de la feuille cible dans le Google Sheet.
    
    Returns:
        dict: Résultats de la comparaison.
    """
    results = compare_dataframe_columns(df1, df2, columns)
    print_comparison_report(results, df1_name, df2_name)
    
    # Export vers Google Sheets si URL fournie
    if google_sheets_url:
        try:
            # Convertir les résultats en DataFrame
            df_results = _format_comparison_results_to_dataframe(results, df1_name, df2_name)
            
            # Obtenir le client gspread
            gspread_client = client_gspread()
            
            # Extraire l'ID du spreadsheet
            spreadsheet_id = _extract_spreadsheet_id(google_sheets_url)
            
            # Sauvegarder dans Google Sheets
            save_dataframe_to_sheet(spreadsheet_id, gspread_client, df_results, sheet_name)
            print(f"\n✅ Résultats exportés vers Google Sheets: {sheet_name or 'Première feuille'}")
        except Exception as e:
            print(f"\n⚠️ Erreur lors de l'export Google Sheets: {str(e)}")
    
    return results



