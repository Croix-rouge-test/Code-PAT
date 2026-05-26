import os
import sys
import json
import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from gspread_dataframe import get_as_dataframe
import re
sys.path.append(os.path.abspath("./")) 
from utils import *

##################################################################################################################
# ------------------------------
# Comparaison des sommes des colonnes entre les deux dataframes UL et DT
# ------------------------------
##################################################################################################################

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

###############################################################################################################
# ------------------------------
# Comparaison des données par DT entre UL agg par DT de rattachement et données DT
# ------------------------------
###############################################################################################################

# ---------------------------------------------------------------------------
# 1. Helpers — clé DT
# ---------------------------------------------------------------------------
 
def _extract_dt_integer(value) -> str:
    """
    Extrait le(s) entier(s) présent(s) dans une valeur de DT_de_rattachement.
 
    Exemples :
        "DT_042"  -> "42"
        "042"     -> "42"
        42        -> "42"
        "Région 3 - DT 12" -> "12"  (dernier entier trouvé)
 
    Args:
        value: La valeur brute de la cellule DT_de_rattachement.
 
    Returns:
        str: L'entier extrait sous forme de chaîne, ou str(value) en fallback.
    """
    if pd.isna(value):
        return None
    text = str(value).strip()
    numbers = re.findall(r'\d+', text)
    if numbers:
        return str(int(numbers[-1]))   # dernier entier, sans zéros en tête
    return text
 
 
def _normalize_dt_key(value) -> str:
    """
    Normalise une clé DT (n_structure ou DT_de_rattachement) pour la jointure.
 
    Supprime les zéros en tête et met en chaîne.
    """
    if pd.isna(value):
        return None
    numbers = re.findall(r'\d+', str(value))
    if numbers:
        return str(int(numbers[-1]))
    return str(value).strip()
 
 
# ---------------------------------------------------------------------------
# 2. Groupby df_UL
# ---------------------------------------------------------------------------
 
def group_ul_by_dt(
    df_UL: pd.DataFrame,
    dt_col: str = 'DT_de_rattachement',
    columns: list = None,
    extract_integer: bool = True,
) -> pd.DataFrame:
    """
    Groupe df_UL par DT et agrège les colonnes numériques par somme.
 
    Args:
        df_UL (pd.DataFrame): DataFrame source UL.
        dt_col (str): Nom de la colonne DT dans df_UL.
        columns (list, optional): Colonnes numériques à conserver avant groupby.
                                  Si None, toutes les colonnes numériques sont utilisées.
        extract_integer (bool): Si True, extrait uniquement l'entier de dt_col
                                 pour faciliter la jointure avec n_structure.
 
    Returns:
        pd.DataFrame: DataFrame groupé, indexé sur la clé DT normalisée.
    """
    df = df_UL.copy()
 
    # Clé de jointure normalisée
    key_col = '__dt_key__'
    if extract_integer:
        df[key_col] = df[dt_col].apply(_extract_dt_integer)
    else:
        df[key_col] = df[dt_col].apply(_normalize_dt_key)
 
    # Colonnes à agréger
    if columns is None:
        num_cols = df.select_dtypes(include='number').columns.tolist()
    else:
        num_cols = [c for c in columns if c in df.columns]
 
    df_grouped = (
        df.groupby(key_col, dropna=True)[num_cols]
        .sum()
        .reset_index()
        .rename(columns={key_col: '__dt_key__'})
    )
    df_grouped = df_grouped.set_index('__dt_key__')
    return df_grouped
 

def _ensure_scalar_value(value, df_name: str, key, column: str):
    """Convertit une valeur extraite en scalaire et fournit un message détaillé en cas d'erreur."""
    if isinstance(value, pd.Series):
        raise ValueError(
            f"Valeur non scalaire détectée dans {df_name} pour la clé={key!r}, colonne={column!r}. "
            f"{len(value)} lignes correspondent à cette clé. Indexs concernés: {list(value.index)}. "
            "Vérifier les doublons dans la clé de jointure ou les valeurs de la colonne."
        )
    if isinstance(value, pd.DataFrame):
        raise ValueError(
            f"Valeur non scalaire (DataFrame) détectée dans {df_name} pour la clé={key!r}, colonne={column!r}."
        )
    if pd.isna(value):
        return 0.0
    try:
        return float(value)
    except Exception as exc:
        raise ValueError(
            f"Impossible de convertir en float la valeur de {df_name} pour la clé={key!r}, colonne={column!r}: {value!r}"
        ) from exc
 
 
