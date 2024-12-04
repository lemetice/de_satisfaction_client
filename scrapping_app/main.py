from selenium import webdriver
from src.scrapers.scraper import scrape_trustpilot_enterprises_details, extract_div_elements, extract_entreprise_elements
from src.scrapers.comment_scraper import scrape_trustpilot_comments
from src.utils.data_processing import process_and_join_data
from selenium.webdriver.chrome.options import Options
from src.utils.mongodb_utils import insert_into_mongodb
from src.utils.postgres_utils import insert_into_postgres
from src.utils.data_processing import process_enterprise_data
import pandas as pd
import os
import json

def scrape_and_save_enterprises(driver, base_url, output_dir):
    all_informations_entreprises = []

    # Scrape enterprise details
    df_details = scrape_trustpilot_enterprises_details(driver, base_url, num_pages=2)

    # Scrape and process enterprise data
    for page_num in range(1, 3):
        driver.get(base_url.format(page_num))
        result_list = extract_div_elements(driver)
        df_new_column = pd.DataFrame(result_list, columns=['infos'])
        df_new_column['institution_type'] = df_new_column['infos'].apply(lambda x: x.split('·')[0].strip() if '·' in x else 'NA')

        page_data = extract_entreprise_elements(driver, df_new_column)
        all_informations_entreprises.extend(page_data)

    df_entreprises = pd.DataFrame(all_informations_entreprises)
    df_final = process_and_join_data(df_entreprises, df_details)

    # Save to CSV
    os.makedirs(output_dir, exist_ok=True)
    df_final.to_csv(os.path.join(output_dir, 'informations_entreprises.csv'), index=False)
    print("Entreprise data saved successfully.")

def scrape_and_save_comments(driver, output_dir):
    # Scrape comments
    comments = scrape_trustpilot_comments(driver, base_url, num_pages=2)

    # Save to JSON
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, 'comments.json'), 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False, indent=4)
    print("Comments data saved successfully.")

if __name__ == "__main__":
    options = Options()
    options.add_argument("--headless")  # Mode sans tête
    options.add_argument("--no-sandbox")  # Nécessaire dans Docker
    options.add_argument("--disable-dev-shm-usage")  # Eviter les problèmes de mémoire partagée
    options.add_argument("--disable-gpu")  # Facultatif, recommandé pour les environnements sans GPU
    options.add_argument("--remote-debugging-port=9222")  # Facultatif, pour le débogage
    driver = webdriver.Chrome(options=options)
    base_url = "https://www.trustpilot.com/categories/atm?page={}"
    output_dir = '/app/data'
   
        # Avant l'insertion dans PostgreSQL
    processed_df = process_enterprise_data(
        input_file='/app/data/informations_entreprises.csv',
        output_file='/app/data/processed_informations_entreprises.csv'
    )

    try:
        # Scrape and save enterprises
        scrape_and_save_enterprises(driver, base_url, output_dir)

        # Scrape and save comments
        scrape_and_save_comments(driver, output_dir)

    except Exception as e:
        print(f"An error occurred during scraping: {e}")

    finally:
        driver.quit()
