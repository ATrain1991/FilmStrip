import os
from venv import logger
from PyQt6.QtWidgets import QApplication, QWidget
import sys
from PyQt6.QtCore import QTimer
import Film_Strip
from VideoManager import DEBUG
from film_strip_generator import FilmStripWidget
from Film_Strip import FilmStrip
from models import noDB_actor
from single_actor_full import generate_actor_object
from video_manager import VideoManager
from pydub import AudioSegment

ICON_DIR = "icons"
fresh_T_meter_icon = os.path.join(ICON_DIR, "FreshTomato.png")
fresh_P_meter_icon = os.path.join(ICON_DIR, "FreshPopcorn.png")
rotten_T_meter_icon = os.path.join(ICON_DIR, "RottenTomato.png") 
rotten_P_meter_icon = os.path.join(ICON_DIR, "RottenPopcorn.png")
box_office_icon = os.path.join(ICON_DIR, "box_office.png")

# Audio paths
current_dir = os.path.dirname(os.path.abspath(__file__))
soundclips_dir = os.path.join(current_dir, "soundclips")
ffmpeg_path = os.path.join(current_dir, "ffmpeg.exe")
ffprobe_path = os.path.join(current_dir, "ffprobe.exe")

# Configure audio settings
AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path 
AudioSegment.ffprobe = ffprobe_path

# Soundclip paths
CLIPS_DIR = soundclips_dir
best_critic_movie_clip = os.path.join(CLIPS_DIR, "CriticsFavorite.wav")
best_audience_movie_clip = os.path.join(CLIPS_DIR, "AudienceFavorite.wav")
highest_grossing_movie_clip = os.path.join(CLIPS_DIR, "MostSuccessful.wav")
worst_tomatometer_movie_clip = os.path.join(CLIPS_DIR, "CriticsLeastFavorite.wav")
worst_popcornmeter_movie_clip = os.path.join(CLIPS_DIR, "AudienceLeastFavorite.wav")

def get_sub_images(movie):
    """Get sub-images and scores for a movie poster"""
    try:
        box_office = movie.NumerizeBoxOffice()
        return [
            (fresh_T_meter_icon if float(movie.tomatometer) > 60.0 else rotten_T_meter_icon, f"{movie.tomatometer}%", 60),
            (fresh_P_meter_icon if float(movie.popcornmeter) > 60.0 else rotten_P_meter_icon, f"{movie.popcornmeter}%", 60),
            (box_office_icon, str(box_office), 45)
        ]
    except Exception as e:
        if DEBUG:
            logger.error(f"Error in get_sub_images: {e}")
        return []

def get_actor_sub_images(actor:noDB_actor):
    """Get sub-images and scores for actor summary poster"""
    try:
        box_office = actor.NumerizeTotalBoxOffice()
        avg_tmeter = actor.get_average_tomatometer()
        avg_pmeter = actor.get_average_popcornmeter()
        
        return [
            (fresh_T_meter_icon if avg_tmeter > 60.0 else rotten_T_meter_icon, f"{avg_tmeter}%", 60),
            (fresh_P_meter_icon if avg_pmeter > 60.0 else rotten_P_meter_icon, f"{avg_pmeter}%", 60),
            (box_office_icon, box_office, 45)
        ]
    except Exception as e:
        if DEBUG:
            logger.error(f"Error in get_actor_sub_images: {e}")
        return []

def create_actor_posters(actor:noDB_actor):
    """Create poster components for an actor's movies"""
    best_critic_movie = actor.get_critics_best_movie("tomatometer")
    best_audience_movie = actor.get_audience_best_movie("popcornmeter") 
    highest_grossing_movie = actor.get_highest_grossing_movie()
    worst_tomatometer_movie = actor.get_lowest_tomatometer_movie()
    worst_popcornmeter_movie = actor.get_lowest_popcornmeter_movie()

    poster_movies = [
        (best_critic_movie, best_critic_movie_clip),
        (highest_grossing_movie, highest_grossing_movie_clip),
        (best_audience_movie, best_audience_movie_clip),
        (worst_tomatometer_movie, worst_tomatometer_movie_clip),
        (worst_popcornmeter_movie, worst_popcornmeter_movie_clip)
    ]
    
    film_strip_components = []
    for movie, soundbite in poster_movies:
        try:
            main_img = os.path.join(actor.name, f"{movie.title.replace(' ', '_').replace('/', '_').replace('?', '').replace(':', '')}.jpg")
            
            # Create FilmStrip instance
            strip = FilmStrip(
                poster_path=main_img,
                tomato_score=movie.tomatometer,
                popcorn_score=movie.popcornmeter,
                year=movie.year,
                box_office=movie.NumerizeBoxOffice()
            )
            strip.show()
            film_strip_components.append(strip)
            
        except Exception as e:
            if DEBUG:
                print(f"Error creating poster for {movie.title}: {e}")
            continue
            
    return film_strip_components




class FilmFrameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = FilmStrip()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create film strip with 6 frames using our custom frame widget
    def record_scroll(widget, duration_ms):
        """Record scrolling through widget for specified duration"""
        from PyQt6.QtCore import QTimer
        from PyQt6.QtTest import QTest
        
        # Calculate scroll increment based on duration
        scrollbar = widget.findChild(QWidget).verticalScrollBar()
        scroll_range = scrollbar.maximum()
        steps = duration_ms // 16  # 60fps
        increment = int(scroll_range / steps)  # Convert to integer
        
        # Scroll and record each frame
        for _ in range(steps):
            current = scrollbar.value()
            scrollbar.setValue(current + increment)
            QTest.qWait(16)  # Wait one frame
            
    # Define recording function
    def start_recording():
        record_scroll(film_strip, 5000)  # 5000ms = 5 seconds of scrolling
    
    # Create film strip widget
    actor = generate_actor_object("Will Smith", 2, 10)
    film_strip_components = create_actor_posters(actor)
    
    # Create the film strip widget
    film_strip = FilmStripWidget(width=1080, height=1920)
    
    # Add the film strips directly to the widget
    for component in film_strip_components:
        film_strip.layout().addWidget(component)
    
    # Start recording after 1 second delay
    QTimer.singleShot(1000, start_recording)
    film_strip.show()
    sys.exit(app.exec())
