# Utiliser une image de base Python légère
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY requirements.txt requirements.txt
COPY viz.py .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port utilisé par Dash
EXPOSE 8050

# Démarrer l'application Dash
CMD ["python", "viz.py"]
