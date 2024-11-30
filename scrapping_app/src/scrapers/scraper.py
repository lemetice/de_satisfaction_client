from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

def scrape_trustpilot_enterprises_details(driver, base_url, num_pages=1):
    liens = []
    score_etoile = []
    commentaires_par_agence = []

    for page_num in range(1, num_pages + 1):
        driver.get(base_url.format(page_num))

        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.paper_paper__1PY90.paper_outline__lwsUX.card_card__lQWDv.card_noPadding__D8PcU.styles_wrapper__2JOo2'))
        )
        for element in elements:
            try:
                link = element.find_element(By.TAG_NAME, 'a')
                href = link.get_attribute('href')
                liens.append(href)
            except Exception:
                liens.append('NA')

        try:
            next_page_button = driver.find_element(By.XPATH, "//a[@aria-label='Next page']")
            next_page_link = next_page_button.get_attribute('href')

            driver.execute_script(f"window.open('{next_page_link}', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])

            elements_1 = driver.find_elements(By.XPATH, "/html/body/div[1]/div/div/main/div/div[2]/div/section/div[4]/a")
            for element in elements_1:
                liens.append(element.get_attribute('href'))

            elements_2 = driver.find_elements(By.XPATH, "/html/body/div[1]/div/div/main/div/div[2]/div/section/div[5]/a")
            for element in elements_2:
                liens.append(element.get_attribute('href'))

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except Exception:
            print("Pas de bouton de page suivante trouvé.")

    for lien in liens:
        try:
            driver.execute_script(f"window.open('{lien}', '_blank');")
            driver.switch_to.window(driver.window_handles[-1])

            try:
                score_5_etoile_element = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/main/div/div[4]/section/div[2]/div[2]/label[1]/p[2]')
                score_5_etoile = score_5_etoile_element.text.replace('%', '').strip()
                score_etoile.append(float(score_5_etoile) if score_5_etoile.isdigit() else 'NA')
            except Exception:
                score_etoile.append('NA')

            try:
                titre = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/main/div/div[3]/div[2]/div/div/div/section/div[1]/div[2]/h1/span[1]'))
                )
                titre_text = titre.text.strip()
                commentaires_par_agence.append(titre_text)
            except Exception:
                commentaires_par_agence.append('NA')

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except Exception as e:
            print(f"Erreur lors de l'extraction des détails pour le lien : {lien}. Erreur : {e}")
            score_etoile.append('NA')
            commentaires_par_agence.append('NA')

    data = {
        'Lien': liens,
        'five_Star_Percentage': score_etoile,
        'Commentaire': commentaires_par_agence
    }
    return pd.DataFrame(data)

def extract_div_elements(driver):
    div_elements = driver.find_elements(By.XPATH, '//div[@class="paper_paper__1PY90 paper_outline__lwsUX card_card__lQWDv card_noPadding__D8PcU styles_wrapper__2JOo2"]')
    result_list = []  # Liste pour stocker les résultats

    for div in div_elements:
        try:
            # Localiser les sous-éléments dans chaque carte
            elements = div.find_element(By.CLASS_NAME, 'styles_footer__DoJVj')
            elements_2 = elements.find_element(By.CLASS_NAME, 'styles_wrapper___E6__')
            span_elements = elements_2.find_elements(By.TAG_NAME, 'span')

            # Concaténer le texte de tous les <span>
            concatenated_text = ''
            for span in span_elements:
                concatenated_text += span.text + '·'  # Ajout du séparateur explicite

            # Ajouter le texte concaténé à la liste
            result_list.append(concatenated_text.strip('·'))  # Retirer le dernier séparateur inutile
        except Exception as e:
            # En cas d'erreur, ajouter une valeur par défaut
            result_list.append('NA')
    return result_list

def extract_entreprise_elements(driver, df_new_column):
    entreprise_elements = driver.find_elements(By.CLASS_NAME, 'styles_businessUnitMain__PuwB7')
    informations_entreprises = []

    for i, entreprise in enumerate(entreprise_elements):
        try:
            emplacement = entreprise.find_element(By.CSS_SELECTOR, 'span.styles_location__ILZb0').text
            location_parts = emplacement.split(",")
            town = location_parts[0].strip() if len(location_parts) > 0 else 'NA'
            country = location_parts[1].strip() if len(location_parts) > 1 else 'NA'
        except Exception:
            town, country = 'NA', 'NA'

        try:
            nom_entreprise = entreprise.find_element(By.CSS_SELECTOR, 'p.typography_heading-xs__jSwUz').text
        except Exception:
            nom_entreprise = 'NA'

        try:
            trust_score_element = entreprise.find_element(By.CSS_SELECTOR, 'span.typography_body-m__xgxZ_')
            trust_score = trust_score_element.text.split()[-1]
            trust_score = trust_score if trust_score.replace('.', '', 1).isdigit() else 'NA'
        except Exception:
            trust_score = 'NA'

        try:
            reviews_text = entreprise.find_element(By.CSS_SELECTOR, 'p.styles_ratingText__yQ5S7').text.split('|')[-1].strip()
            reviews = ''.join(filter(str.isdigit, reviews_text))
        except Exception:
            reviews = 'NA'

        informations_entreprises.append({
            'town': town,
            'country': country,
            'institution_type': df_new_column['institution_type'][i] if i < len(df_new_column) else 'NA',
            'company_name': nom_entreprise,
            'trust_score': trust_score,
            'review': reviews
        })
    return informations_entreprises
