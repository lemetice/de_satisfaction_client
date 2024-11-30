import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os


def scrape_trustpilot_comments(driver, base_url, num_pages=1):
    """
    Scrape les commentaires des entreprises sur Trustpilot.

    Arguments :
    - driver : instance du WebDriver Selenium.
    - base_url : URL de base de la catégorie Trustpilot.
    - num_pages : nombre de pages à parcourir.

    Retourne :
    - commentaires_par_agence : liste de dictionnaires contenant les détails des commentaires.
    """
    commentaires_par_agence = []

    for page_num in range(1, num_pages + 1):
        driver.get(base_url.format(page_num))
        time.sleep(2)  # Ajoutez un délai pour permettre le chargement de la page.

        # Récupérer les liens des entreprises
        try:
            elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.paper_paper__1PY90.paper_outline__lwsUX.card_card__lQWDv.card_noPadding__D8PcU.styles_wrapper__2JOo2'))
            )
        except Exception as e:
            print(f"Erreur lors de la récupération des liens : {e}")
            continue

        liens = []
        for element in elements:
            try:
                link = element.find_element(By.TAG_NAME, 'a')
                liens.append(link.get_attribute('href'))
            except Exception as e:
                print(f"Erreur lors de l'extraction du lien d'entreprise : {e}")
                continue

        # Parcourir les liens pour extraire les commentaires
        for lien in liens:
            try:
                driver.execute_script(f"window.open('{lien}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])

                # Récupérer le nom de l'entreprise
                titre = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/main/div/div[3]/div[2]/div/div/div/section/div[1]/div[2]/h1/span[1]'))
                )
                titre_text = titre.text.strip()

                # Récupérer les commentaires
                comments = driver.find_elements(By.CSS_SELECTOR, '.styles_reviewCardInner__EwDq2')
                if comments:
                    for i, comment in enumerate(comments):
                        try:
                            user_name = driver.find_elements(By.CSS_SELECTOR, 'span[data-consumer-name-typography]')[i].text
                        except Exception:
                            user_name = 'NA'

                        try:
                            user_location = driver.find_elements(By.CSS_SELECTOR, '[data-consumer-country-typography] > span')[i].text
                        except Exception:
                            user_location = 'NA'

                        try:
                            review_content = comment.find_element(By.CSS_SELECTOR, 'div[data-review-content]').text
                        except Exception:
                            review_content = 'NA'

                        try:
                            title = comment.find_element(By.CSS_SELECTOR, '.typography_heading-s__f7029').text
                        except Exception:
                            title = 'NA'

                        try:
                            review_text = comment.find_element(By.CSS_SELECTOR, '.typography_body-l__KUYFJ').text
                        except Exception:
                            review_text = 'NA'

                        try:
                            date_of_experience = comment.find_element(By.CSS_SELECTOR, 'p[data-service-review-date-of-experience-typography]').text.replace('Date of experience: ', '').strip()
                        except Exception:
                            date_of_experience = 'NA'

                        # Ajouter les données du commentaire
                        commentaires_par_agence.append({
                            'company_name': titre_text,
                            'user_name': user_name,
                            'user_location': user_location,
                            'title': title,
                            'comment': review_text,
                            'review_content': review_content,
                            'date_of_experience': date_of_experience
                        })

                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except Exception as e:
                print(f"Erreur lors de l'extraction des commentaires pour le lien : {lien}. Erreur : {e}")
                continue

    return commentaires_par_agence


# Exemple d'utilisation
if __name__ == "__main__":
    from selenium import webdriver

    # Configurer le WebDriver
    options = Options()
    options.add_argument("--headless")  # Mode sans tête
    options.add_argument("--no-sandbox")  # Nécessaire dans Docker
    options.add_argument("--disable-dev-shm-usage")  # Eviter les problèmes de mémoire partagée
    options.add_argument("--disable-gpu")  # Facultatif, recommandé pour les environnements sans GPU
    options.add_argument("--remote-debugging-port=9222")  # Facultatif, pour le débogage
    driver = webdriver.Chrome(options=options)
    base_url = "https://www.trustpilot.com/categories/atm?page={}"

    try:
        commentaires = scrape_trustpilot_comments(driver, base_url, num_pages=2)

        # Assurez-vous que le répertoire parent 'data' existe
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        os.makedirs(data_dir, exist_ok=True)

        with open(os.path.join(data_dir, 'trustpilot_comments.json'), 'w', encoding='utf-8') as f:
            json.dump(commentaires, f, ensure_ascii=False, indent=4)
        print("Scraping des commentaires terminé et sauvegardé.")


    finally:
        driver.quit()
