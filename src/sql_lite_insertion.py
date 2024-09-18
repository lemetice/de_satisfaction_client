import sqlite3
import pandas as pd

def insert_companies_and_reviews(df, db_path='../src/trustscore.db'):
    """
    Insère les données d'entreprises et de reviews dans les tables appropriées.

    Paramètres:
    - df (DataFrame): Le DataFrame prétraité contenant les données des entreprises et des reviews.
    - db_path (str): Le chemin de la base de données SQLite.

    Retourne:
    - None
    """
    try:
        # Connexion à la base de données SQLite
        conn = sqlite3.connect(db_path)

        # Convertir la colonne en string avant manipulation
        if 'five_star_%' in df.columns:
            # Conversion sécurisée en chaîne de caractères
            df['five_star_%'] = df['five_star_%'].astype(str)  # Convertir en chaîne pour éviter l'erreur .str

            # Manipuler les valeurs pour enlever le % et diviser par 100
            #df['five_star_percentage'] = df['five_star_%'].str.rstrip('%').replace('nan', '0').astype(float) / 100
            df['five_star_percentage'] = df['five_star_%'].str.rstrip('%').replace('nan', '0').astype(float)

            # Supprimer la colonne originale 'five_star_%' après conversion
            df.drop(columns=['five_star_%'], inplace=True)

        # Vérifier le DataFrame avant insertion
        print("Données avant insertion :")
        print(df.head())
        print(df.dtypes)

        # Insertion des données dans la table `companies_infos`
        df.to_sql('companies_infos', conn, if_exists='append', index=False)

        print("Insertion des données terminée avec succès.")

    except Exception as e:
        print(f"Erreur lors de l'insertion des données : {e}")

    finally:
        # Fermer la connexion
        conn.close()
