import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse

def scrape_all_extreme_droite():
    base_url = "https://www.france-politique.fr"
    # URL de départ (la catégorie)
    current_url = "/wiki/Cat%C3%A9gorie:Mouvements_d%27extr%C3%AAme_droite_depuis_1945"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    all_partis = []

    while current_url:
        print(f"Extraction de : {base_url + current_url}")
        response = requests.get(base_url + current_url, headers=headers)
        if response.status_code != 200:
            break
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Extraction des partis sur la page actuelle
        category_div = soup.find('div', class_='mw-category')
        if category_div:
            liens = category_div.find_all('a')
            for lien in liens:
                nom = lien.get_text()
                # On filtre pour éviter d'éventuels liens de maintenance du wiki
                if "Catégorie:" not in nom:
                    all_partis.append([nom])

        # 2. Recherche du lien "page suivante"
        # Dans MediaWiki, les liens de pagination sont souvent dans un élément avec l'ID 'mw-pages'
        next_page_link = None
        pagination_links = soup.find('div', id='mw-pages').find_all('a')
        
        for link in pagination_links:
            if "page suivante" in link.get_text().lower():
                next_page_link = link.get('href')
                break # On a trouvé le lien
        
        # Si on trouve un lien, on met à jour current_url pour la prochaine itération
        # Sinon, on met current_url à None pour arrêter la boucle
        current_url = next_page_link

    # Exportation finale en CSV
    filename = "liste_complete_extreme_droite.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Nom du mouvement'])
        writer.writerows(all_partis)
# doit être 232 parce qu'il y a 232 partis en tout:) !! 
    print(f"\n {len(all_partis)} mouvements ont été enregistrés dans {filename}.")



scrape_all_extreme_droite()