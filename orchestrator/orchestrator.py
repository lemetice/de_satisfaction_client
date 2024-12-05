from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

# Fonction pour exécuter un script via subprocess
def execute_script(command, description):
    try:
        print(f"Démarrage de {description}...")
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{description} terminé avec succès.")
            return {"success": True, "message": f"{description} terminé avec succès."}
        else:
            print(f"Erreur lors de {description} : {result.stderr}")
            return {"success": False, "message": f"Erreur : {result.stderr}"}
    except Exception as e:
        print(f"Erreur lors de {description} : {e}")
        return {"success": False, "message": f"Exception : {str(e)}"}

# Routes de l'API Flask
@app.route('/refresh-data', methods=['GET'])
def refresh_data():
    try:
        # Étape 1 : Scraping
        scraping_result = execute_script(
            ["python3", "/app/scrapping_app/scrape.py"],
            "scraping"
        )

        # Étape 2 : Préprocessing
        preprocessing_result = execute_script(
            ["python3", "/app/preprocessing_service/preprocess_data.py"],
            "préprocessing"
        )

        # Étape 3 : Insertion dans PostgreSQL
        postgres_result = execute_script(
            ["python3", "/app/scrapper_to_postgres.py"],
            "insertion dans PostgreSQL"
        )

        # Étape 4 : Insertion dans MongoDB
        mongo_result = execute_script(
            ["python3", "/app/scrapper_to_mongo.py"],
            "insertion dans MongoDB"
        )

        # Résumé des étapes
        results = {
            "scraping": scraping_result,
            "preprocessing": preprocessing_result,
            "postgres_insertion": postgres_result,
            "mongo_insertion": mongo_result,
        }

        # Vérification des échecs
        if all(step["success"] for step in results.values()):
            return jsonify({"success": True, "message": "Données rafraîchies avec succès.", "details": results}), 200
        else:
            return jsonify({"success": False, "message": "Certaines étapes ont échoué.", "details": results}), 500
    except Exception as e:
        return jsonify({"success": False, "message": f"Erreur générale : {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
