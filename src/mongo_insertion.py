from pymongo import MongoClient
import json

def connect_to_mongodb(mongo_uri='mongodb://localhost:27017/'):
    """
    Crée une connexion à MongoDB.

    Paramètres:
    - mongo_uri (str): L'URI de connexion à MongoDB.

    Retourne:
    - client (MongoClient): Le client MongoDB.
    """
    return MongoClient(mongo_uri)

def insert_data_from_json_to_mongodb(json_file_path, db_name='trustscore', collection_name='commentaires', mongo_uri='mongodb://localhost:27017/'):
    """
    Lit les données d'un fichier JSON et les insère dans une collection MongoDB.

    Paramètres:
    - json_file_path (str): Le chemin du fichier JSON contenant les données.
    - db_name (str): Le nom de la base de données.
    - collection_name (str): Le nom de la collection.
    - mongo_uri (str): L'URI de connexion à MongoDB.

    Retourne:
    - result (InsertManyResult): Le résultat de l'insertion.
    """
    try:
        # Connexion à MongoDB
        client = connect_to_mongodb(mongo_uri)

        # Sélection de la base de données et de la collection
        db = client[db_name]
        collection = db[collection_name]

        # Lecture des données du fichier JSON
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Insertion des données
        if isinstance(data, list):
            # Insérer plusieurs documents
            result = collection.insert_many(data)
            print(f"{len(result.inserted_ids)} documents ont été insérés.")
        else:
            # Insérer un seul document
            result = collection.insert_one(data)
            print(f"Document inséré avec l'ID : {result.inserted_id}")

        return result

    except Exception as e:
        print(f"Erreur lors de l'insertion : {e}")

    finally:
        # Fermer la connexion
        client.close()
