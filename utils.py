import pandas as pd
import io
import re
import unicodedata
import re
import torch
from sentence_transformers import SentenceTransformer, util
from typing import List, Dict


# Mensualisation 

def monthly_parsing(df, year):
  def month_conditions(date):
    months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet' , 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    for i in range(len(months)):
      if date.month == i + 1 :
        return months[i]
  df['Mois'] = df.apply(lambda x: month_conditions(x['date']), axis=1)
  df['Année'] = year
  return df


# Exporter le fichier de sortie en xlsx


def export_to_excel_download(dataframe, file_name='data.xlsx'):
    """
    Exporte un DataFrame en fichier Excel et le télécharge depuis Google Colab.

    Parameters:
        dataframe (pd.DataFrame): Le DataFrame à exporter.
        file_name (str): Le nom du fichier Excel à télécharger (par défaut 'data.xlsx').
    """
    dataframe.to_excel(file_name, index=False)
    files.download(file_name)

# Ouvrir un google sheet

def sheet_to_dataframe(client, url, sheet_index=0, sheet_name=None, header_row=1):
    """
    Ouvre une feuille Google Sheets et crée un DataFrame Pandas à partir de ses données.

    Cette fonction prend en entrée l'URL de la feuille Google Sheets, un client Google Sheets autorisé,
    l'index de la page souhaitée ou le nom de la feuille, et la ligne utilisée comme en-tête. Elle renvoie les données de la
    feuille sous forme de DataFrame Pandas.

    Args:
        url (str): L'URL de la feuille Google Sheets.
        client (gspread.Client): Client Google Sheets autorisé.
        sheet_index (int, optional): L'index de la page à ouvrir dans la feuille. Par défaut, 0 (première page).
        sheet_name (str, optional): Le nom de la feuille à ouvrir. Si fourni, prioritaire sur sheet_index.
        header_row (int, optional): Le numéro de la ligne à utiliser comme en-têtes de colonnes pour le DataFrame.
                                   Par défaut, 1 (la première ligne de données après l'en-tête de feuille).

    Returns:
        pd.DataFrame: Un DataFrame Pandas contenant les données de la feuille avec la première ligne spécifiée
                      comme en-tête des colonnes.
    """

    # Ouvre la feuille Google Sheets à partir de l'URL
    sheet = client.open_by_url(url)

    # Sélectionne la page (worksheet) souhaitée
    if sheet_name:
        worksheet = sheet.worksheet(sheet_name)
    else:
        worksheet = sheet.get_worksheet(sheet_index)

    # Récupère toutes les valeurs de la page
    data = worksheet.get_all_values()

    # Crée le DataFrame en utilisant la ligne spécifiée comme en-tête
    df = pd.DataFrame(data[header_row:], columns=data[header_row - 1])

    print(f"✅ Chargement des données réalisées")
    print(f"    Sheet : {sheet.title}")
    print(f"    Feuille {sheet_index + 1 if not sheet_name else ''} : {worksheet.title} ({len(data) - header_row} lignes et {len(data[header_row - 1])} colonnes)\n")

    return df

# Definition des filtres classiques

# #Fonction filtre simple (on met le nom de la colonne)
# def filtre(df, col, key, filters=FILTERS):
#     values = filters[col][key]
#     return df.loc[df[col].isin(values)].copy()

# #Fonction filtre et remplace
# def filtre_et_remplace(df, col, key, filters=FILTERS):
#   values = filters[col][key]
#   mask = df[col].isin(values)
#   df.drop(df.index[~mask], inplace=True)


# # def filtre(df, key, filters=FILTERS):
# def filtre(df, key, filters=FILTERS_PEGASS):
#     rule = filters[key]
#     col = rule["col"]
#     values = rule["values"]
#     return df.loc[df[col].isin(values)]


#Fonction filtre date

def filtre_2025(df, date_col="debut_inscription", dayfirst=True):
    s = pd.to_datetime(df[date_col], errors="coerce", dayfirst=dayfirst)
    return df.loc[s.between("2025-01-01 00:00", "2026-01-01 00:00", inclusive="left")]

#Fonction utile pour renommer automatiquement les variables
#Attention pour simplifier la fonction il faut que le nom initial de la Dataframe soit le même avec la colonne "nom tablme du dictionnaire de données :  Pegass_Inscription_rename = renommer_par_nom_table(PEGASS_PegassInscription, "PEGASS_PegassInscription", mapping_df)"

