
# **Satisfaction Client - Dashboard d'Analyse des Sentiments**

Ce projet vise à créer un tableau de bord d'analyse des sentiments basé sur les commentaires des clients récupérés depuis des sources externes. Il utilise une architecture basée sur des microservices, avec une automatisation complète des processus de scraping, de prétraitement, d'insertion dans des bases de données et d'affichage des résultats via un tableau de bord interactif.

---

## **Fonctionnalités**

1. **Scraping des données** : Extraction des commentaires des clients et des informations des entreprises depuis des sources externes.
2. **Prétraitement des données** : Nettoyage, analyse des sentiments et enrichissement des données brutes.
3. **Stockage** : 
   - MongoDB pour les commentaires clients.
   - PostgreSQL pour les informations des entreprises.
4. **Automatisation** : 
   - Automatisation des processus via des tâches planifiées avec `cron`.
   - Rafraîchissement manuel des données via le tableau de bord.
5. **Visualisation** :
   - Histogrammes d'analyse des sentiments par année et par entreprise.
   - Diagrammes circulaires et barres pour les scores de confiance et les distributions d'institutions.

---

## **Technologies Utilisées**

- **Langages** : Python
- **Bases de données** :
  - MongoDB pour les commentaires
  - PostgreSQL pour les entreprises
- **Frameworks** :
  - Flask pour l'API backend
  - Dash pour le tableau de bord
- **Outils** :
  - Docker pour la conteneurisation
  - `cron` pour l'automatisation des tâches

---

## **Architecture**

### **Microservices**
1. **`scrapping_app`** : Service pour extraire les données depuis les sources externes.
2. **`preprocessing_service`** : Service pour nettoyer et analyser les données.
3. **`scrapper_to_postgres`** : Service pour insérer les données dans PostgreSQL.
4. **`scrapper_to_mongo`** : Service pour insérer les données dans MongoDB.
5. **`flask_api`** : API REST pour servir les données au tableau de bord.
6. **`dash_app`** : Tableau de bord interactif pour visualiser les résultats.

### **Automatisation**
- Un service central **`orchestrator`** exécute les étapes suivantes dans l'ordre :
  1. Scraping des données.
  2. Prétraitement des données.
  3. Insertion dans PostgreSQL et MongoDB.
  4. Rafraîchissement des données disponibles dans l'API.

### **Flux de Données**
1. **Scraping** → Fichiers JSON/CSV
2. **Prétraitement** → Données nettoyées/enrichies
3. **Insertion** → Bases de données (MongoDB/PostgreSQL)
4. **Visualisation** → Tableau de bord Dash

---

## **Installation**

### **Prérequis**
1. **Docker** et **Docker Compose** installés.
2. Port `5432` disponible pour PostgreSQL, `27017` pour MongoDB et `8050` pour Dash.

### **Étapes**
1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/lemetice/de_satisfaction_client.git
   cd de_satisfaction_client
   git checkout pipeline
   ```

2. **Configurer les variables d'environnement** :
   - Créez un fichier `.env` à la racine avec les informations nécessaires :
     ```
     POSTGRES_USER=myuser
     POSTGRES_PASSWORD=mypassword
     POSTGRES_DB=trustscore
     MONGO_URI=mongodb://mongodb:27017
     ```

3. **Lancer les services avec Docker Compose** :
   ```bash
   docker-compose up --build
   ```

4. Accéder aux services :
   - **Tableau de bord Dash** : [http://localhost:8050](http://localhost:8050)
   - **API Flask** : [http://localhost:5000/api](http://localhost:5000/api)

---

## **Utilisation**

### **Tableau de Bord**
1. **Affichage des données** :
   - Voir les scores de confiance par entreprise.
   - Analyser les sentiments des commentaires par année et par entreprise.
2. **Rafraîchir les données** :
   - Cliquez sur le bouton "Rafraîchir les données" pour relancer le pipeline (scraping, prétraitement, insertion).

### **API Endpoints**
- **GET /api/companies** : Retourne les informations des entreprises.
- **GET /api/comments** : Retourne les commentaires clients.

### **Automatisation**
- Une tâche planifiée avec `cron` exécute automatiquement le pipeline toutes les heures. Le fichier `my_cron` gère cette planification.

---

## **Structure du Projet**

```
de_satisfaction_client/
├── scrapping_app/
│   ├── scrape.py         # Script de scraping des données
│   └── Dockerfile        # Dockerfile pour le service de scraping
├── preprocessing_service/
│   ├── preprocess_data.py  # Script de prétraitement des données
│   └── Dockerfile          # Dockerfile pour le service de prétraitement
├── scrapper_to_postgres.py # Insertion dans PostgreSQL
├── scrapper_to_mongo.py    # Insertion dans MongoDB
├── flask_api/
│   ├── app.py             # Code de l'API Flask
│   └── Dockerfile         # Dockerfile pour le service Flask
├── dash_app/
│   ├── viz.py             # Tableau de bord Dash
│   └── Dockerfile         # Dockerfile pour le tableau de bord
├── orchestrator/
│   ├── orchestrator.py    # Pipeline central d'exécution
│   └── Dockerfile         # Dockerfile pour le orchestrator
├── data/
│   ├── comments.json      # Fichier JSON des commentaires
│   └── informations_entreprises.csv # Fichier CSV des entreprises
├── docker-compose.yml      # Fichier Docker Compose pour tous les services
└── README.md               # Documentation du projet
```

---

## **Prochaines Améliorations**

1. **Amélioration de l'API** :
   - Ajout de filtres pour les entreprises et les années.
   - Endpoint pour le statut des tâches planifiées.
2. **Visualisation** :
   - Ajout de graphiques supplémentaires pour des insights plus détaillés.
3. **Notifications** :
   - Envoi d'un email après chaque exécution automatique.

---

## **Contributeurs**

- **Nom** : Lemetice
- **Contact** : 

---

## **Licence**

Ce projet est sous licence MIT. Vous êtes libre de le modifier et de l'utiliser comme vous le souhaitez.

