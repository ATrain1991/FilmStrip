from enum import Enum
import os
import cv2

from cv_helper_methods import overlay_images_and_text

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
            self.image_path = os.path.join(current_dir, "icons", "FreshTomato.png") if score > 60 else os.path.join(current_dir, "icons", "RottenTomato.png")
            self.x = 156  # X position of tomato meter icon
        else:
            self.image_path = os.path.join(current_dir, "icons", "FreshPopcorn.png") if score > 60 else os.path.join(current_dir, "icons", "RottenPopcorn.png")
            self.x = 626  # X position of popcorn meter icon
            
        self.y = 1515  # Y position of meter icons
        self.width = 300  # Width of meter icons
        self.height = 295  # Height of meter icons
    
    def get_image_tuple(self):
        image_path = self.image_path
        # Load and crop the top 5 pixels from the meter image
        img = cv2.imread(image_path)
        if img is not None:
            img = img[5:, :] # Remove top 5 pixels
            # Save cropped image to temp file with same name
            cv2.imwrite(image_path, img)
        # Returns (image_path, x_pos, y_pos, width, height) for meter icon
        return (self.image_path, self.x, self.y, self.width, self.height)
    
    def get_text_tuple(self):
        # Format score text
        text = f"{self.score}%"
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(current_dir, "fonts", "RozhaOne-Regular.ttf")
        font = cv2.FONT_HERSHEY_SIMPLEX  # Fallback font
        try:
            if not os.path.exists(font_path):
                raise FileNotFoundError(f"Font file not found: {font_path}")
                
            font = cv2.freetype.createFreeType2()
            font.loadFontData(font_path, 0)
        except Exception as e:
            print(f"Error loading font: {str(e)}")
            
        y_pos = 1890
        scale = 4
        thickness = 15
        if self.meter_type == MeterType.TOMATO:
            x_pos = 200
        else:
            x_pos = 670
        return (text, x_pos, y_pos, scale, (255,255,255), font, thickness)

class Poster:
    def __init__(self, path, x, y, width, height):
        self.poster_path = path
        self.x = x  # X position of movie poster
        self.y = y  # Y position of movie poster  
        self.width = width  # Width of movie poster
        self.height = height  # Height of movie poster

    def get_poster_tuple(self):
        # Returns (image_path, x_pos, y_pos, width, height) for movie poster
        return (self.poster_path, self.x, self.y, self.width, self.height)

class Movie:
    def __init__(self, title: str, poster_path: str, tmeter: Meter, pmeter: Meter, year: str, box_office: str):
        self.title = title
        self.poster = Poster(poster_path, 156, 144, 770, 1365)   
        self.tmeter = tmeter
        self.pmeter = pmeter
        self.year = year
        self.box_office = box_office
        
    def get_poster_tuple(self):
        # Returns poster image tuple from Poster class
        return self.poster.get_poster_tuple()

    def get_year_tuple(self):
        # Returns (text, x_pos, y_pos, scale, color, font, thickness) for year text
        return (self.year, 170, 100, 2.4, (0,0,0), cv2.FONT_HERSHEY_SIMPLEX, 6)

    def get_box_office_tuple(self):
        # Returns (text, x_pos, y_pos, scale, color, font, thickness) for box office text
        return (f"${self.box_office}", 696, 100, 2.0, (0,0,0), cv2.FONT_HERSHEY_SIMPLEX, 6)
        
    def get_tmeter_tuple(self):
        # Returns tomato meter image tuple from Meter class
        return self.tmeter.get_image_tuple()
        
    def get_pmeter_tuple(self):
        # Returns popcorn meter image tuple from Meter class
        return self.pmeter.get_image_tuple()
        
    def get_tmeter_text_tuple(self):
        # Returns tomato score text tuple from Meter class
        return self.tmeter.get_text_tuple()
        
    def get_pmeter_text_tuple(self):
        # Returns popcorn score text tuple from Meter class
        return self.pmeter.get_text_tuple()
        
    def get_movie_image(self):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            background_image = os.path.join(current_dir, "icons", "film_strip.png")
            # Load background image
            background = cv2.imread(background_image)
            if background is None:
                raise ValueError(f"Could not load background image from {background_image}")
                
            # Get image and text tuples from movie
            images = [
                self.get_poster_tuple(),  # Movie poster image
                self.get_tmeter_tuple(),  # Tomato meter icon
                self.get_pmeter_tuple()   # Popcorn meter icon
            ]
            
            texts = [
                self.get_year_tuple(),         # Year text
                self.get_box_office_tuple(),   # Box office text
                self.get_tmeter_text_tuple(),  # Tomato score text
                self.get_pmeter_text_tuple()   # Popcorn score text
            ]
            
        # Overlay movie content onto background
            result = overlay_images_and_text(background, images, texts)
        
            return result
