import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import warnings
import os

warnings.filterwarnings("ignore")

def scrape_trustpilot():
    # Configuration du WebDriver
    driver = webdriver.Chrome()
    url = "https://www.trustpilot.com/categories/atm"
    driver.get(url)
    wait = WebDriverWait(driver, 5)
    time.sleep(2)

    # Gestion du bouton de consentement
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'onetrust-close-btn-handler'))
        )
        button.click()
        print("Bouton cliqué avec succès.")
    except Exception as e:
        print("Impossible de cliquer sur le bouton :", e)

    # Collecte des informations initiales
    div_elements = driver.find_elements(By.XPATH, '//div[@class="paper_paper__1PY90 paper_outline__lwsUX card_card__lQWDv card_noPadding__D8PcU styles_wrapper__2JOo2"]')
    result_list = []
    for div in div_elements:
        elements = div.find_element(By.CLASS_NAME, 'styles_footer__DoJVj')
        elements_2 = elements.find_element(By.CLASS_NAME, 'styles_wrapper___E6__')
        span_elements = elements_2.find_elements(By.TAG_NAME, 'span')
        concatenated_text = '' 
        for span in span_elements:
            concatenated_text += span.text 
        result_list.append(concatenated_text)
    df_new_column = pd.DataFrame(result_list, columns=['infos'])

    # Reccuperons les differents liens
    elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.paper_paper__1PY90.paper_outline__lwsUX.card_card__lQWDv.card_noPadding__D8PcU.styles_wrapper__2JOo2'))
    )
    liens = []

    next_page_button = driver.find_element(By.XPATH, "//a[@aria-label='Next page']")
    next_page_link = next_page_button.get_attribute('href')

    driver.execute_script("window.open('{}', '_blank');".format(next_page_link))
    driver.switch_to.window(driver.window_handles[-1])

    elements_1 = driver.find_elements(By.XPATH, "/html/body/div[1]/div/div/main/div/div[2]/div/section/div[4]/a")
    for element in elements_1:
        href = element.get_attribute('href')
        liens.append(href)
    elements_2 = driver.find_elements(By.XPATH, "/html/body/div[1]/div/div/main/div/div[2]/div/section/div[5]/a")
    for element in elements_2:
        href = element.get_attribute('href')
        liens.append(href)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    for element in elements:
        link = element.find_element(By.TAG_NAME, 'a')
        href = link.get_attribute('href')
        liens.append(href)

    # Attendre que tous les éléments avec la classe spécifique soient présents dans le DOM
    elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.paper_paper__1PY90.paper_outline__lwsUX.card_card__lQWDv.card_noPadding__D8PcU.styles_wrapper__2JOo2'))
    )

    score_etoile = []
    commentaires_par_agence = []

    for element in elements:
        link = element.find_element(By.TAG_NAME, 'a')
        href = link.get_attribute('href')

        driver.execute_script("window.open('{}', '_blank');".format(href))

        driver.switch_to.window(driver.window_handles[-1])
        
        score_5_etoile = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/main/div/div[4]/section/div[2]/div[2]/label[1]/p[2]')
        score_5_etoile = score_5_etoile.text
        score_etoile.append(score_5_etoile)
        
        titre = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/main/div/div[3]/div[2]/div/div/div/section/div[1]/div[2]/h1/span[1]'))
            )
        titre_text = titre.text.strip()

        comments = driver.find_elements(By.CSS_SELECTOR, '.styles_reviewCardInner__EwDq2')
            
        if comments:
            i = 0
            for comment in comments:
                try:
                    name_element = driver.find_elements(By.CSS_SELECTOR, 'span[data-consumer-name-typography]')
                    name_element = name_element[i]
                    user_name = name_element.text
                except Exception as e:
                    user_name = 'NA' 
                try:
                    location_element = driver.find_elements(By.CSS_SELECTOR, '[data-consumer-country-typography] > span')
                    location_element = location_element[i]
                    user_location = location_element.text
                except Exception as e:
                    user_location = 'NA' 
                try:
                    review_content_element = driver.find_element(By.CSS_SELECTOR, 'div[data-review-content]')
                    review_content = review_content_element.text
                except Exception as e:
                    review_content = 'NA' 
                try:
                    title = comment.find_element(By.CSS_SELECTOR, '.typography_heading-s__f7029').text
                except Exception as e:
                    title = 'NA'          
                try:
                    review_text = comment.find_element(By.CSS_SELECTOR, '.typography_body-l__KUYFJ').text
                except Exception as e:
                    review_text = 'NA'          
                try:
                    review_count_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.styles_consumerExtraDetails__fxS4S > span.typography_body-m__xgxZ_'))
                    )
                    review_count = review_count_element.text
                except NoSuchElementException:
                    review_count = 'NA'       
                try:
                    date_of_experience_element = comment.find_element(By.CSS_SELECTOR, 'p[data-service-review-date-of-experience-typography]')
                    date_of_experience = date_of_experience_element.text.replace('Date of experience: ', '').strip()
                except NoSuchElementException:
                    date_of_experience = 'NA'                
                try:
                    reply_element = comment.find_element(By.CSS_SELECTOR, '.paper_paper__1PY90')
                    reply_text = reply_element.find_element(By.CSS_SELECTOR, '.styles_message__shHhX').text
                    reply_date_element = reply_element.find_element(By.CSS_SELECTOR, '.styles_replyDate__Iem0_')
                    reply_date = reply_date_element.get_attribute('title')
                    
                    comment_data = {
                    'company_name': titre_text,
                    'User': user_name,
                    'localisation': user_location,
                    'Titre': title,
                    'commentaire': review_text,
                    'nombre_reviews': review_count,
                    'date_experience': date_of_experience,
                    'reply': {
                        'reply_text': reply_text,
                        'reply_date': reply_date
                    }
                }
                except NoSuchElementException:
                    comment_data = {
                        'company_name': titre_text,
                        'User': user_name,
                        'localisation': user_location,
                        'Titre': title,
                        'commentaire': review_text,
                        'nombre_reviews': review_count,
                        'date_experience': date_of_experience,
                        'reply': None
                    }

                # Ajouter les données du commentaire (avec ou sans réponse) à la liste des commentaires de l'agence
                commentaires_par_agence.append(comment_data)
                i = i+1
                
        driver.close()

        driver.switch_to.window(driver.window_handles[0])
        


    # Assurez-vous que le répertoire parent 'data' existe
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    os.makedirs(data_dir, exist_ok=True)


    # Sauvegarder les commentaires en JSON
    with open(os.path.join(data_dir, 'df_commentaires_per_entreprise.json'), 'w', encoding='utf-8') as f:
        json.dump(commentaires_par_agence, f, ensure_ascii=False, indent=4)

    print("Les données ont été enregistrées dans le répertoire parent 'data'.")

    driver.quit()

# Exécuter la fonction de scraping
scrape_trustpilot()