#On récupère la table qui sera la table "dictionnaire de données" = sans doute un url
def renommer_par_nom_table(df, nom_table, mapping_df):
    # On filtre le mapping sur cette table
    mapping_table = mapping_df[mapping_df["nom_table"] == nom_table]
    mapping_dict = dict(zip(mapping_table["nom_variable"], mapping_table["rename"]))
    return df.rename(columns=mapping_dict)

def filtre(df, key, filters=None):
    # Applique un filtre défini dans un dictionnaire de règles :
    # filters = {
    #     "nom_filtre": {"col": "nom_colonne", "values": [...]}
    # }

    # Si filters n'est pas fourni, on utilise le dict global FILTERS_PEGASS.
    # ⚠ Ici, on ne touche à FILTERS_PEGASS qu'au moment de l'APPEL, pas à la définition

    if filters is None:
        filters = globals()["FILTERS_PEGASS"]  # va chercher le dict global au moment de l'appel

    rule = filters[key]
    col = rule["col"]
    values = rule["values"]

    # si values est une seule valeur, on l'encapsule dans une liste
    if not isinstance(values, (list, tuple, set)):
        values = [values]

    return df.loc[df[col].isin(values)]


# Normaliser les libellés des structures

def normalize_structure(structure: str) -> str:
    if structure is None:
        return structure

    # Enlève les accents (UNITÉ -> UNITE, DÉLÉGATION -> DELEGATION, etc.)
    s = unicodedata.normalize("NFD", structure)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")

    # Remplacements (insensible à la casse)
    s = re.sub(r"\bUNITE\s+LOCALE\b", "UL", s, flags=re.IGNORECASE)
    s = re.sub(r"\bDELEGATION\s+TERRITORIALE\b", "DT", s, flags=re.IGNORECASE)

    return s
# Rapprochement libellés quand on a ni les codes 

def rapprochement_libelles(df_ref, df_traiter, colonne_analyser, seuil_alerte=0.80, embeddings_file='reference_embeddings.pt', silent=True):
    # Ensure df_ref['nom_structure'] is string type and handle potential NaNs
    df_ref['nom_structure'] = df_ref['nom_structure'].fillna('').astype(str)

    # Charger le modèle pré-entraîné
    model = SentenceTransformer('models/paraphrase-MiniLM-L6-v2')

    # Obtenir les embeddings des libellés de référence
    reference_labels = df_ref['nom_structure'].tolist()

    # Always compute reference_embeddings from the current reference_labels to prevent mismatch
    reference_embeddings = model.encode(reference_labels, convert_to_tensor=True)

    # Dictionnaire pour mémoriser les rapprochements déjà calculés
    memo_similarities = {}

    # Fonction pour trouver le libellé de référence le plus similaire
    def find_most_similar(label, reference_embeddings, reference_labels):
        if label in memo_similarities:
            return memo_similarities[label]
        else:
            label_embedding = model.encode(label, convert_to_tensor=True)
            cosine_scores = util.pytorch_cos_sim(label_embedding, reference_embeddings)[0]
            top_result = torch.argmax(cosine_scores)
            result = (reference_labels[top_result], cosine_scores[top_result].item())
            memo_similarities[label] = result
            return result

    # Ajouter les colonnes N_structure et Libelle au DataFrame à traiter
    df_traiter['n_structure'] = None
    df_traiter['nom_structure'] = None

    # Rapprocher chaque libellé et mettre à jour le DataFrame
    for index, row in df_traiter.iterrows():

        label_to_match = row[colonne_analyser]

        # Simplifications et corrections des libellés
        label_to_match_rework = re.sub(r'unité locale', 'UL', str(label_to_match), flags=re.IGNORECASE)
        label_to_match_rework = re.sub(r'direction territoriale', 'DT', label_to_match_rework, flags=re.IGNORECASE)
        label_to_match_rework = re.sub(r'antenne', 'AL', label_to_match_rework, flags=re.IGNORECASE)
        label_to_match_rework = re.sub(r'unite locale', 'UL', label_to_match_rework, flags=re.IGNORECASE)

        # Trouver le libellé de référence le plus proche
        most_similar_label, score = find_most_similar(label_to_match_rework, reference_embeddings, reference_labels)
        matching_code = df_ref[df_ref['nom_structure'] == most_similar_label]['n_structure'].values[0]

        # Condition sur le score
        if score > seuil_alerte:
            if not silent:
                print(f"✅ {label_to_match} -> {most_similar_label} (Score: {score:.2f})")
            df_traiter.at[index, 'n_structure'] = matching_code
            df_traiter.at[index, 'nom_structure'] = most_similar_label
        else:
            if not silent:
                print(f"⚠️ {label_to_match} -> {most_similar_label} (Score: {score:.2f})")
            df_traiter.at[index, 'n_structure'] = ""
            df_traiter.at[index, 'nom_structure'] = ""

    return df_traiter