# ---------------------------------------------------------------------------
# 3. Comparaison ligne par ligne
# ---------------------------------------------------------------------------
 
def compare_dt_row_by_row(
    df_DT: pd.DataFrame,
    df_UL: pd.DataFrame,
    columns: list = None,
    dt_key_dt: str = 'n_structure',
    dt_col_ul: str = 'DT_de_rattachement',
    extract_integer: bool = True,
) -> pd.DataFrame:
    """
    Compare df_DT et df_UL (groupé par DT) ligne par ligne.
 
    La jointure se fait sur la clé DT normalisée :
      - df_DT  : colonne ``dt_key_dt`` (ex: n_structure)
      - df_UL  : colonne ``dt_col_ul``  (ex: DT_de_rattachement)
 
    Args:
        df_DT (pd.DataFrame): DataFrame DT (référence).
        df_UL (pd.DataFrame): DataFrame UL brut (sera groupé en interne).
        columns (list, optional): Colonnes numériques à comparer.
                                   Si None, toutes les colonnes numériques communes.
        dt_key_dt (str): Colonne-clé dans df_DT.
        dt_col_ul (str): Colonne DT dans df_UL.
        extract_integer (bool): Extraction de l'entier dans DT_de_rattachement.
 
    Returns:
        pd.DataFrame: Résultat de comparaison avec les colonnes :
            DT_key | Colonne | Valeur_DT | Valeur_UL | Différence | Pourcentage | Statut
    
    Raises:
        ValueError: Si les dataframes sont vides ou sans colonnes communes.
    """
    if df_DT.empty or df_UL.empty:
        raise ValueError("Les dataframes ne peuvent pas être vides.")
 
    # --- Préparer df_DT avec clé normalisée ---
    df_dt = df_DT.copy()

    df_dt['__dt_key__'] = df_dt[dt_key_dt].astype(int).astype(str)
    if df_dt['__dt_key__'].duplicated().any():
        duplicated_keys = sorted(df_dt['__dt_key__'][df_dt['__dt_key__'].duplicated()].unique())
        raise ValueError(
            f"Clés DT dupliquées détectées dans df_DT après normalisation : {duplicated_keys}. "
            "Vérifier la colonne de jointure n_structure et les valeurs de la table DT."
        )
    df_dt = df_dt.set_index('__dt_key__')
 
    # --- Grouper df_UL ---
    df_ul_grouped = group_ul_by_dt(
        df_UL,
        dt_col=dt_col_ul,
        columns=columns,
        extract_integer=extract_integer,
    )
 
    # --- Colonnes à comparer ---
    if columns is None:
        num_dt = df_dt.select_dtypes(include='number').columns
        num_ul = df_ul_grouped.select_dtypes(include='number').columns
        columns = list(set(num_dt) & set(num_ul))
 
    if not columns:
        raise ValueError("Aucune colonne numérique commune trouvée.")
 
    # --- Clés communes ---
    common_keys = sorted(set(df_dt.index) & set(df_ul_grouped.index))
    if not common_keys:
        print(set(df_ul_grouped.index))
        raise ValueError("Aucune DT commune entre df_DT et df_UL groupé.")
 
    # --- Construction du résultat ---
    rows = []
    for key in common_keys:
        for col in columns:
            v_dt = df_dt.loc[key, col] if col in df_dt.columns else float('nan')
            v_ul = df_ul_grouped.loc[key, col] if col in df_ul_grouped.columns else float('nan')
 
            v_dt = _ensure_scalar_value(v_dt, 'df_DT', key, col)
            v_ul = _ensure_scalar_value(v_ul, 'df_UL groupé', key, col)
 
            diff = _calculate_difference(v_dt, v_ul)
            rows.append({
                'DT_key':      key,
                'Colonne':     col,
                'Valeur_DT':   v_dt,
                'Valeur_UL':   v_ul,
                'Différence':  diff['difference'],
                'Pourcentage': diff['percentage'],
                'Statut':      _get_status_marker(diff['is_equal'], diff['difference']),
            })
 
    return pd.DataFrame(rows)
 
 
# ---------------------------------------------------------------------------
# 4. Affichage console
# ---------------------------------------------------------------------------
 
