from time import time
from csv_exporter import export_actor_speedrun
import csv_exporter
from databaseManager import DatabaseManager
from databaseModels import Actor, Movie
import config
from image_resize import resize_root_poster_folder
import imdb
import omdb_api
from RottenTomatoesScraper import get_actor_birthdate, scrape_actor_data, get_actor_portrait


def Add_movie_to_db(movie_title,tomato_meter,popcorn_meter):
    db_manager = DatabaseManager()
    movie_data = {
        'title': omdb_api.get_title_from_omdb(omdb_api.Master_api_key, movie_title),
        'genre': omdb_api.get_genre_from_omdb(omdb_api.Master_api_key, movie_title),
        'director': omdb_api.get_director_from_omdb(omdb_api.Master_api_key, movie_title),
        # 'actors': omdb_api.get_actors_from_omdb(omdb_api.Master_api_key, movie_title),
        'release_date': omdb_api.get_releaseDate_from_omdb(omdb_api.Master_api_key, movie_title),
        'runtime': omdb_api.get_runtime_from_omdb(omdb_api.Master_api_key, movie_title),
        'mpaa_rating': omdb_api.get_rated_from_omdb(omdb_api.Master_api_key, movie_title),
        'synopsis': omdb_api.get_plot_from_omdb(omdb_api.Master_api_key, movie_title),
        # 'poster_bytes': omdb_api.get_poster_bytes_from_omdb(omdb_api.Master_api_key, movie_title),
        # 'poster_path': omdb_api.get_poster_path_from_omdb(omdb_api.Master_api_key, movie_title),
        'imdb_score': omdb_api.get_imdb_rating_from_omdb(omdb_api.Master_api_key, movie_title),
        'box_office': omdb_api.get_box_office_from_omdb(omdb_api.Master_api_key, movie_title),
        'awards': omdb_api.get_awards_from_omdb(omdb_api.Master_api_key, movie_title),
        'tomato_meter': tomato_meter,
        'popcorn_meter': popcorn_meter
    }

    sanitized_movie_data = sanitize_movie_data(movie_data)

    db_manager.add_or_update_movie(**sanitized_movie_data)

def get_Actor_Portrait(name):
    # portrait_path = get_actor_portrait(name)
    portrait_path = imdb.get_actor_portrait(name)
    existing_actor = db_manager.session.query(Actor).filter_by(name=name).first()
    if existing_actor:
        existing_actor.portrait_path = portrait_path
        db_manager.session.commit()
def sanitize_movie_data(movie_data):
    # Convert 'N/A', None, or empty strings to None or a default value
    def to_float(value, default=0.0):
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    movie_data['imdb_score'] = to_float(movie_data.get('imdb_score', 'N/A'))
    movie_data['box_office'] = to_float(movie_data.get('box_office', 'N/A'))
    movie_data['tomato_meter'] = to_float(movie_data.get('tomato_meter', 'N/A'))
    movie_data['popcorn_meter'] = to_float(movie_data.get('popcorn_meter', 'N/A'))

    return movie_data
def update_all_box_office():
    db_manager = DatabaseManager()
    movies = db_manager.get_all_movies()
    for movie in movies:
        if float(movie.box_office) == 0 or movie.box_office is None:
            movie.box_office = omdb_api.get_box_office_from_omdb(omdb_api.Master_api_key, movie.title)
            db_manager.add_or_update_box_office(movie.title, movie.box_office)
            print(f"Updated box office for {movie.title}")
    import time
def update_roles(actor_name):
    db_manager = DatabaseManager()
    movies = scrape_actor_data(actor_name)
    if not movies:
        return
    for movie in movies:
        db_manager.add_or_update_role(actor_name, movie[1], movie[4])
    # Add a short delay to avoid overwhelming the API
    # Implement a simple rate limiting mechanism
    from time import time

    # Define rate limit: 1 request per second
    RATE_LIMIT = 0.5
    last_request_time = 0

    current_time = time()
    time_since_last_request = current_time - last_request_time
    if time_since_last_request < RATE_LIMIT:
        time_to_wait = RATE_LIMIT - time_since_last_request
        time.sleep(time_to_wait)
    
    last_request_time = time()


