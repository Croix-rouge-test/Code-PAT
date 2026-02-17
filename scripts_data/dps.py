def clean_dps(df_conventions):
    df = df_conventions[
        [
            'DT Annuaire Opé',
            'Departement',
            'Nb de vacations de 4H effectuées PAPS',
            'Nb de vacations de 4H effectuées PE',
            'Nb de vacations de 4H effectuées ME',
            'Nb de vacations de 4H effectuées GE'
        ]
    ]

    df["Departement"] = df["Departement"].str.replace(
        r"DELEGATION DEPARTEMENTALE|DELEGATION TERRITORIALE",
        "DT",
        regex=True
    )

    df = df.rename(columns={'Code structure': 'n_structure'})

    return df




def indicateurs_dps(df_dps, df_ref_structure):
    df = df_dps[
        ["Departement", 'Nb de vacations de 4H effectuées PAPS',
            'Nb de vacations de 4H effectuées PE',
            'Nb de vacations de 4H effectuées ME',
            'Nb de vacations de 4H effectuées GE'
]
    ].copy()

    df = rapprochement_libelles(
        df_ref_structure,
        df,
        "Departement"
    )

    df = df.rename(
        columns={
            "Nb de vacations de 4H effectuées PAPS": "Secours Nb_PAPS_2025",
	    "Nb de vacations de 4H effectuées PE": "Secours Nb_DPS_PE_2025",
	    "Nb de vacations de 4H effectuées ME": "Secours Nb_DPS_ME_2025",
	    "Nb de vacations de 4H effectuées GE": "Secours Nb_DPS_GE_2025"
        }
    )

    df['Secours Nb_DPS_2025'] = df['Nb de vacations de 4H effectuées PAPS', 'Nb de vacations de 4H effectuées PE', 'Nb de vacations de 4H effectuées ME', 'Nb de vacations de 4H effectuées GE'].sum(axis=1)

    return df