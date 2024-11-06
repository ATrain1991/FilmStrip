import base64
import csv
import datetime
import os  
from numerize import numerize
import cpi
from HelperMethods import get_float_from_box_office
from databaseManager import DatabaseManager
from models import noDB_actor, noDB_movie

def get_movie_header(preface):
    return [f"{preface} Title", f"{preface} poster", f"{preface} Tmeter", f"{preface} Tmeter Icon", f"{preface} Pmeter", f"{preface} Pmeter Icon", f"{preface} Box Office"]
def safe_get_year(movie):
    current_year = datetime.datetime.now().year
    year = movie.get_release_year()
    return int(year) if year and year.isdigit() and int(year) < current_year else current_year
def get_Actor_Data(db_manager,movies):
    current_year = datetime.datetime.now().year 

    total_box_office = sum([
        get_float_from_box_office(movie.box_office) if safe_get_year(movie) >= current_year else
        cpi.inflate(
            get_float_from_box_office(movie.box_office),
            safe_get_year(movie),
        ) 
        for movie in movies if movie.box_office
    ])
    movies_with_box_office = [movie for movie in movies if get_float_from_box_office(movie.box_office) > 0]
    average_tomatometer = round(sum([movie.tomato_meter for movie in movies_with_box_office if movie.tomato_meter]) / len(movies_with_box_office)) if movies_with_box_office else 0
    average_popcornmeter = round(sum([movie.popcorn_meter for movie in movies_with_box_office if movie.popcorn_meter]) / len(movies_with_box_office)) if movies_with_box_office else 0
    highest_tomatometer_movie = max(movies_with_box_office, key=lambda movie: movie.tomato_meter) if movies_with_box_office else None
    highest_popcornmeter_movie = max(movies_with_box_office, key=lambda movie: movie.popcorn_meter) if movies_with_box_office else None
    lowest_tomatometer_movie = min(movies_with_box_office, key=lambda movie: movie.tomato_meter) if movies_with_box_office else None
    lowest_popcornmeter_movie = min(movies_with_box_office, key=lambda movie: movie.popcorn_meter) if movies_with_box_office else None
    highest_box_office_movie = max(movies, key=lambda movie: 
        get_float_from_box_office(movie.box_office) if safe_get_year(movie) >= current_year else
        cpi.inflate(
            get_float_from_box_office(movie.box_office),
            safe_get_year(movie)
        )
    )
    
    return total_box_office, average_tomatometer, average_popcornmeter, highest_tomatometer_movie, highest_box_office_movie, highest_popcornmeter_movie, lowest_tomatometer_movie, lowest_popcornmeter_movie

def writeHeader(writer):
    # writer.writerow(['Actor Name', 'Age','birthdate','oscar wins','oscar nominations','Actor Portrait', 'Total Box Office Earnings (Adjusted for Inflation)', 'Average Tomatometer', 'Average Popcornmeter',                    
    #                  'Highest Tomatometer Movie', 'Highest Tomatometer Movie Poster','Highest Tomatometer', 'Highest Tomatometer Tomatometer Path', 'Highest Tomatometer Popcornmeter', 'Highest Tomatometer Popcornmeter Icon', 'Highest Tomatometer Box Office',
    #                  'Highest Box Office Movie', 'Highest Box Office Movie Poster','Highest Box Office Tomatometer', 'Highest Box Office Tomatometer Path', 'Highest Box Office Popcornmeter', 'Highest Box Office Popcornmeter Path', 'Highest Box Office Box Office',
    #                  'Highest Popcornmeter Movie', 'Highest Popcornmeter Movie Poster','Highest Popcornmeter Tomatometer', 'Highest Popcornmeter Tomatometer path', 'Highest PopcornMeter Tomatometer Image' 'Highest Popcornmeter', 'Highest Popcornmeter Icon', 'Highest popcornMeter popcornMeter Image' 'Highest Popcornmeter Box Office',
    #                  ])
    writer.writerow(['Actor Name', 'Age', 'birthdate', 'oscar wins', 'oscar nominations', 'Actor Portrait', 
                        'Total Box Office Earnings (Adjusted for Inflation)', 'Average Tomatometer', 'Average Popcornmeter'] +
                    get_movie_header('Highest Tomatometer') +
                    get_movie_header('Highest Box Office') +
                    get_movie_header('Highest Popcornmeter') +
                    get_movie_header('Lowest Tomatometer') +
                    get_movie_header('Lowest Popcornmeter'))
    return writer
    
