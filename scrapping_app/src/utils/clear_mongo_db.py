from pymongo import MongoClient

def clear_mongo_collection_batch():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client['trustscore']
        collection = db['commentaires']
        
        # Supprimer par lot (1000 documents à la fois)
        batch_size = 1000
        while collection.count_documents({}) > 0:
            result = collection.delete_many({}, limit=batch_size)
            print(f"{result.deleted_count} documents supprimés.")
        
        print("Tous les documents ont été supprimés.")
        
    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        client.close()

clear_mongo_collection_batch()
