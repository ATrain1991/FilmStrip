import os
import numerize
from numerize import numerize as n

def numerize_value(value):
    print(f"Debug - Original value: {value}")
    print(f"Debug - Type of value: {type(value)}")
    
    try:
        if not value or value == "N/A":
            return "N/A"
            
        cleaned_value = str(value).replace("$", "").replace(",", "")
        print(f"Debug - Cleaned value: {cleaned_value}")
        
        try:
            float_value = float(cleaned_value)
            print(f"Debug - Float value: {float_value}")
            result = n(float_value, 1)
            print(f"Debug - Numerized result: {result}")
            return result
        except ValueError as ve:
            print(f"Debug - ValueError: {ve}")
            return value
            
    except Exception as e:
        print(f"Debug - Exception: {e}")
        return str(value)

class noDB_actor:
    def __init__(self, name, age, birthdate, oscar_wins, oscar_nominations, movies):
        self.name = name
        self.age = age
        self.birthdate = birthdate
        self.oscar_wins = oscar_wins
        self.oscar_nominations = oscar_nominations
        self.movies = movies

    def get_critics_best_movie(self, type):
        if type == "tomatometer":
            return max(self.movies, key=lambda x: x.tomatometer)
    def get_audience_best_movie(self, type):
        if type == "popcornmeter":
            return max(self.movies, key=lambda x: x.popcornmeter)
    def get_highest_grossing_movie(self):
        return max(self.movies, key=lambda x: x.box_office)
    def get_lowest_tomatometer_movie(self):
        return min(self.movies, key=lambda x: x.tomatometer)
    def get_lowest_popcornmeter_movie(self):
        return min(self.movies, key=lambda x: x.popcornmeter)
    def get_total_box_office(self):
        return sum(movie.box_office for movie in self.movies)
    def get_average_tomatometer(self):
        return round(sum(movie.tomatometer for movie in self.movies) / len(self.movies))
    def get_average_popcornmeter(self):
        return round(sum(movie.popcornmeter for movie in self.movies) / len(self.movies))
    def get_main_image_path(self):
        name_ = self.name.replace(" ", "_")
        return os.path.join(self.name, f"{name_}.jpg")
    def NumerizeTotalBoxOffice(self):
        return numerize_value(self.get_total_box_office())

class noDB_movie:
    def __init__(self, title, year, tomatometer, popcornmeter, box_office, role):
        self.title = title
        self.year = year
        self.tomatometer = tomatometer
        self.popcornmeter = popcornmeter
        self.box_office = box_office
        self.role = role
    def NumerizeBoxOffice(self):
        return numerize_value(self.box_office)