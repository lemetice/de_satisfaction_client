# Utiliser une image légère de Python
FROM python:3.9-slim

# Installer les dépendances nécessaires pour Selenium et ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libnss3 \
    libgconf-2-4 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    chromium \
    chromium-driver \
    && apt-get clean

# Définir le répertoire de travail
WORKDIR /app

#Repertoire de sauvegarde des données
RUN mkdir -p /app/data

# Copier les fichiers nécessaires dans le conteneur
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .  
COPY src/ src/
COPY data/ ./data/

# Exposer un port si nécessaire (non nécessaire pour un scraper, mais utile si vous utilisez Flask ou Dash)
# EXPOSE 8050

# Commande par défaut pour exécuter votre script principal
CMD ["python", "main.py"]
