import pandas as pd

# Charger le fichier source
input_file = "informations_entreprises.csv"
output_file = "data.csv"

# Charger les données
df = pd.read_csv(input_file)

# Nettoyer les pourcentages et les transformer en valeurs numériques
df['five_star_percentage'] = df['five_star_%'].str.rstrip('%').astype(float)

# Supprimer la colonne originale
df.drop(columns=['five_star_%'], inplace=True)

# Sauvegarder dans un nouveau fichier ou écraser l'existant
df.to_csv(output_file, index=False)

print(f"Fichier traité et sauvegardé dans : {output_file}")