def print_dt_comparison_report(
    df_result: pd.DataFrame,
    df_dt_name: str = "df_DT",
    df_ul_name: str = "df_UL (groupé)",
) -> None:
    """
    Affiche un rapport console lisible à partir du DataFrame de résultats.
 
    Args:
        df_result (pd.DataFrame): Sortie de compare_dt_row_by_row().
        df_dt_name (str): Libellé affiché pour df_DT.
        df_ul_name (str): Libellé affiché pour df_UL groupé.
    """
    if df_result.empty:
        print("Aucun résultat à afficher.")
        return
 
    print("\n" + "=" * 80)
    print(f"RAPPORT DE COMPARAISON LIGNE PAR LIGNE : {df_dt_name} vs {df_ul_name}")
    print("=" * 80)
 
    for dt_key, group in df_result.groupby('DT_key', sort=False):
        print(f"\n🏷  DT : {dt_key}")
        for _, row in group.iterrows():
            print(f"   📊 {row['Colonne']}")
            print(f"      {df_dt_name} : {_format_value(row['Valeur_DT'])}")
            print(f"      {df_ul_name}  : {_format_value(row['Valeur_UL'])}")
            pct = row['Pourcentage']
            pct_str = "∞" if pct == float('inf') else f"{pct:,.2f}%"
            print(f"      Δ : {_format_value(row['Différence'])} ({pct_str})")
            print(f"      Statut : {row['Statut']}")
 
    print("\n" + "=" * 80 + "\n")
 
 
# ---------------------------------------------------------------------------
# 5. Export Google Sheets + wrapper principal
# ---------------------------------------------------------------------------
 
def compare_dt_and_export(
    df_DT: pd.DataFrame,
    df_UL: pd.DataFrame,
    columns: list = None,
    dt_key_dt: str = 'n_structure',
    dt_col_ul: str = 'DT_de_rattachement',
    extract_integer: bool = True,
    df_dt_name: str = "df_DT",
    df_ul_name: str = "df_UL",
    google_sheets_url: str = None,
    sheet_name: str = None,
    show_all: bool = True,
) -> pd.DataFrame:
    """
    Wrapper principal : compare df_DT et df_UL, affiche le rapport,
    et exporte optionnellement vers Google Sheets.
 
    Args:
        df_DT (pd.DataFrame): DataFrame DT.
        df_UL (pd.DataFrame): DataFrame UL brut.
        columns (list, optional): Colonnes à comparer (None = toutes communes).
        dt_key_dt (str): Colonne-clé dans df_DT.
        dt_col_ul (str): Colonne DT dans df_UL.
        extract_integer (bool): Extraction entier dans DT_de_rattachement.
        df_dt_name (str): Nom affiché pour df_DT.
        df_ul_name (str): Nom affiché pour df_UL.
        google_sheets_url (str, optional): URL ou ID du Google Sheet cible.
        sheet_name (str, optional): Onglet cible dans le Google Sheet.
        show_all (bool): Si False, exporte uniquement les lignes avec écart (Statut ≠ ✓ ÉGAL).
 
    Returns:
        pd.DataFrame: DataFrame complet des résultats de comparaison.
    """
    df_result = compare_dt_row_by_row(
        df_DT, df_UL, columns, dt_key_dt, dt_col_ul, extract_integer
    )
    print_dt_comparison_report(df_result, df_dt_name, df_ul_name)
 
    if google_sheets_url:
        try:
            df_export = df_result if show_all else df_result[df_result['Statut'] != '✓ ÉGAL']
 
            gspread_client = client_gspread()
            spreadsheet_id = _extract_spreadsheet_id(google_sheets_url)
            save_dataframe_to_sheet(spreadsheet_id, gspread_client, df_export, sheet_name)
            print(f"✅ Résultats exportés → onglet '{sheet_name or 'Première feuille'}'")
        except Exception as e:
            print(f"⚠️  Erreur export Google Sheets : {e}")
 
    return df_result

###############################################################################################################
# ------------------------------
# Comparaison des sommes des colonnes entre deux dataframes avec rapport détaillé et export vers Google Sheets
# ------------------------------
###############################################################################################################

 
 
# ---------------------------------------------------------------------------
# Constantes — noms d'onglets par défaut dans le Google Sheet de référence
# ---------------------------------------------------------------------------
 
SHEET_UL    = 'UL'
SHEET_DT    = 'DT'
SHEET_TOTAL = 'Total'
 
 
# ---------------------------------------------------------------------------
# 1. Chargement des feuilles de référence
# ---------------------------------------------------------------------------
 
