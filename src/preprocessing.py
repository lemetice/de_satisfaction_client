from sklearn.impute import SimpleImputer
import numpy as np
import pandas as pd

def company_preprocessing(df):
    """
    Prétraite les données des entreprises avant l'insertion.
    
    Paramètres:
    - df (DataFrame): Le DataFrame contenant les données brutes.

    Retourne:
    - df (DataFrame): Le DataFrame nettoyé et prétraité.
    """
    # Renommer les colonnes
    df.rename(columns={"review": "nombre_reviews"}, inplace=True)

    # Supprimer les espaces blancs et normaliser les valeurs
    df['town'] = df['town'].astype(str).str.strip().str.upper().replace('nan', 'NaN')
    df['country'] = df['country'].astype(str).str.strip().replace('nan', 'NaN')
    df['institution_type'] = df['institution_type'].astype(str).str.strip().replace('nan', 'NaN')

    # Remplacer les valeurs NaN avec les valeurs les plus fréquentes
    imputer = SimpleImputer(missing_values='NaN', strategy='most_frequent')
    df[['town', 'country', 'institution_type']] = imputer.fit_transform(df[['town', 'country', 'institution_type']])

    # Convertir les colonnes numériques et gérer les valeurs NaN
    df['trust_score'] = pd.to_numeric(df['trust_score'], errors='coerce').fillna(0)
    df['five_star_%'] = df['five_star_%'].astype(str).replace('nan', '0').str.rstrip('%').astype(float) / 100
    df['nombre_reviews'] = pd.to_numeric(df['nombre_reviews'], errors='coerce').fillna(0)

    # Raccourcir le nom des entreprises
    df['short_company_name'] = df['company_name']
    df['company_name'] = df['short_company_name'].apply(lambda x: str(x).strip()[:7] + "...")

    return df
