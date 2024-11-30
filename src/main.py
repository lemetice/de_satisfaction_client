from selenium import webdriver
from scraper import scrape_trustpilot_enterprises_details, extract_div_elements, extract_entreprise_elements
from data_processing import process_and_join_data
import pandas as pd
import os

if __name__ == "__main__":
    driver = webdriver.Chrome()
    base_url = "https://www.trustpilot.com/categories/atm?page={}"
    all_informations_entreprises = []

    try:
        df_details = scrape_trustpilot_enterprises_details(driver, base_url, num_pages=2)

        for page_num in range(1, 3):
            driver.get(base_url.format(page_num))
            result_list = extract_div_elements(driver)
            #print("Données brutes des div_elements :", result_list)
            df_new_column = pd.DataFrame(result_list, columns=['infos'])
            df_new_column['institution_type'] = df_new_column['infos'].apply(lambda x: x.split('·')[0].strip() if '·' in x else 'NA')
                                                                                    
            page_data = extract_entreprise_elements(driver, df_new_column)
            all_informations_entreprises.extend(page_data)

        df_entreprises = pd.DataFrame(all_informations_entreprises)
        df_final = process_and_join_data(df_entreprises, df_details)
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        os.makedirs(data_dir, exist_ok=True)

        # Sauvegarder le DataFrame
        df_final.to_csv(os.path.join(data_dir, 'informations_entreprises.csv'), index=False)
        #print(df_final.head())

    finally:
        driver.quit()
