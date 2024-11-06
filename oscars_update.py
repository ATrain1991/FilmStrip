from databaseManager import DatabaseManager
from databaseModels import Actor

def update_actor_oscars(actor_name):
    db_manager = DatabaseManager()
    
    actor = db_manager.get_actor_by_name(actor_name)
    
    if not actor:
        print(f"Actor {actor_name} not found in the database.")
        return
    
    oscars_wins = input(f"Enter the number of Oscar wins for {actor_name}: ")
    oscars_nominations = input(f"Enter the number of Oscar nominations for {actor_name}: ")
    
    try:
        oscars_wins = int(oscars_wins)
        oscars_nominations = int(oscars_nominations)
    except ValueError:
        print("Please enter valid integer values for Oscar wins and nominations.")
        return
    
    db_manager.update_oscars(actor.name, oscars_wins, oscars_nominations)
    print(f"Oscar information updated for {actor_name}.")

if __name__ == "__main__":
    export_actors_list = [
    "Al Pacino",
    "Alan Tudyk",
    "Amy Adams",
    "Anthony Hopkins",
    "Brad Pitt",
    "Cate Blanchett",
    "Charlize Theron",
    "Christian Bale",
    "Denzel Washington",
    "Dwayne Johnson",
    "Emma Stone",
    "Gary Oldman",
    "George Clooney",
    "Jennifer Lawrence",
    "Joaquin Phoenix",
    "Julia Roberts",
    "Kate Winslet",
    "Kevin Hart",
    "Leonardo Di Caprio",
    "Matt Damon",   
    "Matthew McConaughey",
    "Meryl Streep",
    "Michael Fassbender",
    "Natalie Portman",
    "Nicole Kidman",
    "Robert De Niro",
    "Scarlett Johansson",
    "Sean Penn",
    "Tom Cruise",
    "Tom Hanks",
    "Viola Davis",
    "Ryan Gosling",
    "Ryan Reynolds",
    ]
    for name in export_actors_list:
        update_actor_oscars(name)
