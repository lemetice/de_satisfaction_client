# Étape 1 : Base Python
FROM python:3.9-slim

# Étape 2 : Copier uniquement requirements.txt pour installer les dépendances Python
COPY requirements.txt /app/requirements.txt

# Étape 3 : Installer les dépendances Python
RUN pip install --no-cache-dir -r /app/requirements.txt

# Étape 4 : Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    gnupg \
    unzip \
    fonts-liberation \
    libvulkan1 \
    xdg-utils \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libepoxy0 \
    libgtk-3-0 \
    libdrm2 \
    libxshmfence1 && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade numpy pandas selenium
USER root

RUN rm -f /usr/bin/chromedriver && rm -f /usr/local/bin/chromedriver

# Ajouter la clé de signature de Google et le dépôt
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

    RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
    
    # Mettre à jour la liste des paquets
    RUN apt-get update -y
    
    #Installer Google Chrome
    RUN wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
        && apt install -y /tmp/chrome.deb \
        && rm /tmp/chrome.deb
    
    # Définir le dossier pour Chromedriver
    ENV CHROMEDRIVER_DIR /chromedriver
    RUN mkdir -p $CHROMEDRIVER_DIR  
    
    # Télécharger et installer Chromedriver
    RUN wget -q -P $CHROMEDRIVER_DIR "https://storage.googleapis.com/chrome-for-testing-public/130.0.6723.116/linux64/chromedriver-linux64.zip" \
        && unzip -o $CHROMEDRIVER_DIR/chromedriver-linux64.zip -d $CHROMEDRIVER_DIR \
        && rm $CHROMEDRIVER_DIR/chromedriver-linux64.zip
    
    # Ajouter ChromeDriver au PATH
    ENV PATH $CHROMEDRIVER_DIR:$PATH

# Étape 7 : Copier le code de scraping
WORKDIR /app
# Étape 7 : Copier les fichiers de l'application dans le conteneur
COPY . /app

# Installer les dépendances Python
RUN pip install --no-cache-dir -r /app/requirements.txt

# Étape 9 : Commande par défaut pour exécuter le script de scraping
CMD ["python", "scrapping.py"]