def update_birthdate(actor_name):
    db_manager = DatabaseManager()
    actor = db_manager.get_actor_by_name(actor_name)
    if not actor or actor.birth_date is not None:
        return
    birthdate = get_actor_birthdate(actor_name)
    if birthdate:
        print(f"Updating birthdate for {actor_name}: {birthdate}")
        db_manager.update_birthdate(actor_name, birthdate)
        
    else:
        print(f"Failed to get birthdate for {actor_name}")
    # Add a short delay to avoid overwhelming the API
    # Implement a simple rate limiting mechanism
    from time import time

    # Define rate limit: 1 request per second
    RATE_LIMIT = 0.5
    last_request_time = 0

    current_time = time()
    time_since_last_request = current_time - last_request_time
    if time_since_last_request < RATE_LIMIT:
        time_to_wait = RATE_LIMIT - time_since_last_request
        time.sleep(time_to_wait)
    
    last_request_time = time()

def scrape_actor_data_and_add_to_db(db_manager,actor_name):
    movies = scrape_actor_data(actor_name)
    data = scrape_movie_list(movies)
    db_manager.add_or_update_movie(**data)


def scrape_movie_list(movies):
    movies = [(movie[0], format_movie_title(movie[1]), movie[2], movie[3], movie[4]) for movie in movies]
    for movie in movies:
        movie_data = omdb_api.get_movie_data(omdb_api.Master_api_key, movie[1])
        print(movie_data)
        poster_path = omdb_api.download_movie_posters(omdb_api.Master_api_key, movie[1],config.POSTER_OUTPUT_FOLDER)

        # Combine movie data from OMDB and scraped data
        combined_movie_data = {
            'title': movie_data.get('Title', movie[1]),
            'genre': movie_data.get('Genre'),
            'director': movie_data.get('Director'),
            'release_date': movie_data.get('Released'),
            'runtime': movie_data.get('Runtime'),
            'mpaa_rating': movie_data.get('Rated'),
            'synopsis': movie_data.get('Plot'),
            'imdb_score': movie_data.get('imdbRating'),
            'box_office': movie_data.get('BoxOffice'),
            'awards': movie_data.get('Awards'),
            'tomato_meter': movie[2],
            'popcorn_meter': movie[3],
            'actors': movie_data.get('Actors'),
            'role': movie[4],
            'actor_name': name,
            'poster_path': poster_path
        }

        # Sanitize the movie data
        return sanitize_movie_data(combined_movie_data)
def update_movie_list(movies):
    movies = [(movie[0], format_movie_title(movie[1]), movie[2], movie[3], movie[4]) for movie in movies]
    for movie in movies:
        movie_data = omdb_api.get_movie_data(omdb_api.Master_api_key, movie[1])
        print(movie_data)
        poster_path = omdb_api.download_movie_posters(omdb_api.Master_api_key, movie[1],config.POSTER_OUTPUT_FOLDER)

        # Combine movie data from OMDB and scraped data
        combined_movie_data = {
            'title': movie_data.get('Title', movie[1]),
            'genre': movie_data.get('Genre'),
            'director': movie_data.get('Director'),
            'release_date': movie_data.get('Released'),
            'runtime': movie_data.get('Runtime'),
            'mpaa_rating': movie_data.get('Rated'),
            'synopsis': movie_data.get('Plot'),
            'imdb_score': movie_data.get('imdbRating'),
            'box_office': movie_data.get('BoxOffice'),
            'awards': movie_data.get('Awards'),
            'tomato_meter': movie[2],
            'popcorn_meter': movie[3],
            'actors': movie_data.get('Actors'),
            'role': movie[4],
            'actor_name': name,
            'poster_path': poster_path
        }

        # Sanitize the movie data
        return sanitize_movie_data(combined_movie_data)
def format_movie_title(title):
# Remove any subtitle after a colon
    title = title.split(':')[0].strip()

    # Remove common suffixes
    suffixes_to_remove = [
    "25th Anniversary Edition",
    "20th Anniversary Edition",
    "10th Anniversary Edition",
    "Special Edition",
    "Director's Cut",
    "Extended Cut",
    "Remastered",
    "Re-release"
    ]

    for suffix in suffixes_to_remove:
        if title.lower().endswith(suffix.lower()):
            title = title[:-(len(suffix) + 1)].strip()

    # Remove year in parentheses at the end
    if title.endswith(')'):
        last_open_paren = title.rfind('(')
        if last_open_paren != -1:
            year_part = title[last_open_paren:]
            if year_part[1:-1].isdigit() and len(year_part) == 6:
                title = title[:last_open_paren].strip()

    # Remove extra spaces
    title = ' '.join(title.split())

    return title
       
