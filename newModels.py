from datetime import datetime
from logging import config
import os
import cpi
import cv2
from dotenv import load_dotenv
from HelperMethods import get_float_from_box_office, inflation_safe_year
from ImageManager import PlaceText,PlaceImage,overlay_images_and_text
from config import (OMDB_API_KEY,POSTER_X, POSTER_Y, POSTER_WIDTH, POSTER_HEIGHT,
                   
                   YEAR_X, YEAR_Y, YEAR_SCALE, YEAR_THICKNESS,
                   BOX_OFFICE_X, BOX_OFFICE_Y, BOX_OFFICE_SCALE, BOX_OFFICE_THICKNESS,
                   SCORE_X_TOMATO, SCORE_X_POPCORN, SCORE_Y, SCORE_SCALE, SCORE_THICKNESS,
                   ACTOR_AGE_X, ACTOR_AGE_Y, ACTOR_AGE_SCALE, ACTOR_AGE_THICKNESS,
                   BIRTHDATE_X, BIRTHDATE_Y, BIRTHDATE_SCALE, BIRTHDATE_THICKNESS,
                   TEXT_COLOR_BLACK, TEXT_COLOR_WHITE, DEFAULT_FONT)
import omdb_api










class Movie:
    def __init__(self, name, year, box_office, poster_path,tomatometer:float,popcornmeter:float):
        self.name = name
        self.year = PlaceText(text=year, x=YEAR_X, y=YEAR_Y, scale=YEAR_SCALE, thickness=YEAR_THICKNESS,color=TEXT_COLOR_BLACK)
        self.box_office = PlaceText(text=box_office, x=BOX_OFFICE_X, y=BOX_OFFICE_Y, scale=BOX_OFFICE_SCALE, thickness=BOX_OFFICE_THICKNESS,color=TEXT_COLOR_BLACK)
        self.poster = PlaceImage(poster_path, x=POSTER_X, y=POSTER_Y, width=POSTER_WIDTH, height=POSTER_HEIGHT)
        self.tomato_meter = Meter(MeterType.TOMATO, tomatometer)
        self.popcorn_meter = Meter(MeterType.POPCORN, popcornmeter)
    def get_tomato_meter_Image_tuple(self):
        return self.tomato_meter.get_image_tuple()
    def get_popcorn_meter_Image_tuple(self):
        return self.popcorn_meter.get_image_tuple()
    def get_tomato_meter_Text_tuple(self):
        return self.tomato_meter.get_text_tuple()
    def get_popcorn_meter_Text_tuple(self):
        return self.popcorn_meter.get_text_tuple()
    def get_movie_image(self):
            current_dir = os.path.dirname(os.path.abspath(__file__))
            background_image = os.path.join(current_dir, "icons", "film_strip.png")
            # Load background image
            background = cv2.imread(background_image)
            if background is None:
                raise ValueError(f"Could not load background image from {background_image}")
                
            # Get image and text tuples from movie
            images = [
                self.poster.get_tuple(),  # Movie poster image
                self.get_tomato_meter_Image_tuple(),  # Tomato meter icon
                self.get_popcorn_meter_Image_tuple()   # Popcorn meter icon
            ]
            
            texts = [
                self.year.get_tuple(),         # Year text
                self.box_office.get_tuple(),   # Box office text
                self.get_tomato_meter_Text_tuple(),  # Tomato score text
                self.get_popcorn_meter_Text_tuple()   # Popcorn score text
            ]
            
        # Overlay movie content onto background
            result = overlay_images_and_text(background, images, texts)
        
            return result
