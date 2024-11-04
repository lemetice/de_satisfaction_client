from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from config import POSTGRES_URI, MONGO_URI

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Connexion à PostgreSQL
db = SQLAlchemy(app)

# Connexion à MongoDB
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client['your_mongo_db']


@app.route('/', methods=['GET'])
def api_check():
    """Vérifie si l'API est en ligne."""
    return jsonify({"status": "Welcome to our API -->"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Vérifie si l'API est en ligne."""
    return jsonify({"status": "API is running"}), 200

@app.route('/company_data', methods=['GET'])
def get_postgres_data():
    """Récupère toutes les données de PostgreSQL avec une requête brute."""
    try:
        # Exécuter la requête SQL brute
        result = db.engine.execute("SELECT * FROM Companies")
        user_list = [dict(row) for row in result]
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mongo_data', methods=['GET'])
def get_all_mongo_data():
    """Récupère toutes les données de la collection 'users'."""
    try:
        mongo_users = mongo_db.users.find()
        user_list = [{"_id": str(user["_id"]), "name": user.get("name"), "email": user.get("email")} for user in mongo_users]
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
