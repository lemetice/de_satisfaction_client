import pandas as pd
def process_and_join_data(df_entreprises, df_details):
    df_final = pd.merge(
        df_entreprises,
        df_details[['Commentaire', 'five_star_percentage']],
        left_on='company_name',
        right_on='Commentaire',
        how='left'
    )
    df_final.drop(columns=['Commentaire'], inplace=True)
    return df_final


import pandas as pd

def process_enterprise_data(input_file, output_file=None):
    """
    Prétraiter les données d'entreprises avant insertion dans PostgreSQL.

    Arguments :
    - input_file : Chemin vers le fichier CSV d'entrée.
    - output_file : Chemin vers le fichier CSV de sortie (optionnel).

    Retourne :
    - DataFrame traité.
    """
    try:
        # Charger les données
        df = pd.read_csv(input_file)
        
        # Renommer la colonne `five_Star_Percentage` en `five_star_%` si elle existe
        if 'five_star_percentage' in df.columns:
            df.rename(columns={'five_star_percentage': 'five_star_%'}, inplace=True)

        # Liste des colonnes à vérifier et nettoyer
        required_columns = ['five_star_%', 'town', 'country', 'institution_type', 
                            'company_name', 'trust_score', 'review']
        
        # Vérifier que toutes les colonnes nécessaires sont présentes
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise KeyError(f"Les colonnes suivantes sont absentes : {', '.join(missing_columns)}")
        
        # Remplir les valeurs manquantes pour les colonnes texte
        for col in ['town', 'country', 'institution_type', 'company_name']:
            if col in df.columns:
                df[col] = df[col].fillna('Unknown')  # Remplace les NaN par 'Unknown'

        # Traiter les valeurs numériques pour 'trust_score' et 'review'
        if 'trust_score' in df.columns:
            df['trust_score'] = pd.to_numeric(df['trust_score'], errors='coerce').fillna(0)
        if 'review' in df.columns:
            df['review'] = pd.to_numeric(df['review'], errors='coerce').fillna(0).astype(int)

        # Sauvegarder dans un fichier CSV si un chemin est fourni
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"Fichier traité et sauvegardé dans : {output_file}")

        return df

    except FileNotFoundError:
        print(f"Erreur : Le fichier {input_file} est introuvable.")
        return None
    except KeyError as e:
        print(f"Erreur : {str(e)}")
        return None
    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {str(e)}")
        return None

