import psycopg2
from psycopg2 import sql

def insert_into_postgres(postgres_uri, table_name, data):
    """
    Insère les données des entreprises dans PostgreSQL.

    Arguments :
    - postgres_uri : URI de connexion PostgreSQL.
    - table_name : Nom de la table dans laquelle insérer les données.
    - data : Liste de dictionnaires contenant les données des entreprises.
    """
    try:
        # Connexion à la base de données PostgreSQL
        conn = psycopg2.connect(postgres_uri)
        cursor = conn.cursor()

        # Préparer la requête d'insertion
        columns = data[0].keys()
        insert_query = sql.SQL("""
            INSERT INTO {table} ({fields})
            VALUES ({values})
            ON CONFLICT DO NOTHING
        """).format(
            table=sql.Identifier(table_name),
            fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
            values=sql.SQL(', ').join(sql.Placeholder() * len(columns))
        )

        # Insérer les données
        for record in data:
            cursor.execute(insert_query, tuple(record.values()))

        conn.commit()
        print(f"{cursor.rowcount} entreprises insérées dans PostgreSQL.")

    except Exception as e:
        print(f"Erreur lors de l'insertion dans PostgreSQL : {e}")

    finally:
        if conn:
            cursor.close()
            conn.close()
