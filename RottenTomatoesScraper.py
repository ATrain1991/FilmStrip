import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_actor_url_soup(actor_name):
        formatted_name = actor_name.lower().replace(' ', '_').replace('.', '').replace("'", "").replace('-','_')
        url = f'https://www.rottentomatoes.com/celebrity/{formatted_name}'
    
    # Fetch the page content
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data for {actor_name}. Status code: {response.status_code}")
            return None  
        else:
            print(f"Successfully fetched data for {actor_name}")
            return BeautifulSoup(response.text, 'html.parser')
def get_actor_portrait(actor_name):
    soup = get_actor_url_soup(actor_name)
    if not soup:
        return None

    import os
    images = soup.find_all('img')
    portrait_element = soup.find('img', alt=lambda alt: alt and 'portrait photo of' in alt.lower() and actor_name.lower() in alt.lower())
    if portrait_element:
        portrait_url = portrait_element['src']
        response = requests.get(portrait_url)
        if response.status_code == 200:
            output_folder = 'actor_portraits'
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            file_path = os.path.join(output_folder, f"{actor_name.replace(' ', '_').lower()}.jpg")
            with open(file_path, 'wb') as file:
                file.write(response.content)
            return file_path
        else:
            print(f"Failed to download portrait for {actor_name}. Status code: {response.status_code}")
            return None
    else:
        print(f"Failed to find portrait for {actor_name}")
        return None

def get_actor_birthdate(actor_name):
    # Update or add the birthdate to the actor in the database
        from datetime import datetime
        soup=get_actor_url_soup(actor_name)

        birthday_element = soup.find('p', class_='celebrity-bio__item', attrs={'data-qa': 'celebrity-bio-bday'})
        birthday_text = birthday_element.text.strip().split(':')[-1].strip()
        try:
            return datetime.strptime(birthday_text, '%b %d, %Y').date()
        except ValueError:
            print(f"Failed to parse birthday: {birthday_text}")

def scrape_actor_data(actor_name):
    # Format the actor name for the URL
    soup=get_actor_url_soup(actor_name)
    if not soup:
        return None
#remove tv section
    tv_section = soup.find('rt-text', string=lambda text: text and text.strip() == 'TV')
    if tv_section:
        # Remove everything after the TV section
        for element in tv_section.find_all_next():
            element.decompose()

    # Scrape movies data
    movies_data = []
    movie_id = 0
    for row in soup.select('tr[data-title]'):
        title = row.select_one('.celebrity-filmography__title a')
        title = title.text.strip() if title else None

        year_elem = row.select_one('.celebrity-filmography__year')
        year = year_elem.text.strip() if year_elem else None

        tomatometer_elem = row.select_one('[data-tomatometer]')
        tomatometer = tomatometer_elem['data-tomatometer'] if tomatometer_elem and tomatometer_elem['data-tomatometer'] not in ["N/A", "", "-1", "-","No Score Yet"] else None

        box_office_elem = row.select_one('.celebrity-filmography__box-office')
        box_office = box_office_elem.text.strip() if box_office_elem else None

        audience_score_elem = row.select_one('[data-audiencescore]')
        popcornmeter = audience_score_elem['data-audiencescore'] if audience_score_elem else None

        credit_elem = row.select_one('.celebrity-filmography__credits')
        credit = credit_elem.text.strip() if credit_elem else None
        
        
        movies_data.append([
            movie_id,
            title,
            year,
            box_office,
            tomatometer,
            popcornmeter,
            credit
        ])
        movie_id += 1

    return movies_data