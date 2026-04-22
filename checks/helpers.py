import pandas as pd
import io
import re
from typing import List, Dict



def find_duplicates_in_list_of_dfs(dfs, column):
    """
    Pour chaque DataFrame dans une liste, trouve les doublons dans la colonne spécifiée.

    Args:
        dfs (list of pd.DataFrame): Liste de DataFrames à analyser
        column (str): Nom de la colonne sur laquelle chercher les doublons

    Returns:
        dict: Clé = index du DataFrame, Valeur = DataFrame des doublons
    """
    duplicates_dict = {}

    for i, df in enumerate(dfs):
        if column not in df.columns:
            print(f"⚠️ DataFrame {i} : la colonne '{column}' n'existe pas.")
            continue

        # Trouve les doublons
        df_duplicates = df[df.duplicated(subset=[column], keep=False)]

        if not df_duplicates.empty:
            duplicates_dict[i] = df_duplicates
            print(f"🔹 DataFrame {i} : {len(df_duplicates)} doublons trouvés dans '{column}'")
        else:
            print(f"✅ DataFrame {i} : aucun doublon dans '{column}'")

    return duplicates_dict

def check_same_col_sum(df_left: pd.DataFrame,
                       df_right: pd.DataFrame,
                       col: str,
                       dropna: bool = True,
                       atol: float = 0.0,
                       rtol: float = 0.0):
    """
    Vérifie que la somme de la colonne `col` est la même dans 2 DataFrames.

    Parameters
    ----------
    df_left, df_right : pd.DataFrame
        DataFrames à comparer
    col : str
        Nom de la colonne (même intitulé dans les 2 df)
    dropna : bool
        Si True, les NaN sont traités comme 0 (via fillna(0))
    atol, rtol : float
        Tolérances absolue et relative (utile si float)

    Returns
    -------
    result : dict
        Résumé des sommes + delta
    ok : bool
        True si égalité (avec tolérances), sinon False
    """
    if col not in df_left.columns:
        raise KeyError(f"Colonne '{col}' absente de df_left")
    if col not in df_right.columns:
        raise KeyError(f"Colonne '{col}' absente de df_right")

    s1 = pd.to_numeric(df_left[col], errors="coerce")
    s2 = pd.to_numeric(df_right[col], errors="coerce")

    if dropna:
        s1 = s1.fillna(0)
        s2 = s2.fillna(0)

    sum1 = float(s1.sum())
    sum2 = float(s2.sum())
    delta = sum1 - sum2

    ok = abs(delta) <= (atol + rtol * abs(sum2))

    result = {
        "col": col,
        "sum_df_left": sum1,
        "sum_df_right": sum2,
        "delta_left_minus_right": delta,
        "atol": atol,
        "rtol": rtol,
        "ok": ok
    }
    return result, ok

def check_sums_against_final(
    df_final: pd.DataFrame,
    list_of_dfs: List[pd.DataFrame],
    key_col: str = "n_structure",
    dropna: bool = True,
    atol: float = 0.0,
    rtol: float = 0.0
) -> List[Dict]:

    report = []

    for i, df in enumerate(list_of_dfs):
        print(f"\n🔎 Vérification DataFrame {i}")

        cols_to_check = [col for col in df.columns if col != key_col]

        for col in cols_to_check:

            if col not in df_final.columns:
                print(f"   ⚠️ Colonne '{col}' absente du df_final → ignorée")
                continue

            try:
                result, ok = check_same_col_sum(
                    df_left=df,
                    df_right=df_final,
                    col=col,
                    dropna=dropna,
                    atol=atol,
                    rtol=rtol
                )

                summary = {
                    "df_index": i,
                    "col": col,
                    "sum_df_individual": result["sum_df_left"],
                    "sum_df_final": result["sum_df_right"],
                    "atol": atol,
                    "rtol": rtol,
                    "ok": ok
                }

                report.append(summary)

                if ok:
                    print(
                        f"   ✅ '{col}' OK | "
                        f"individuel = {summary['sum_df_individual']} | "
                        f"final = {summary['sum_df_final']}"
                    )
                else:
                    print(
                        f"   ❌ '{col}' KO | "
                        f"individuel = {summary['sum_df_individual']} | "
                        f"final = {summary['sum_df_final']}"
                    )

            except Exception as e:
                print(f"   ⚠️ Erreur sur '{col}' : {e}")

    return report

