import asyncio
import json
import pandas as pd
from playwright.async_api import async_playwright
import os

async def scrape_trustpilot():
    async with async_playwright() as p:
        # Lancer le navigateur en mode headless
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Naviguer vers la page principale
        url = "https://www.trustpilot.com/categories/atm"
        await page.goto(url)
        await page.wait_for_load_state('networkidle')

        # Gestion du bouton de consentement
        try:
            await page.click('button.onetrust-close-btn-handler', timeout=5000)
            print("Bouton cliqué avec succès.")
        except Exception:
            print("Bouton de consentement non trouvé ou déjà géré.")

        # Collecte des informations initiales
        # Utilisation du même sélecteur que dans votre code
        div_elements = page.locator('//div[contains(@class, "styles_wrapper")]')
        div_count = await div_elements.count()
        result_list = []

        for i in range(div_count):
            div = div_elements.nth(i)
            try:
                # Trouver les éléments à l'intérieur de chaque div
                elements = div.locator('.styles_footer__DoJVj')
                elements_2 = elements.locator('.styles_wrapper___E6__')
                span_elements = elements_2.locator('span')
                span_count = await span_elements.count()
                concatenated_text = ''
                for j in range(span_count):
                    span = span_elements.nth(j)
                    text = await span.text_content()
                    concatenated_text += text
                result_list.append(concatenated_text)
            except Exception as e:
                print(f"Erreur lors de la collecte des informations initiales : {e}")
                continue

        df_new_column = pd.DataFrame(result_list, columns=['infos'])

        # Collecter les liens des entreprises
        elements = page.locator('div.styles_wrapper__2JOo2')
        element_count = await elements.count()
        liens = []

        # Trouver le bouton "Page suivante"
        next_page_button = await page.query_selector("a[aria-label='Next page']")
        next_page_link = await next_page_button.get_attribute('href')
        # Ajouter le domaine principal si nécessaire
        if next_page_link.startswith('/'):
            next_page_link = 'https://www.trustpilot.com' + next_page_link

        # Ouvrir la page suivante dans une nouvelle page
        next_page = await context.new_page()
        await next_page.goto(next_page_link)
        await next_page.wait_for_load_state('networkidle')

        elements_1 = next_page.locator("//div[@class='styles_businessUnitsCardsContainer__1ggaO']//a")
        elements_1_count = await elements_1.count()
        for i in range(elements_1_count):
            element = elements_1.nth(i)
            href = await element.get_attribute('href')
            if href.startswith('/'):
                href = 'https://www.trustpilot.com' + href
            liens.append(href)

        await next_page.close()

        for i in range(element_count):
            element = elements.nth(i)
            link = element.locator('a')
            href = await link.get_attribute('href')
            if href.startswith('/'):
                href = 'https://www.trustpilot.com' + href
            liens.append(href)

        commentaires_par_agence = []

        for href in liens:
            company_page = await context.new_page()
            await company_page.goto(href)
            await company_page.wait_for_load_state('networkidle')

            # Extraire le pourcentage de 5 étoiles
            try:
                score_5_etoile_element = company_page.locator('//label[@for="reviews-filter-5"]//p[2]')
                score_5_etoile = await score_5_etoile_element.text_content()
            except Exception:
                score_5_etoile = 'NA'

            # Extraire le nom de l'entreprise
            try:
                titre_element = company_page.locator('//h1/span[1]')
                titre_text = (await titre_element.text_content()).strip()
            except Exception:
                titre_text = 'NA'

            # Extraire les commentaires
            comments = company_page.locator('.styles_reviewCardInner__EwDq2')
            comments_count = await comments.count()
            if comments_count > 0:
                for i in range(comments_count):
                    comment = comments.nth(i)
                    try:
                        name_elements = company_page.locator('span[data-consumer-name-typography]')
                        user_name = await name_elements.nth(i).text_content()
                    except Exception:
                        user_name = 'NA'
                    try:
                        location_elements = company_page.locator('[data-consumer-country-typography] > span')
                        user_location = await location_elements.nth(i).text_content()
                    except Exception:
                        user_location = 'NA'
                    try:
                        review_content_element = company_page.locator('div[data-review-content]').first
                        review_content = await review_content_element.text_content()
                    except Exception:
                        review_content = 'NA'
                    try:
                        title = await comment.locator('.typography_heading-s__f7029').text_content()
                    except Exception:
                        title = 'NA'
                    try:
                        review_text = await comment.locator('.typography_body-l__KUYFJ').text_content()
                    except Exception:
                        review_text = 'NA'
                    try:
                        review_count_element = company_page.locator('.styles_consumerExtraDetails__fxS4S > span').first
                        review_count = await review_count_element.text_content()
                    except Exception:
                        review_count = 'NA'
                    try:
                        date_of_experience_element = comment.locator('p[data-service-review-date-of-experience-typography]').first
                        date_of_experience_text = await date_of_experience_element.text_content()
                        date_of_experience = date_of_experience_text.replace('Date of experience: ', '').strip()
                    except Exception:
                        date_of_experience = 'NA'
                    try:
                        reply_element = comment.locator('.paper_paper__1PY90').first
                        reply_text = await reply_element.locator('.styles_message__shHhX').text_content()
                        reply_date_element = reply_element.locator('.styles_replyDate__Iem0_').first
                        reply_date = await reply_date_element.get_attribute('title')
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
                    except Exception:
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
                    commentaires_par_agence.append(comment_data)

            await company_page.close()

        # Assurez-vous que le répertoire 'data' existe
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        os.makedirs(data_dir, exist_ok=True)

        # Sauvegarder les commentaires en JSON
        with open(os.path.join(data_dir, 'df_commentaires_par_entreprise.json'), 'w', encoding='utf-8') as f:
            json.dump(commentaires_par_agence, f, ensure_ascii=False, indent=4)

        print("Les données ont été enregistrées dans le répertoire 'data'.")

        await browser.close()

# Exécuter la fonction de scraping
asyncio.run(scrape_trustpilot())
