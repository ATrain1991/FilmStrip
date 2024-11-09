from enum import Enum
import os
import cv2

# Define the enum
class MeterType(Enum):
    TOMATO = 1
    POPCORN = 2

# Simplify the Meter class for testing
class Meter:
    def __init__(self, meter_type, score):
        # Print debug info
        print(f"Debug - Received meter_type: {meter_type}")
        print(f"Debug - Type of meter_type: {type(meter_type)}")
        print(f"Debug - MeterType.TOMATO: {MeterType.TOMATO}")
        print(f"Debug - Type of MeterType.TOMATO: {type(MeterType.TOMATO)}")
        print(f"Debug - Are they equal? {meter_type == MeterType.TOMATO}")
        
        self.meter_type = meter_type
        self.score = score
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        if meter_type == MeterType.TOMATO:
            self.image_path = os.path.join(current_dir, "icons", "FreshTomato.png")
            self.x = 156
        else:
            self.image_path = os.path.join(current_dir, "icons", "FreshPopcorn.png")
            self.x = 626
            
        self.y = 1510
        self.width = 300
        self.height = 300
    
    def get_image_tuple(self):
        return (self.image_path, self.x, self.y, self.width, self.height)
    
    def get_text_tuple(self):
        text = f"{self.score}%"
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "RozhaOne-Regular.ttf")
        font = cv2.FONT_HERSHEY_SIMPLEX # Fallback to default font if custom font fails
        try:
            font = cv2.freetype.createFreeType2()
            font.loadFontData(font_path, 0)
        except:
            print(f"Warning: Could not load custom font from {font_path}")
        if self.meter_type == MeterType.TOMATO:
            return (text, 200, 1840, 1.0, (255,255,255), font, 6)
        else:
            return (text, 670, 1840, 1.5, (255,255,255), font, 7)

class Poster:
    def __init__(self, path, x, y, width, height):
        self.poster_path = path
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_poster_tuple(self):
        return (self.poster_path, self.x, self.y, self.width, self.height)

class Movie:
    def __init__(self, poster: Poster, tmeter: Meter, pmeter: Meter, year: str, box_office: str):
        self.poster = poster
        self.tmeter = tmeter
        self.pmeter = pmeter
        self.year = year
        self.box_office = box_office
        
    def get_poster_tuple(self):
        return self.poster.get_poster_tuple()

    def get_year_tuple(self):
        return (self.year, 170, 90, 1.0, (0,0,0), cv2.FONT_HERSHEY_SIMPLEX, 5)

    def get_box_office_tuple(self):
        return (self.box_office, 696, 90, 1.0, (0,0,0), cv2.FONT_HERSHEY_SIMPLEX, 5)
        
    def get_tmeter_tuple(self):
        return self.tmeter.get_image_tuple()
        
    def get_pmeter_tuple(self):
        return self.pmeter.get_image_tuple()
        
    def get_tmeter_text_tuple(self):
        return self.tmeter.get_text_tuple()
        
    def get_pmeter_text_tuple(self):
        return self.pmeter.get_text_tuple()

