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

    # Collecter les informations sur les entreprises
    entreprise_elements = driver.find_elements(By.CLASS_NAME, 'styles_businessUnitMain__PuwB7')
    informations_entreprises = []

    next_page_button = driver.find_element(By.XPATH, "//a[@aria-label='Next page']")
    next_page_link = next_page_button.get_attribute('href')

    driver.execute_script("window.open('{}', '_blank');".format(next_page_link))
    driver.switch_to.window(driver.window_handles[-1])
    entreprise_elements_2 = driver.find_elements(By.CLASS_NAME, 'styles_businessUnitMain__PuwB7')

    try:
        nom_entreprise_element = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/main/div/div[2]/div/section/div[4]/a/div/div[2]/p')
        nom_entreprise1 = nom_entreprise_element.text
    except NoSuchElementException:
        nom_entreprise1 = 'NA'

    try:
        trust_score_element = driver.find_element(By.CSS_SELECTOR, 'span.typography_body-m__xgxZ_')
        trust_score1 = trust_score_element.text.split()[-1]
    except NoSuchElementException:
        trust_score1 = 'NA'

    try:
        reviews_element = driver.find_element(By.CSS_SELECTOR, 'p.styles_ratingText__yQ5S7')
        reviews1 = reviews_element.text.split('|')[-1].strip()
    except NoSuchElementException:
        reviews1 = 'NA'
    try:
        emplacement_element1 = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/main/div/div[2]/div/section/div[4]/a/div/div[2]/div/span')
        emplacement1 = emplacement_element1.text
    except NoSuchElementException:
        emplacement1 = 'NA'

    if reviews1 == 'NA':
        trust_score1 = 'NA'

    div_elements = driver.find_elements(By.XPATH, '//div[@class="paper_paper__1PY90 paper_outline__lwsUX card_card__lQWDv card_noPadding__D8PcU styles_wrapper__2JOo2"]')
    for div in div_elements:
        elements = div.find_element(By.CLASS_NAME, 'styles_footer__DoJVj')
        elements_2 = elements.find_element(By.CLASS_NAME, 'styles_wrapper___E6__')
        span_elements = elements_2.find_elements(By.TAG_NAME, 'span')
        concatenated_text = '' 
        for span in span_elements:
            concatenated_text += span.text
        result_list.append(concatenated_text)

    df_new_column = pd.DataFrame(result_list, columns=['infos'])

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    entreprise_elements = entreprise_elements + entreprise_elements_2

    for entreprise in entreprise_elements[0:24]:
        try:
            nom_entreprise = entreprise.find_element(By.CSS_SELECTOR, 'p.styles_displayName__GOhL2').text
        except Exception as e:
            nom_entreprise = 'NA'

        try:
            trust_score_element = entreprise.find_element(By.CSS_SELECTOR, 'span.typography_body-m__xgxZ_')
            trust_score = trust_score_element.text.split()[-1]
        except Exception as e:
            trust_score = 'NA'

        try:
            reviews = entreprise.find_element(By.CSS_SELECTOR, 'p.styles_ratingText__yQ5S7').text.split('|')[-1].strip()
        except Exception as e:
            reviews = 'NA'

        try:
            emplacement = entreprise.find_element(By.CSS_SELECTOR, 'span.styles_location__ILZb0').text
        except Exception as e:
            emplacement = 'NA'

        if reviews == 'NA':
            trust_score = 'NA'
        
        informations_entreprises.append({
            'Nom': nom_entreprise,
            'TrustScore': trust_score,
            'Reviews': reviews,
            'Emplacement': emplacement,
        })

    informations_entreprises.append({
        'Nom': nom_entreprise1,
        'TrustScore': trust_score1,
        'Reviews': reviews1,
        'Emplacement': emplacement1,
    })

    # Créer un DataFrame avec les informations des entreprises
    df_entreprises = pd.DataFrame(informations_entreprises)
    df_entreprises = df_entreprises.assign(infos=df_new_column)

    driver_2 = webdriver.Chrome()
    driver_2.get("https://www.trustpilot.com/categories/atm?page=2")
    data_2 = []
    cards = driver_2.find_elements(By.CSS_SELECTOR, ".card_card__lQWDv")

    for card in cards:
        try:
            name = card.find_element(By.CSS_SELECTOR, ".styles_displayName__GOhL2").text
        except:
            name = "NA"
        
        try:
            location = card.find_element(By.CSS_SELECTOR, ".styles_location__ILZb0").text
        except:
            location = "NA"
        
        try:
            infos = [info.text for info in card.find_elements(By.CSS_SELECTOR, ".styles_categoriesLabels__FiWQ4 span")]
            infos = "·".join(infos)
        except:
            infos = "NA"

        data_2.append({
            "Nom": name,
            "Location": location,
            "Infos": infos
        })
    data_2 = pd.DataFrame(data_2)
    data_2 = data_2.iloc[2:6].head()

    df_entreprises.iloc[20, df_entreprises.columns.get_loc('Nom')] = data_2.iloc[0, data_2.columns.get_loc('Nom')]
    df_entreprises.iloc[21, df_entreprises.columns.get_loc('Nom')] = data_2.iloc[1, data_2.columns.get_loc('Nom')]
    df_entreprises.iloc[22, df_entreprises.columns.get_loc('Nom')] = data_2.iloc[2, data_2.columns.get_loc('Nom')]
    df_entreprises.iloc[23, df_entreprises.columns.get_loc('Nom')] = data_2.iloc[3, data_2.columns.get_loc('Nom')]

    df_entreprises.iloc[20, df_entreprises.columns.get_loc('Emplacement')] = data_2.iloc[0, data_2.columns.get_loc('Location')]
    df_entreprises.iloc[21, df_entreprises.columns.get_loc('Emplacement')] = data_2.iloc[1, data_2.columns.get_loc('Location')]
    df_entreprises.iloc[22, df_entreprises.columns.get_loc('Emplacement')] = data_2.iloc[2, data_2.columns.get_loc('Location')]
    df_entreprises.iloc[23, df_entreprises.columns.get_loc('Emplacement')] = data_2.iloc[3, data_2.columns.get_loc('Location')]

    df_entreprises.iloc[20, df_entreprises.columns.get_loc('infos')] = data_2.iloc[0, data_2.columns.get_loc('Infos')]
    df_entreprises.iloc[21, df_entreprises.columns.get_loc('infos')] = data_2.iloc[1, data_2.columns.get_loc('Infos')]
    df_entreprises.iloc[22, df_entreprises.columns.get_loc('infos')] = data_2.iloc[2, data_2.columns.get_loc('Infos')]
    df_entreprises.iloc[23, df_entreprises.columns.get_loc('infos')] = data_2.iloc[3, data_2.columns.get_loc('Infos')]

    df_entreprises.head(24)

    # Extraire des informations supplémentaires et les ajouter au DataFrame
    df_entreprises['Reviews'] = df_entreprises['Reviews'].apply(
        lambda x: int(''.join(filter(str.isdigit, str(x)))) if x != 'NA' else 0)
    df_entreprises['review'] = df_entreprises['Reviews'].apply(lambda x: int(str(x).replace(',', '')) if x != 'NA' else 0)
    df_entreprises['town'] = df_entreprises['Emplacement'].apply(lambda x: str(x).split(',')[0])
    df_entreprises['country'] = df_entreprises['Emplacement'].apply(lambda x: str(x).split(',')[-1])
    df_entreprises['institution_type'] = df_entreprises['infos'].apply(lambda x: str(x).split('·')[0])
    df_entreprises['company_name'] = df_entreprises['Nom']
    df_entreprises['trust_score'] = df_entreprises['TrustScore']

    df_entreprises = df_entreprises.drop(columns=['Nom', 'TrustScore', 'Reviews', 'Emplacement', 'infos'])

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
        
    score_etoile.append(score_5_etoile)

    df_new_column = pd.DataFrame(score_etoile, columns=['five_star_%'])
    df_entreprises['five_star_%'] = df_new_column
    cols = df_entreprises.columns.tolist() 
    cols.insert(5, cols.pop(0))
    df_entreprises = df_entreprises[cols]
    df_entreprises = df_entreprises.head(24)
    df_entreprises.head(30)


    # Assurez-vous que le répertoire parent 'data' existe
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    os.makedirs(data_dir, exist_ok=True)

    # Sauvegarder le DataFrame
    df_entreprises.to_csv(os.path.join(data_dir, 'informations_entreprises.csv'), index=False)

    # Sauvegarder les commentaires en JSON
    with open(os.path.join(data_dir, 'df_commentaires_par_entreprise.json'), 'w', encoding='utf-8') as f:
        json.dump(commentaires_par_agence, f, ensure_ascii=False, indent=4)

    print("Les données ont été enregistrées dans le répertoire parent 'data'.")

    driver.quit()

# Exécuter la fonction de scraping
scrape_trustpilot()