def get_movie_data(movie):
    if movie is None:
        return None
    current_year = datetime.datetime.now().year 
    return [
        movie.title,
        '',
        movie.tomato_meter,
        'FreshTomato.png' if movie.tomato_meter >= 60 else 'RottenTomato.png',
        '',
        movie.popcorn_meter,
        'FreshPopcorn.png' if movie.popcorn_meter >= 60 else 'RottenPopcorn.png',
        '',
        '$' + numerize.numerize(get_float_from_box_office(movie.box_office) if safe_get_year(movie) >= current_year else cpi.inflate(get_float_from_box_office(movie.box_office), safe_get_year(movie)))
    ]

# def write_actor_data(writer,actor,total_box_office, average_tomatometer, average_popcornmeter, highest_tomatometer_movie, highest_box_office_movie, highest_popcornmeter_movie):
#     writer.writerow([
#         actor.name,
#         actor.get_age(),
#         actor.birth_date,
#         actor.oscars_wins,
#         actor.oscars_nominations,
#         actor.portrait_path,
#         '$' + numerize.numerize(total_box_office),
#         average_tomatometer,
#         average_popcornmeter,
#         *get_movie_data(highest_tomatometer_movie),
#         *get_movie_data(highest_box_office_movie),
#         *get_movie_data(highest_popcornmeter_movie)
#     ])
#     return writer

def export_actor_speedrun(actor_name, output_file, writeHeader=True):
    db_manager = DatabaseManager()
    actor = db_manager.get_actor_by_name(actor_name)
    
    if not actor:
        print(f"Actor {actor_name} not found in the database.")
        return None

    movies = db_manager.get_character_movies_by_actor(actor_name)
    
    if not movies:
        print(f"No movies found for actor {actor_name}.")
        return None
    
    total_box_office, average_tomatometer, average_popcornmeter, highest_tomatometer_movie, highest_box_office_movie, highest_popcornmeter_movie, lowest_tomatometer_movie, lowest_popcornmeter_movie = get_Actor_Data(db_manager, movies)

    actor_data = [
        actor.name,
        actor.get_age(),
        actor.birth_date,
        actor.oscars_wins,
        actor.oscars_nominations,
        "insert actor image column",# actor.portrait_path,
        '$' + numerize.numerize(total_box_office),
        average_tomatometer,
        average_popcornmeter,
        *get_movie_data(highest_tomatometer_movie),
        *get_movie_data(highest_box_office_movie),
        *get_movie_data(highest_popcornmeter_movie),
        *get_movie_data(lowest_tomatometer_movie),
        *get_movie_data(lowest_popcornmeter_movie)
    ]

    if writeHeader:
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer = writeHeader(writer)
            writer.writerow(actor_data)
        return None
    else:
        return actor_data

def export_actors(actors, output_file):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer = writeHeader(writer)
        for actor in actors:
            actor_data = export_actor_speedrun(actor, output_file, False)
            if actor_data:
                writer.writerow(actor_data)




#noDB_get_Actor_Data


def noDB_get_movie_data(movie: noDB_movie):
    if movie is None:
        return None
    return [
        movie.title,
        '',
        movie.tomatometer,
        'FreshTomato.png' if movie.tomatometer >= 60 else 'RottenTomato.png',
        movie.popcornmeter,
        'FreshPopcorn.png' if movie.popcornmeter >= 60 else 'RottenPopcorn.png',
        '$' + numerize.numerize(movie.box_office)
    ]
