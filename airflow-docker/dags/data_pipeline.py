import os 
import datetime
import pendulum
import time
import pandas as pd
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from psycopg2 import OperationalError, connect
from airflow.hooks.postgres_hook import PostgresHook
from src.mongo_insertion import insert_data_from_json_to_mongodb
from src.sql_lite_insertion import insert_companies_and_reviews
from src.scrapping import scrape_trustpilot
from src.preprocessing import company_preprocessing

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
        print("Scraping des données depuis Trustpilot...")
        scrape_trustpilot()  # Appel de la fonction de scraping si nécessaire

        # Étape 1 : Lire les données du CSV
        print("Lecture des données CSV...")
        df = pd.read_csv(csv_file_path)

        # Étape 2 : Preprocessing des données
        print("Preprocessing des données...")
        df = company_preprocessing(df)  

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
"""
if __name__ == "__main__":
    # Récupérer les chemins des fichiers CSV et JSON dans le dossier parent 'data'
    base_path = '../data'
    csv_file_path = os.path.join(base_path, 'informations_entreprises.csv')
    json_file_path = os.path.join(base_path, 'df_commentaires_par_entreprise.json')

    # Exécuter le pipeline
    run_data_pipeline(csv_file_path, json_file_path)
"""

# Définition du DAG
with DAG(
    dag_id="daily_stock_data_pipeline",
    schedule_interval="@daily",
    start_date=pendulum.datetime(2023, 10, 29, tz="UTC"),
    catchup=False,
) as dag:

    start_task = EmptyOperator(task_id="start")

    
    extract_transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=test_connection,
        # python_callable=extract_transform_data,
    )

    load_task = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
        provide_context=True,
    )

    end_task = EmptyOperator(task_id="end")
    start_task >> extract_transform_task >> load_task >> end_task
