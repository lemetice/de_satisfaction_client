from pymongo import MongoClient, errors
import json
import hashlib

def generate_unique_id(comment):
    """Génère un ID unique basé sur le commentaire."""
    comment_string = json.dumps(comment, sort_keys=True)
    return hashlib.md5(comment_string.encode('utf-8')).hexdigest()

def insert_into_mongodb():
    client = MongoClient("mongodb://mongodb:27017/")
    db = client['trustscore']
    collection = db['commentaires']
    
    # Chemin vers le fichier JSON
    data_file = "/app/data/comments.json"

    try:
        # Charger les données
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Ajouter un champ _id unique pour éviter les doublons
        for comment in data:
            comment["_id"] = generate_unique_id(comment)
        
        # Insérer les données tout en ignorant les doublons
        collection.insert_many(data, ordered=False)
        print("Données insérées dans MongoDB avec succès.")
    except errors.BulkWriteError as bwe:
        print("Certains documents sont déjà dans la base. Les doublons ont été ignorés.")
    except Exception as e:
        print(f"Erreur lors de l'insertion dans MongoDB : {e}")

if __name__ == "__main__":
    insert_into_mongodb()
