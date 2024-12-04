import os
from src.utils.data_processing import process_enterprise_data

def main():
    # Chemins des fichiers
    input_file = "/app/data/informations_entreprises.csv"
    output_file = "/app/data/processed_informations_entreprises.csv"

    # Vérifier si le fichier d'entrée existe
    if not os.path.exists(input_file):
        print(f"Erreur : Le fichier {input_file} n'existe pas.")
        return

    # Appeler la fonction de preprocessing
    processed_df = process_enterprise_data(input_file, output_file)

    if processed_df is not None:
        print("Preprocessing terminé avec succès.")
    else:
        print("Une erreur s'est produite lors du preprocessing.")

if __name__ == "__main__":
    main()