def load_reference_sheets(
    gspread_client,
    reference_url: str,
    sheet_dt: str = SHEET_DT,
) -> dict:
    """
    Charge les trois feuilles de référence depuis un Google Sheet.
 
    Les cellules non renseignées (NaN) sont conservées telles quelles :
    elles signifient « pas de valeur de référence » et seront ignorées
    lors de la comparaison.
 
    Args:
        gspread_client: Client gspread authentifié (issu de client_gspread()).
        reference_url (str): URL ou ID du Google Sheet de référence.
        sheet_ul (str): Nom de l'onglet UL.
        sheet_dt (str): Nom de l'onglet DT.
        sheet_total (str): Nom de l'onglet Total.
 
    Returns:
        dict: {'UL': df_ul_ref, 'DT': df_dt_ref, 'Total': df_total_ref}
    """
    from gspread_dataframe import get_as_dataframe
 
    spreadsheet = gspread_client.open_by_url(reference_url)
 
    def _load(name):
        ws = spreadsheet.worksheet(name)
        return get_as_dataframe(ws, evaluate_formulas=True)
 
    return {
        'DT':    _load(sheet_dt),
    }
 
 
# ---------------------------------------------------------------------------
# 2. Comparaison source vs référence
# ---------------------------------------------------------------------------
 
def compare_with_reference(
    df_source: pd.DataFrame,
    df_ref: pd.DataFrame,
    columns: list = None,
    id_col: str = None,
) -> pd.DataFrame:
    """
    Compare df_source (données terrain réelles) avec df_ref (feuille de référence).
 
    Règles :
      - Seules les cellules **renseignées** dans df_ref (non-NaN) sont comparées.
      - Les NaN dans df_source sont traités comme 0.
      - La jointure se fait sur id_col (si fourni) ou sur la position des lignes.
 
    Args:
        df_source (pd.DataFrame): Données source (df_UL ou df_DT).
        df_ref (pd.DataFrame): Feuille de référence chargée depuis Google Sheets.
        columns (list, optional): Colonnes numériques à comparer.
                                   Si None, toutes les colonnes numériques communes
                                   entre df_source et df_ref.
        id_col (str, optional): Colonne identifiant pour la jointure (ex: 'n_structure').
                                 Si None, jointure par position.
 
    Returns:
        pd.DataFrame: Colonnes :
            [id_col ou 'Index'] | Colonne | Valeur_Source | Valeur_Ref |
            Différence | Pourcentage | Statut
 
    Raises:
        ValueError: Si aucune colonne commune n'est trouvée.
    """
    src = df_source.copy()
    ref = df_ref.copy()
 
    # --- Déterminer les colonnes à comparer ---
    if columns is None:
        num_src = set(src.select_dtypes(include='number').columns)
        num_ref = set(ref.select_dtypes(include='number').columns)
        columns = list(num_src & num_ref)
 
    if not columns:
        raise ValueError("Aucune colonne numérique commune entre source et référence.")
 
    # --- Alignement par id_col ou par position ---
    if id_col and id_col in src.columns and id_col in ref.columns:
        src = src.set_index(id_col)
        ref = ref.set_index(id_col)
        common_idx = src.index.intersection(ref.index)
        src = src.loc[common_idx]
        ref = ref.loc[common_idx]
        index_label = id_col
    else:
        # Alignement par position — tronquer à la plus courte
        min_len = min(len(src), len(ref))
        src = src.iloc[:min_len].reset_index(drop=True)
        ref = ref.iloc[:min_len].reset_index(drop=True)
        index_label = 'Index'
 
    # --- Construire le résultat ---
    rows = []
    for idx in src.index:
        for col in columns:
            val_ref_raw = ref.loc[idx, col] if col in ref.columns else float('nan')
 
            # Ignorer les cellules non renseignées dans la référence
            if pd.isna(val_ref_raw):
                continue
 
            val_src_raw = src.loc[idx, col] if col in src.columns else float('nan')
 
            # NaN dans la source → 0
            val_src = 0.0 if pd.isna(val_src_raw) else float(val_src_raw)
            val_ref = float(val_ref_raw)
 
            diff = _calculate_difference(val_ref, val_src)
            rows.append({
                index_label:     idx,
                'Colonne':       col,
                'Valeur_Source': val_src,
                'Valeur_Ref':    val_ref,
                'Différence':    diff['difference'],
                'Pourcentage':   diff['percentage'],
                'Statut':        _get_status_marker(diff['is_equal'], diff['difference']),
            })
 
    return pd.DataFrame(rows)
 
 
# ---------------------------------------------------------------------------
# 3. Affichage console
# ---------------------------------------------------------------------------
 