# Sauvegarder les données dans un sheet

def save_dataframe_to_sheet(spreadsheet_id, client, df, sheet_name=None):
    """
    Sauvegarde un DataFrame dans une feuille Google Sheets.

    Args:
        spreadsheet_id (str): L'identifiant du Google Sheets.
        client (gspread.Client): Client Google Sheets autorisé.
        df (pd.DataFrame): DataFrame Pandas à sauvegarder.
        sheet_name (str, optional): Nom de la feuille cible.
                                     Si elle n'existe pas, elle sera créée.
                                     Si None, la première feuille sera utilisée.
    """

    if df is None or df.empty:
        raise ValueError("Le DataFrame est vide ou invalide.")

    # 1️⃣ Ouvre le spreadsheet
    spreadsheet = client.open_by_key(spreadsheet_id)

    # 2️⃣ Sélectionne ou crée la feuille
    if sheet_name:
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            print(f"📄 Feuille existante '{sheet_name}' sélectionnée.")
        except Exception:
            print(f"➕ La feuille '{sheet_name}' n'existe pas. Création en cours...")
            worksheet = spreadsheet.add_worksheet(
                title=sheet_name,
                rows=str(len(df) + 100),
                cols=str(len(df.columns) + 10)
            )
            print(f"✅ Feuille '{sheet_name}' créée.")
    else:
        worksheet = spreadsheet.get_worksheet(0)
        print(f"📄 Première feuille sélectionnée : '{worksheet.title}'")

    # 3️⃣ Nettoie la feuille
    worksheet.clear()
    print(f"🗑️ Les anciennes données ont été supprimées de la feuille '{worksheet.title}'")

    # 4️⃣ Conversion en string (sécurité format)
    df_to_save = df.copy().astype(str)

    # 5️⃣ Écriture des données
    worksheet.update(
        [df_to_save.columns.values.tolist()] + df_to_save.values.tolist()
    )

    # 6️⃣ Confirmation
    print(f"💾 Données sauvegardées dans '{spreadsheet.title}' → feuille '{worksheet.title}'")
    print(f"    Nombre de lignes : {len(df_to_save)}")
    print(f"    Nombre de colonnes : {len(df_to_save.columns)}")


# Vérifications

def verifier_colonne_structure(df, col_code_structure, df_ref_structure):
    """
    Vérifie la validité d'une colonne de codes structure :
    - Présence de NaN ou de chaînes vides
    - Doublons
    - Existence dans le référentiel
    """
    print(f"\n🔎 Vérification de la colonne '{col_code_structure}'")

    # 1. Vérification des NaN ou valeurs vides
    lignes_vides = df[df[col_code_structure].isna() | (df[col_code_structure] == "")]
    if not lignes_vides.empty:
        print(f"   ❌ {len(lignes_vides)} valeur(s) manquante(s) ou vide(s) détectée(s).")
    else:
        print("   ✅ Aucun NaN ou valeur vide détecté.")

    # 2. Vérification des doublons (uniquement les codes)
    doublons_series = df[col_code_structure][df[col_code_structure].duplicated(keep=False)]
    if not doublons_series.empty:
        codes_doublons = sorted(doublons_series.value_counts().index.tolist())
        print(f"   ❌ {len(codes_doublons)} code(s) en doublon : {codes_doublons}")
    else:
        print("   ✅ Aucun doublon détecté.")

    # 3. Vérification des codes absents du référentiel
    codes_dans_df = set(df[col_code_structure].dropna().unique())
    codes_dans_ref = set(df_ref_structure[col_code_structure].dropna().unique())
    codes_manquants = codes_dans_df - codes_dans_ref

    if codes_manquants:
        print(f"   ❌ {len(codes_manquants)} code(s) non trouvés dans le référentiel : {sorted(codes_manquants)}")
    else:
        print("   ✅ Tous les codes sont présents dans le référentiel.")