#simplified version of get_Actor_Data that does not require a database manager
def noDB_get_Actor_Data(actor_obj : noDB_actor):
    total_box_office = actor_obj.get_total_box_office()
    average_tomatometer = actor_obj.get_average_tomatometer()
    average_popcornmeter = actor_obj.get_average_popcornmeter()
    highest_tomatometer_movie = actor_obj.get_critics_best_movie('tomatometer')
    highest_box_office_movie = actor_obj.get_highest_grossing_movie()
    highest_popcornmeter_movie = actor_obj.get_audience_best_movie('popcornmeter')
    lowest_tomatometer_movie = actor_obj.get_lowest_tomatometer_movie()
    lowest_popcornmeter_movie = actor_obj.get_lowest_popcornmeter_movie()
    return [total_box_office, average_tomatometer, average_popcornmeter, highest_tomatometer_movie, highest_box_office_movie, highest_popcornmeter_movie, lowest_tomatometer_movie, lowest_popcornmeter_movie]


def getHeader():
    return ['Name', 'Age', 'birthdate', 'oscar wins', 'oscar nominations', 'Actor Portrait', 
            'Box Office Earnings', 'Avg Tmeter', 'Avg Pmeter'] + \
            get_movie_header('Best Tmeter') + \
            get_movie_header('Best Box Office') + \
            get_movie_header('Best Pmeter') + \
            get_movie_header('Worst Tmeter') + \
            get_movie_header('Worst Pmeter')
# Function to export a single actor's data in a simplified format
def noDB_export_actor_speedrun(actor_obj : noDB_actor, output_file, writeHeader=True):
    # Check if the actor object is of the correct type
    # if not isinstance(actor_obj, noDB_actor):
    #     print("Actor object is not of type noDB_actor")
    #     return None
    
    # Get the actor's data
    total_box_office, average_tomatometer, average_popcornmeter, highest_tomatometer_movie, highest_box_office_movie, highest_popcornmeter_movie, lowest_tomatometer_movie, lowest_popcornmeter_movie = noDB_get_Actor_Data(actor_obj)
    
    # Prepare the actor's data for writing
    actor_data = [
        actor_obj.name,
        actor_obj.age,
        actor_obj.birthdate,
        actor_obj.oscar_wins,
        actor_obj.oscar_nominations,
        '',  # Placeholder for actor portrait
        '$' + numerize.numerize(total_box_office),
        round(average_tomatometer),
        round(average_popcornmeter)
    ]
    
    # Add data for each movie category
    for movie in [highest_tomatometer_movie, highest_box_office_movie, highest_popcornmeter_movie, lowest_tomatometer_movie, lowest_popcornmeter_movie]:
        actor_data.extend(noDB_get_movie_data(movie))
    
    # Write the header and data if writeHeader is True
    if writeHeader:
        with open(output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(getHeader())
            writer.writerow(actor_data)
        return None
    else:
        return actor_data

def export_actor_full(actor_obj, output_file):
    if not isinstance(actor_obj, noDB_actor):
        print("Actor object is not of type noDB_actor")
        return None
    actor_data = noDB_get_Actor_Data(actor_obj)
    # Check if the file exists and has content
    file_exists = os.path.isfile(output_file) and os.path.getsize(output_file) > 0

    mode = 'a' if file_exists else 'w'
    with open(output_file, mode=mode, newline='') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            # Write header if the file is new
            writer = writeHeader(writer)
        else:
            # Check if the file has at least two rows (header + entry)
            file.seek(0)
            reader = csv.reader(file)
            row_count = sum(1 for row in reader)
            
            if row_count >= 2:
                # Add a blank row if file has header and at least one entry
                writer.writerow([])
        if actor_data:
            writer.writerow(actor_data)