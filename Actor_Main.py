import sys
import cv2
import infograph_generator
from models import noDB_actor
from numerize import numerize
from PyQt6.QtWidgets import QApplication
from single_actor_full import generate_actor_object
import os
from PyQt6.QtCore import QTimer
import time
from pydub import AudioSegment
import PosterUI
import traceback
import logging
from VideoManager import VideoManager

# Configure logging
logger = logging.getLogger(__name__)
DEBUG = False

# Icon paths
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
        box_office = numerize.numerize(round(float(actor.get_total_box_office())))
        avg_tmeter = round(actor.get_average_tomatometer())
        avg_pmeter = round(actor.get_average_popcornmeter())
        
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
    
    poster_components = []
    for movie, soundbite in poster_movies:
        try:
            main_img = os.path.join(actor.name, f"{movie.title.replace(' ', '_').replace('/', '_').replace('?', '').replace(':', '')}.jpg")
            sub_images = get_sub_images(movie)
            if not sub_images:
                continue

            component = PosterUI.create_poster_component(
                main_img,
                sub_images_data=sub_images,
                soundbite_path=soundbite,
                year=movie.year
            )
            poster_components.append(component)
            
        except Exception as e:
            if DEBUG:
                logger.error(f"Error creating poster for {movie.title}: {e}")
            continue
            
    return poster_components

def convert_mp3_to_wav(mp3_path, wav_path):
    """Convert MP3 audio to WAV format"""
    try:
        sound = AudioSegment.from_mp3(mp3_path)
        sound.export(wav_path, format="wav")
    except Exception as e:
        if DEBUG:
            logger.error(f"Error converting {mp3_path}: {e}")
            logger.debug(traceback.format_exc())

def convert_all_soundclips():
    """Convert all MP3 soundclips to WAV format"""
    os.makedirs(soundclips_dir, exist_ok=True)
    
    for mp3_file in [f for f in os.listdir(soundclips_dir) if f.endswith('.mp3')]:
        mp3_path = os.path.join(soundclips_dir, mp3_file)
        wav_path = os.path.join(soundclips_dir, mp3_file.replace('.mp3', '.wav'))
        
        if not os.path.exists(wav_path):
            try:
                sound = AudioSegment.from_mp3(mp3_path)
                sound.export(wav_path, format="wav")
            except Exception as e:
                if DEBUG:
                    logger.error(f"Error converting {mp3_file}: {e}")

if __name__ == "__main__":
    convert_all_soundclips()

    try:
        app = QApplication(sys.argv)
        actor = generate_actor_object("Will Smith", 2, 10)
        posters = create_actor_posters(actor)
        
        window = infograph_generator.InfographGenerator()
        actor_sub_images = get_actor_sub_images(actor)
        actor_poster = PosterUI.create_poster_component(
            actor.get_main_image_path(),
            sub_images_data=actor_sub_images,
            soundbite_path="soundclips/CriticsFavorite.wav",
            year=f"{actor.birthdate}({actor.age})"
        )

        # Setup actor directory
        actor_dir = os.path.join(os.getcwd(), actor.name)
        os.makedirs(actor_dir, exist_ok=True)

        window.generateFullImage(posters, actor_poster)
        window.show()
        app.exec()
        VideoManager.create_scrolling_video(actor.get_main_image_path(), os.path.join(actor_dir, f"{actor.name}.mp4"))
        # window.generateScroller(posters, actor_poster)
        # window.show()
        
        # # Start recording and scrolling
        # QTimer.singleShot(1000, window.start_recording)
        # QTimer.singleShot(1000, window.start_auto_scroll)
        




        def move_video(duration_seconds=10):
            """Process and move recorded video in YouTube Shorts format"""
            try:
                # Adjust recording time based on duration
                QTimer.singleShot(duration_seconds * 1000, window.stop_recording)
                
                if hasattr(window, 'video_writer') and window.video_writer:
                    window.video_writer.release()
                
                VideoManager.process_video(actor.name, duration_seconds)
                
            except Exception as e:
                if DEBUG:
                    logger.error(f"Error processing video: {e}")
                
        app.aboutToQuit.connect(move_video)
        app.exec()
        
    except Exception as e:
        if DEBUG:
            logger.error(f"Error in main: {e}")
            logger.debug(traceback.format_exc())