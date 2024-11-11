from datetime import datetime
import os  
from numerize import numerize
import cpi
from HelperMethods import get_float_from_box_office
import image_resize
import omdb_api
from models import noDB_actor, noDB_movie, Meter,Movie


def inflation_safe_year(year):
    current_year = datetime.now().year
    return int(year) if year and year.isdigit() and int(year) < current_year else current_year

def generate_actor_object(actor_name,oscar_wins,oscar_nominations):
    import sys
    from RottenTomatoesScraper import scrape_actor_data, get_actor_birthdate
    Master_api_key = "66f234c0"  # Replace with your actual OMDB API key
    current_year = datetime.now().year
    if "dicaprio" in actor_name.lower():
        tomato_actor_name = "Leonardo Di Caprio"
    else:
        tomato_actor_name = actor_name
    # Fetch actor data
    movies = scrape_actor_data(tomato_actor_name)
    if not movies:
        print(f"Failed to fetch data for {actor_name}.")
        sys.exit(1)
    # Remove movies with no box office or from the future
    current_year = datetime.now().year
    filtered_movies = []
    for movie in movies:
        if movie[3] in ["N/A", "", "-1", "-"] or (movie[2] and int(movie[2]) > current_year):
            continue
        data = omdb_api.get_movie_data(Master_api_key, movie[1])
        if not data or data['Response'] == 'False':
            continue
        actors = data['Actors']
        if actors:
            actorList = [actor.lower() for actor in actors.split(', ')] 
            if actor_name.lower() not in actorList:
                print(f"Removing {movie[1]} - {actor_name} not found in cast")
                continue
        movie[3] = get_float_from_box_office(data['BoxOffice'])
        filtered_movies.append(movie)

    movies = filtered_movies
    for movie in movies:
        movie[3] = get_float_from_box_office(movie[3]) if inflation_safe_year(movie[2]) >= current_year else cpi.inflate(
            get_float_from_box_office(movie[3]),
            inflation_safe_year(movie[2])
        )

    # Convert the movies list to a list of movie class objects
    movie_objects = []
    for movie_data in movies:
        title = movie_data[1]
        year = movie_data[2]
        box_office = movie_data[3]
        tomatometer = float(movie_data[4]) if movie_data[4] else 0
        popcornmeter = float(movie_data[5]) if movie_data[5] else 0
        role = movie_data[6]
        
        movie_obj = noDB_movie(title, year, tomatometer, popcornmeter, box_office, role)
        movie_objects.append(movie_obj)
    
    # Replace the original movies list with the list of movie objects
    movies = movie_objects
    # Get actor's birthdate
    birthdate = get_actor_birthdate(tomato_actor_name)
    if not birthdate:
        print(f"Failed to fetch birthdate for {actor_name}.")
        age = None
    else:
        age = datetime.now().year - birthdate.year
    
    # Create actor instance
    return noDB_actor(actor_name, age, str(birthdate), oscar_wins, oscar_nominations, movies)

def download_posters(actor,poster_movies= None):
    Master_api_key = "66f234c0"  # Replace with your actual OMDB API key
    # Download posters for the movies
    if poster_movies is None:
        poster_movies = actor.movies
    omdb_api.download_movie_posters(Master_api_key, poster_movies, actor.name)
    image_resize.resize_root_poster_folder(actor.name, actor.name)