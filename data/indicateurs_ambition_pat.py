import pandas as pd
from gspread_dataframe import get_as_dataframe


def charger_indicateurs_ambition_pat(df_indic_ambition, df_ref_structure):
    colonnes_a_conserver = [
        "DT",
        "% Completion PAT",
        "% de nouveaux volontaires formés à CRB*",
        #"Affichage 7 principes dans 100% des structures*",
        #"Affichage affiche Mouvement semestrielle dans 100% structures*",
        #"Emblème CRF en devanture \ndans 100% des structures*",
        #"Nb d’ateliers “7 principes” réalisés dans les structures locales*",
        "La déclinaison de la convention nationale a été signée avec les préfectures*",
        "Nb de conventions avec des opérateurs privés \n*",
        "Nb de conventions avec des opérateurs publics*",
        "Astreinte territoriale joignable 24/24*",
        "CAI en condition opérationnelle +  CHU pour 50 personnes*",
        "Nombre de lots CAI*",
        " Nombre de lots CHU*",
        "Nombre de lots Coup de main Coup de coeur*",
        "Nombre d’exercices de crise*",
        "Existence d’un Pôle Santé Territoriale (PST) ?*",
        "Au moins 20% des nv volontaires CRf sont formés au TCAU +  PSP chaque année*",
        "% des volontaires formés au TCAU*",
        "% des volontaires formés au PSP*",
        "% des volontaires formés au GQS*",
        "Nb personnes formées au PSC ",
        "Nb de formateurs FPSC ",
        "Nb d’animateurs AGQS ",
        "Nb de sessions PSC réalisées ",
        "Nb de sessions GQS réalisées",
        "Nb de sessions IPS réalisées",
        "Nb de sessions IPSEN réalisées",
        "Nb de sessions PREVIC réalisées",
        "Nb d’OCR déployées*",
        "Nb de maraudes réalisées*",
        "Nb volontaires formés à SOLIDAR2020*",
        "Nb d’intervenants secouristes*",
        "Nb DPS équivalent poste de secours*",
        "Produit financier associé au DPS*",
        "Nb d'AEO fixe*",
        "Nb d'AEO mobile*"
    ]

    df_indic_ambition = df_indic_ambition[colonnes_a_conserver].copy()
    df_indic_ambition

    # Cleaning de la table
    colonnes_oui_non = [
        "Affichage 7 principes dans 100% des structures*",
        "Affichage affiche Mouvement semestrielle dans 100% structures*",
        "Emblème CRF en devanture \ndans 100% des structures*",
        "La déclinaison de la convention nationale a été signée avec les préfectures*",
        "Astreinte territoriale joignable 24/24*",
        "CAI en condition opérationnelle +  CHU pour 50 personnes*",
        "Existence d’un Pôle Santé Territoriale (PST) ?*",
        "Au moins 20% des nv volontaires CRf sont formés au TCAU +  PSP chaque année*",
    ]

    colonnes_pourcentage = [
        "% de nouveaux volontaires formés à CRB*",
        "% des volontaires formés au TCAU*",
        "% des volontaires formés au PSP*",
        "% des volontaires formés au GQS*",
    ]

    colonnes_nombre = [
        "Nb d’ateliers “7 principes” réalisés dans les structures locales*",
        "Nb de conventions avec des opérateurs privés \n*",
        "Nb de conventions avec des opérateurs publics*",
        "Nombre de lots CAI*",
        " Nombre de lots CHU*",
        "Nombre de lots Coup de main Coup de coeur*",
        "Nombre d’exercices de crise*",
        "Nb personnes formées au PSC ",
        "Nb de formateurs FPSC ",
        "Nb d’animateurs AGQS ",
        "Nb de sessions PSC réalisées ",
        "Nb de sessions GQS réalisées",
        "Nb de sessions IPS réalisées",
        "Nb de sessions IPSEN réalisées",
        "Nb de sessions PREVIC réalisées",
        "Nb d’OCR déployées*",
        "Nb de maraudes réalisées*",
        "Nb volontaires formés à SOLIDAR2020*",
        "Nb d’intervenants secouristes*",
        "Nb DPS équivalent poste de secours*",
        "Produit financier associé au DPS*",
        "Nb dAEO fixe*",
        "Nb dAEO mobile*",
    ]
    df_clean = df_indic_ambition.copy()
    # 1. Colonnes Oui / Non
    for col in colonnes_oui_non:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip()
            df_clean[col] = df_clean[col].where(
                df_clean[col].isin(["Oui", "Non"]),
                pd.NA
            )
    # 2. Colonnes Nombre
    for col in colonnes_nombre:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
    # 3. Colonnes Pourcentage
    # On garde uniquement les valeurs numériques entre 0 et 1
    # Exemple : 0.5, 0.9, 1.0
    for col in colonnes_pourcentage:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
            df_clean[col] = df_clean[col].where(
                (df_clean[col] >= 0) & (df_clean[col] <= 1),
                pd.NA
            )
    df_indic_ambition = df_clean.copy()

    # création des indicateurs
    df_indic_ambition

    # Rename colonne
    rename_indicateurs = {
        "% de nouveaux volontaires formés à CRB*": "PAT Taux_nvx_formes_CRB",
        "La déclinaison de la convention nationale a été signée avec les préfectures*": "PAT conv_pref",
        "Nb de conventions avec des opérateurs privés \n*": "PAT conv_prive",
        "Nb de conventions avec des opérateurs publics*": "PAT conv_public",
        "Astreinte territoriale joignable 24/24*": "PAT astreinte",
        "CAI en condition opérationnelle +  CHU pour 50 personnes*": "PAT CAI_CHU",
        "Nombre de lots CAI*": "PAT CAI",
        " Nombre de lots CHU*": "PAT CHU",
        "Nombre de lots Coup de main Coup de coeur*": "PAT coup_coeur",
        "Nombre d’exercices de crise*": "PAT Dispos_urgence_nb_exercices",
        "Existence d’un Pôle Santé Territoriale (PST) ?*": "PAT Dispos_urgence_PST",
        "Au moins 20% des nv volontaires CRf sont formés au TCAU +  PSP chaque année*": "PAT %_TCAU_PSP",
        "% des volontaires formés au TCAU*": "PAT Dispos_urgence_tauxformation_TCAU",
        "% des volontaires formés au PSP*": "PAT Dispos_urgence_tauxformation_PSP",
        "% des volontaires formés au GQS*": "PAT Dispos_urgence_tauxformation_GQS",
        "Nb personnes formées au PSC ": "PAT FGP_Nb_formes_PSC",
        "Nb de formateurs FPSC ": "PAT FGP_Nb_FPSC",
        "Nb d’animateurs AGQS ": "PAT FGP_Nb_AGQS",
        "Nb de sessions PSC réalisées ": "PAT FGP_Nb_sessions_PSC",
        "Nb de sessions GQS réalisées": "PAT FGP_Nb_sessions_GQS",
        "Nb de sessions IPS réalisées": "PAT FGP_Nb_sessions_IPS",
        "Nb de sessions IPSEN réalisées": "PAT FGP_Nb_sessions_IPSEN",
        "Nb de sessions PREVIC réalisées": "PAT FGP_Nb_sessions_PREVIC",
        "Nb d’OCR déployées*": "PAT OCR_Nb_OCR",
        "Nb de maraudes réalisées*": "PAT Maraudes_Nb_maraudes",
        "Nb volontaires formés à SOLIDAR2020*": "PAT Maraudes_Formes_SOLIDAR2020",
        "Nb d’intervenants secouristes*": "PAT DPS_Nb_IS",
        "Nb DPS équivalent poste de secours*": "PAT DPS_Nb_DPS",
        "Produit financier associé au DPS*": "PAT DPS_CA",
        "Nb d'AEO fixe*": "PAT AEO_Nb_aeo_fixe",
        "Nb d'AEO mobile*": "PAT AEO_Nb_aeo_mobile"
    }
    df_indic_ambition = df_indic_ambition.rename(columns=rename_indicateurs)
    df_indic_ambition["PAT conv_total"] = df_indic_ambition[["PAT conv_prive", "PAT conv_public"]].sum(axis=1, skipna=True)

    # ajout de N structure


    df_ref_structure['n_structure'] = df_ref_structure['n_structure'].astype(int)
    df_DT_ref_structure = df_ref_structure[df_ref_structure["type_structure"].isin(["DELEGATION TERRITORIALE - DT"])]
    df_DT_ref_structure = df_DT_ref_structure[
        ["n_structure", "n_dept"]
    ].copy()
    # df_indic_ambition["DT"] = df_indic_ambition["DT"].replace({
    #     "986-1": "986",
    #     "986-2": "986"
    # })
    df_DT_ref_structure.loc[df_DT_ref_structure['n_structure'] == 4303, 'n_dept'] = '986-1'
    df_DT_ref_structure.loc[df_DT_ref_structure['n_structure'] == 3884, 'n_dept'] = '986-2'
    df_indic_ambition = pd.merge(df_DT_ref_structure, df_indic_ambition, left_on="n_dept", right_on="DT", how="outer")

    df_indic_ambition.loc[df_indic_ambition['n_structure'] == 4303, 'n_dept'] = '986'
    df_indic_ambition.loc[df_indic_ambition['n_structure'] == 3884, 'n_dept'] = '986'
    return df_indic_ambition