def verifier_mapping(df, col_code_structure, col_libele, df_ref_structure):
    """
    Vérifie la validité d'une colonne de codes structure :
    - Présence de NaN ou de chaînes vides (affiche les libellés correspondants)
    - Doublons (affiche les codes)
    - Existence dans le référentiel (affiche les codes manquants)
    """
    print(f"\n🔎 Vérification de la colonne '{col_libele}' et mapping associé '{col_code_structure}'")

    lignes_vides = df[df[col_code_structure].isna() | (df[col_code_structure] == "")]
    if not lignes_vides.empty:
        print(f"   ❌ {len(lignes_vides)} Valeurs non mappées. Libellés associés :")
        print(sorted(lignes_vides[col_libele].dropna().unique().tolist()))
    else:
        print("   ✅ Mapping réalisé avec succès.")

# Vérification qu'on a bien la même somme entre le fichier source et le fichier de sortie

def check_sum_equal(df_left, col_left, df_right, col_right, label_left="DF1", label_right="DF2", raise_on_fail=True):
    """
    Compare la somme de df_left[col_left] et df_right[col_right].
    - Coerce en numérique (NaN -> 0)
    - Affiche OK si égal, sinon affiche l'écart et lève une erreur si raise_on_fail=True
    """
    s_left = pd.to_numeric(df_left[col_left], errors="coerce").fillna(0).sum()
    s_right = pd.to_numeric(df_right[col_right], errors="coerce").fillna(0).sum()

    if s_left != s_right:
        msg = (
            f"Incohérence ❌ : somme {label_left}[{col_left}]={s_left} "
            f"vs {label_right}[{col_right}]={s_right} (écart={s_left - s_right})"
        )
        if raise_on_fail:
            raise ValueError(msg)
        else:
            print(msg)
            return False

    print(f"OK ✅ : sommes égales ({s_left}) entre {label_left}[{col_left}] et {label_right}[{col_right}]")
    return True


def def_Structure_de_rattachement(df_ref_structure):
  rattachement_successif =   df_ref_structure[
        df_ref_structure["type_structure"].isin([ 'IMPLANTATION LOCALE HORS AL - IL'])
    ].copy()
  rattachement_successif = rattachement_successif [[
        "n_structure",
        "type_structure",
        "Structure_de_rattachement"
    ]].copy()

  rattachement_successif["N structure de rattachement"] = (
        rattachement_successif ["Structure_de_rattachement"]
        .astype("string")
        .str.split("-", n=1, expand=True)[0]
        .str.strip()
    )
  rattachement_successif .loc[rattachement_successif ["Structure_de_rattachement"].isna(), "N structure de rattachement"] = pd.NA


  return rattachement_successif

def add_num_structure_rattachement(
    df: pd.DataFrame,
    col_source: str,
    col_out: str = "N structure de rattachement"
) -> pd.DataFrame:
    """
    Crée une colonne col_out = partie avant le 1er '-' dans col_source.
    Exemple: '10 - DT DES ALPES MARITIMES' -> '10'

    - Gère NaN
    - Trim espaces
    - Ne modifie pas le df original (retourne une copie)
    """
    out = df.copy()

    out[col_out] = (
        out[col_source]
        .astype("string")
        .str.split("-", n=1, expand=True)[0]
        .str.strip()
    )

    # Optionnel : remettre <NA> si la source est vide/NA
    out.loc[out[col_source].isna(), col_out] = pd.NA

    return out

def rattache_structure(df1, df_ratt,col):
    # mapping : n_structure -> N structure de rattachement
    mapping = (
        df_ratt.set_index(df_ratt["n_structure"].astype("string"))["N structure de rattachement"]
        .astype("string")
    )

    col = col

    s = df1[col].astype("string")
    s2 = s.map(mapping)

    # si pas trouvé dans le mapping, on garde l'original
    df1[col] = s2.fillna(s)

    # optionnel : repasser en entier nullable
    df1[col] = pd.to_numeric(df1[col], errors="coerce").astype("Int64")

    return df1

    
# def apply_rattachement_successif(df_ref_structure, df, col="maraude_structure_id_fk"):
#     """
#     OBJECTIF MÉTIER
#     ----------------
#     Cette fonction permet de rattacher certaines structures opérationnelles de type Implantations locales (IL) à leur structure de référence (UL / DT), afin de garantir
#     la cohérence des indicateurs.

#     CONTEXTE
#     --------
#     Dans les données d’activité, certaines structures

