import pandas as pd
import os
from mongo_insertion import insert_data_from_json_to_mongodb
from sql_lite_insertion import insert_companies_and_reviews
from preprocessing import company_preprocessing

def run_data_pipeline(csv_file_path, json_file_path):
    """
    Exécute le pipeline de données pour insérer des données dans MongoDB et SQLite.

    Paramètres:
    - csv_file_path (str): Le chemin du fichier CSV contenant les données des entreprises et des reviews.
    - json_file_path (str): Le chemin du fichier JSON contenant les commentaires pour MongoDB.
    
    Retourne:
    - None
    """
    try:
        # Étape 0 : Scraper les données depuis Trustpilot
        # print("Scraping des données depuis Trustpilot...")
        # scrape_trustpilot()  # Appel de la fonction de scraping si nécessaire

        # Étape 1 : Lire les données du CSV
        print("Lecture des données CSV...")
        df = pd.read_csv(csv_file_path)

        # Étape 2 : Preprocessing des données
        print("Preprocessing des données...")
        df = company_preprocessing(df)  # Appel de la fonction de preprocessing pour nettoyer et transformer les données

        # Vérification des types de données après preprocessing
        print("Types de données après preprocessing :")
        print(df.dtypes)

        # Étape 3 : Insertion des données dans SQLite
        print("Insertion des données dans SQLite...")
        insert_companies_and_reviews(df)

        # Étape 4 : Insertion des données dans MongoDB
        print("Insertion des données dans MongoDB...")
        insert_data_from_json_to_mongodb(json_file_path)

        print("Pipeline d'insertion terminé avec succès.")

    except Exception as e:
        print(f"Erreur dans le pipeline : {e}")

# Exemple d'utilisation
if __name__ == "__main__":
    # Récupérer les chemins des fichiers CSV et JSON dans le dossier parent 'data'
    base_path = '../data'
    csv_file_path = os.path.join(base_path, 'informations_entreprises.csv')
    json_file_path = os.path.join(base_path, 'df_commentaires_par_entreprise.json')

    # Exécuter le pipeline
    run_data_pipeline(csv_file_path, json_file_path)
