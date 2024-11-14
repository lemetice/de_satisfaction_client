# Utiliser une image Python légère
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copier le fichier principal de l'API
COPY app.py app.py

# Exposer le port utilisé par Flask
EXPOSE 5000

# Commande de démarrage
CMD ["python", "app.py"]
