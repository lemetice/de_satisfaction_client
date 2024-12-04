import pandas as pd
from sqlalchemy import create_engine

def insert_into_postgres():
    # Configurer la connexion PostgreSQL
    engine = create_engine("postgresql://myuser:mypassword@postgres:5432/trustscore")
    
    # Chemin vers le fichier CSV
    data_file = "/app/data/informations_entreprises.csv"

    # Charger les données
    try:
        df = pd.read_csv(data_file)
        df.to_sql('companies', engine, if_exists='append', index=False)
        print("Données insérées dans PostgreSQL avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'insertion dans PostgreSQL : {e}")

if __name__ == "__main__":
    insert_into_postgres()