if __name__ == "__main__":
    db_manager = DatabaseManager()
    # update_all_box_office()
    failed_actors = [
    "Daniel Day Lewis",
    ]
    # resize_root_poster_folder("movie_posters")
    export_actors_list = [
    # "Al Pacino",
    # "Alan Tudyk",
    # "Amy Adams",
    # # "Anthony Hopkins",
    # "Brad Pitt",
    # # "Cate Blanchett",
    # "Charlize Theron",
    # "Christian Bale",
    "Denzel Washington",
    # "Dwayne Johnson",
    # "Emma Stone",
    # "Gary Oldman",
    # # "George Clooney",
    # "Jennifer Lawrence",
    # "Joaquin Phoenix",
    # # "Julia Roberts",
    # "Kate Winslet",
    # # "Kevin Hart",
    # # "Leonardo DiCaprio",
    # "Matt Damon",   
    # "Matthew McConaughey",
    # # "Meryl Streep",
    # "Michael Fassbender",
    # "Natalie Portman",
    # # "Nicole Kidman",
    # # "Robert De Niro",
    # "Scarlett Johansson",
    # # "Sean Penn",
    # "Tom Cruise",
    # "Tom Hanks",
    # # "Viola Davis",
    # "Ryan Gosling",
    "Ryan Reynolds",
    ]
    actors = [
    "Tom Hardy",
    "Alan Tudyk",
    "Dwayne Johnson",
    "Kevin Hart",
    "matthew mcconaughey",
    "Andy Serkis",
    "Tom Hardy",
    "Meryl Streep",
    "Tom Hanks",
    "Denzel Washington",
    "Cate Blanchett",
    "Morgan Freeman",
    "Viola Davis",
    "Anthony Hopkins",
    "Nicole Kidman",
    "Al Pacino",
    "Judi Dench",
    "Charlize Theron",
    "Frances McDormand",
    "Robert De Niro",
    "Joaquin Phoenix",
    "Helen Mirren",
    "Gary Oldman",
    "Kate Winslet",
    "Christian Bale",
    "Meryl Streep",
    "Mahershala Ali",
    "Olivia Colman",
    "Samuel L Jackson",
    "Emma Thompson",
    "Brad Pitt",
    "Natalie Portman",
    "Ian McKellen",
    "Tilda Swinton",
    "Dustin Hoffman",
    "Saoirse Ronan",
    "Philip Seymour Hoffman",
    "Maggie Smith",
    "Jack Nicholson",
    "Julianne Moore",
    "Willem Dafoe",
    "Cate Blanchett",
    "Bryan Cranston",
    "Javier Bardem",
    "Octavia Spencer"
    ]
    # export_actor_speedrun("Bryan Cranston", "Bryan Cranston Speedrun.csv")
    export_actors = True
    # export_actors = False
    # Initialize the database manager
    db_manager = DatabaseManager()

    # Create a new list to store actors with more than 3 movies
    export_actors_list_adjusted = []

    for actor_name in export_actors_list:
        # Get the movies for this actor
        movies = db_manager.get_character_movies_by_actor(actor_name)
        
        # If the actor has more than 3 movies, add them to the export list
        if movies and len(movies) > 3:
            export_actors_list_adjusted.append(actor_name)
        else:
            print(f"{actor_name} has 3 or fewer movies and will not be exported.")

    print(f"Number of actors to be exported: {len(export_actors_list)}")
    if export_actors:
        csv_exporter.export_actors(export_actors_list_adjusted, f"Actor_Speedruns.csv")
    for name in export_actors_list:
        update_birthdate(name)
    # db_actors = db_manager.get_all_actors()
    # for actor in db_actors:
    #     if actor.name in failed_actors:
    #         continue
    #     update_roles(actor.name)
    for name in actors:
        # existing_actor = db_manager.session.query(Actor).filter_by(name=name).first()
        # if existing_actor and existing_actor.movie_roles:
        #     continue
        # update_roles(name)


        scrape_actors = False
        if scrape_actors:
            if db_manager.has_roles(name):
                print(f"{name} already has roles")
                continue
            else:
                scrape_actor_data_and_add_to_db(db_manager,name)
            

           
    
