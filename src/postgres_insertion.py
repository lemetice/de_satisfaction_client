import psycopg2
import pandas as pd

def insert_companies_to_postgres(csv_file_path, db_config):
    """
    Vide la table companies puis insère les données d'un fichier CSV dans PostgreSQL.
    
    :param csv_file_path: Chemin vers le fichier CSV contenant les données à insérer.
    :param db_config: Dictionnaire contenant les informations de connexion à PostgreSQL.
    """
    
    try:
        # Connexion à PostgreSQL
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()

        # Vider la table 'companies'
        cursor.execute("TRUNCATE TABLE companies;")
        print("Table 'companies' vidée avec succès.")

        # Lire le fichier CSV avec pandas
        df = pd.read_csv(csv_file_path)

        # Nettoyer les données - convertir 'five_star_%' en décimal (ex : de '96%' à 96.00)
        df['five_star_percentage'] = df['five_star_%'].str.replace('%', '').astype(float)

        # Insérer les données dans PostgreSQL
        for index, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO companies (town, country, institution_type, company_name, trust_score, review, five_star_percentage)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (row['town'], row['country'], row['institution_type'], row['company_name'], row['trust_score'], row['review'], row['five_star_percentage'])
            )

        # Commit les changements
        conn.commit()
        print("Données insérées avec succès dans la table 'companies'.")

    except psycopg2.Error as e:
        print(f"Erreur PostgreSQL : {e.pgcode}, {e.pgerror}")
    except Exception as e:
        print(f"Erreur générale : {e}")
    finally:
        # Fermer la connexion
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    # Configuration de la base de données
    db_config = {
        'host': 'localhost',     # Remplace par ton hôte (par ex. 'postgres' si Docker Compose)
        'port': '5432',          # Port par défaut pour PostgreSQL
        'database': 'trustscore_db',
        'user': 'myuser',
        'password': 'mypassword'
    }

    # Chemin vers ton fichier CSV
    csv_file_path = r'..\data\informations_entreprises.csv'

    # Appeler la fonction pour insérer les données
    insert_companies_to_postgres(csv_file_path, db_config)