def print_reference_comparison_report(
    df_result: pd.DataFrame,
    source_name: str = "Source",
    ref_name: str = "Référence",
) -> None:
    """
    Affiche un rapport console lisible pour la comparaison source vs référence.
 
    Args:
        df_result (pd.DataFrame): Sortie de compare_with_reference().
        source_name (str): Libellé des données source.
        ref_name (str): Libellé des données de référence.
    """
    if df_result.empty:
        print("Aucun résultat à afficher (aucune cellule de référence renseignée ?).")
        return
 
    id_col = df_result.columns[0]   # première colonne = identifiant
 
    print("\n" + "=" * 80)
    print(f"RAPPORT COMPARAISON RÉFÉRENCE : {source_name} vs {ref_name}")
    print("=" * 80)
 
    for id_val, group in df_result.groupby(id_col, sort=False):
        print(f"\n🏷  {id_col} : {id_val}")
        for _, row in group.iterrows():
            pct = row['Pourcentage']
            pct_str = "∞" if pct == float('inf') else f"{pct:,.2f}%"
            print(f"   📊 {row['Colonne']}")
            print(f"      {ref_name}   : {_format_value(row['Valeur_Ref'])}")
            print(f"      {source_name} : {_format_value(row['Valeur_Source'])}")
            print(f"      Δ : {_format_value(row['Différence'])} ({pct_str})")
            print(f"      Statut : {row['Statut']}")
 
    print("\n" + "=" * 80 + "\n")
 
 
# ---------------------------------------------------------------------------
# 4. Wrapper principal
# ---------------------------------------------------------------------------
 
def compare_reference_and_export(
    df_DT: pd.DataFrame,
    reference_url: str,
    output_url: str,
    columns_dt: list = None,
    columns_total: list = None,
    id_col_ul: str = None,
    id_col_dt: str = None,
    sheet_dt_ref: str = SHEET_DT, 
    output_sheet_dt: str = 'Comparaison_DT',
    output_sheet_total: str = 'Comparaison_Total',
    show_all: bool = True,
) -> dict:

    gspread_client  = client_gspread()
    output_sheet_id = _extract_spreadsheet_id(output_url)

    # --- Charger les feuilles de référence ---
    print("📥 Chargement des feuilles de référence…")
    refs = load_reference_sheets(
        gspread_client, reference_url,
        sheet_dt_ref,
    )

    results = {}


    # --- Comparaison DT ---
    print("\n🔍 Comparaison par DT…")
    df_res_dt = compare_with_reference(df_DT, refs['DT'], columns_dt, id_col_dt)
    print_reference_comparison_report(df_res_dt, "df_DT", "Référence DT")
    results['DT'] = df_res_dt

    # --- Comparaison Total (basée sur df_DT) ---
    print("\n🔍 Comparaison Total…")

    

    # 🔑 1. Construire UNE ligne de total à partir des DT
    num_cols_dt = df_DT.select_dtypes(include='number').columns.tolist()
    df_dt_total = df_DT[num_cols_dt].sum().to_frame().T.reset_index(drop=True)

    # 🔑 2. Récupérer UNE seule ligne de référence (ligne "Total")
    df_ref_total = refs['DT'][refs['DT']['n_structure'] == 'Total' ]

    if df_ref_total.shape[0] > 1:
        # 👉 on prend la ligne qui contient "Total" si elle existe
        mask_total = df_ref_total.astype(str).apply(
            lambda row: row.str.contains("total", case=False, na=False)
        ).any(axis=1)

        if mask_total.any():
            df_ref_total = df_ref_total[mask_total].head(1)
        else:
            print("⚠️ Aucune ligne 'Total' trouvée → on prend la première")
            df_ref_total = df_ref_total.head(1)

    # 🔑 3. Comparaison ligne unique vs ligne unique
    df_res_total = compare_with_reference(
        df_dt_total,
        df_ref_total,
        columns_total,
        None
    )

    print_reference_comparison_report(df_res_total, "df_DT (total)", "Référence Total")
    results['Total'] = df_res_total

    # --- Export ---
    def _export(df_res, sheet_out, label):
        try:
            df_out = df_res if show_all else df_res[df_res['Statut'] != '✓ ÉGAL']
            save_dataframe_to_sheet(output_sheet_id, gspread_client, df_out, sheet_out)
            print(f"✅ {label} exporté → onglet '{sheet_out}'")
        except Exception as e:
            print(f"⚠️ Erreur export {label} : {e}")

    print("\n📤 Export vers Google Sheets…")
    _export(df_res_dt,    output_sheet_dt,    "DT")
    _export(df_res_total, output_sheet_total, "Total")

    return results