#     Exemple :
#         Une "IMPLANTATION LOCALE HORS AL - IL" peut être rattachée à une "UNITE LOCALE - UL".

#     Sans ce rattachement :
#     - certaines structures ne seraient pas dans le fichier final
#     - Il manquerait des informations au niveau UL/DT

#     LOGIQUE DE TRAITEMENT
#     ---------------------
#     1. Normalisation du référentiel de structures :
#        - Extraction du code de structure à partir du champ texte "Structure_de_rattachement"
#        - Exemple : "10 - DT DES ALPES MARITIMES" → 10

#     2. Construction d’un référentiel de rattachement :
#        - Sélection des structures de type :
#          "IMPLANTATION LOCALE HORS AL - IL"
#        - Création d’un mapping :
#          n_structure → structure de rattachement

#     3. Application du rattachement :
#        - Pour chaque ligne du DataFrame métier (df_maraude) :
#            - si la structure existe dans le mapping :
#                → elle est remplacée par sa structure de rattachement
#            - sinon :
#                → elle est conservée

#     4. Contrôle qualité :
#        - Comptage du nombre de structures sans rattachement

#     NOTION DE "RATTACHEMENT SUCCESSIF"
#     ----------------------------------
#     Le terme "successif" signifie que ce mécanisme peut être appliqué en plusieurs étapes
#     pour remonter une structure vers un niveau de référence.

#     Exemple :
#         IL → UL → DT

#     Dans cette implémentation :
#         une seule étape de rattachement est réalisée.

#     ENTREES
#     -------
#     df_ref_structure : DataFrame
#         Référentiel des structures (incluant type et rattachement)

#     df : DataFrame
#         Table métier contenant les structures à rattacher

#     col : str
#         Nom de la colonne contenant l’identifiant de structure dans df_maraude

#     SORTIES
#     -------
#     df_ref_structure : DataFrame
#         Référentiel enrichi avec la colonne "N structure de rattachement"

#     c : int
#         Nombre de structures sans rattachement (indicateur de qualité)

#     rattachement_successif : DataFrame
#         Table de correspondance (structure → structure de rattachement)

#     df : DataFrame
#         Table métier avec les structures remplacées par leur structure de rattachement

#     RESUME
#     ------
#     Cette fonction garantit que les données d’activité sont rattachées à des structures
#     valides du référentiel, afin de produire des indicateurs fiables et cohérents.
#     """
#     # 1) Ajout "N structure de rattachement" dans le ref structure
#     df_ref_structure = add_num_structure_rattachement(
#         df=df_ref_structure,
#         col_source="Structure_de_rattachement",
#         col_out="N structure de rattachement"
#     )

#     # 2) Création du référentiel "rattachement successif"
#     rattachement_successif = def_Structure_de_rattachement(df_ref_structure)

#     # Vérif : nb de rattachements manquants
#     c = rattachement_successif["N structure de rattachement"].isna().sum()

#     # 3) Application du rattachement sur le df de travail
#     df = rattache_structure(df, rattachement_successif, col=col)

#     return df_ref_structure , c , rattachement_successif, df


def apply_rattachement_successif(df_ref_structure: pd.DataFrame, df: pd.DataFrame, col = 'n_structure') -> pd.DataFrame:
    """
    Remplace les IL d'un dataframe par leur structure de rattachement

    df_ref_structure doit contenir :
    - une colonne 'n_structure' (clé de correspondance)
    - une colonne 'n_structure-ratt' (nouvelle valeur)

    Retourne un nouveau dataframe.
    """

    resultat = df.copy()

    mapping = df_ref_structure.set_index("n_structure")["n_structure-ratt"]

    # Remplacement en conservant les valeurs originales si pas de correspondance
    resultat[col] = resultat[col].map(mapping).fillna(resultat[col])

    return resultat

def keep_integer(x):
  """
  En utilisant avec .apply() sur une colonne d'un dataframe,
  permet de garder uniquement la partie avec des nombres du str.
  Input doit être un str.
  """
  return re.sub("[^0-9]", "", x)
  
def dt_rattachement(df, df_ref_structure):
  """
  Permet d'associer les structures du dataframe avec la DT de rattachement, 
  utile pour le merge avec toutes les données par DT. 
  """
  df_return = pd.merge(df, df_ref_structure[['n_structure','DT_de_rattachement']], on="n_structure", how="left")
  df_return['DT_de_rattachement'] = df_return['DT_de_rattachement'].astype(str).apply(keep_integer)
  return df_return


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

  


