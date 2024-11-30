from pymongo import MongoClient
import json

def insert_into_mongodb(json_file, mongo_url="mongodb://mongodb:27017/", db_name="trustscore", collection_name="comments"):
    """
    Insère des données depuis un fichier JSON dans MongoDB.

    Args:
    - json_file (str): Chemin vers le fichier JSON à insérer.
    - mongo_url (str): URL de connexion à MongoDB.
    - db_name (str): Nom de la base de données.
    - collection_name (str): Nom de la collection.

    Retourne:
    - None
    """
    try:
        # Connexion au client MongoDB
        client = MongoClient(mongo_url)
        db = client[db_name]
        collection = db[collection_name]

        # Charger les données JSON
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Insérer les données dans la collection
        collection.insert_many(data)
        print(f"Data from {json_file} inserted into MongoDB collection '{collection_name}' successfully!")

    except Exception as e:
        print(f"An error occurred while inserting into MongoDB: {e}")

    finally:
        client.close()
