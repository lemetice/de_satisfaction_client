from pymongo import MongoClient
import json
import os

def insert_into_mongodb():
    client = MongoClient("mongodb://mongodb:27017/")
    db = client['trustscore']
    collection = db['commentaires']
    
    # Chemin vers le fichier JSON
    data_file = "/app/data/comments.json"

    # Charger et insérer les données
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        collection.insert_many(data)
        print("Données insérées dans MongoDB avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'insertion dans MongoDB : {e}")

if __name__ == "__main__":
    insert_into_mongodb()
