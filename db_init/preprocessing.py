import pandas as pd

# Charger le fichier source
input_file = "informations_entreprises.csv"
output_file = "data.csv"

try:
    # Charger les données
    df = pd.read_csv(input_file)
    
    # Liste des colonnes à vérifier et nettoyer
    required_columns = ['five_star_%', 'town', 'country', 'institution_type', 
                        'company_name', 'trust_score', 'review']
    
    # Vérifier que toutes les colonnes nécessaires sont présentes
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f"Les colonnes suivantes sont absentes : {', '.join(missing_columns)}")
    
    # Nettoyer les valeurs manquantes et les formats de colonnes
    if 'five_star_%' in df.columns:
        df['five_star_%'] = df['five_star_%'].fillna('0%')  # Remplace NaN par '0%'
        df['five_star_percentage'] = pd.to_numeric(
            df['five_star_%'].str.rstrip('%'),
            errors='coerce'
        ).fillna(0)  # Convertit les erreurs en 0
        df.drop(columns=['five_star_%'], inplace=True)  # Supprimer la colonne originale

    # Remplir les valeurs manquantes pour les colonnes texte
    #for col in ['town', 'country', 'institution_type', 'company_name']:
    for col in ['town']:
        if col in df.columns:
            df[col] = df[col].fillna('Other town')  # Remplace les NaN par 'NA' (not available)

    # Traiter les valeurs numériques pour 'trust_score' et 'review'
    if 'trust_score' in df.columns:
        df['trust_score'] = pd.to_numeric(df['trust_score'], errors='coerce').fillna(0)
    if 'review' in df.columns:
        df['review'] = pd.to_numeric(df['review'], errors='coerce').fillna(0).astype(int)

    # Sauvegarder dans un nouveau fichier ou écraser l'existant
    df.to_csv(output_file, index=False)
    
    print(f"Fichier traité et sauvegardé dans : {output_file}")

except FileNotFoundError:
    print(f"Erreur : Le fichier {input_file} est introuvable.")
except KeyError as e:
    print(f"Erreur : {str(e)}")
except Exception as e:
    print(f"Une erreur inattendue s'est produite : {str(e)}")
