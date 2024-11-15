from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, CompositeAudioClip
from pydub import AudioSegment
import cv2
import os
import time
import logging
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
import numpy as np

logger = logging.getLogger(__name__)
DEBUG = False

class VideoManager:
    def __init__(self):
        self.recording = False
        self.video_writer = None
        self.frame_count = 0
        self.capture_timer = None

    @staticmethod
    def create_looping_video(image_path, output_path, duration=15):
        """Create a seamlessly looping video"""
        try:
            # Create a temp directory in our project folder
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Create temp files in our temp directory
            temp_video_path = os.path.join(temp_dir, 'temp_video.mp4')
            temp_audio_path = os.path.join(temp_dir, 'temp_audio.mp3')
            
            # Read the input image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return

            # Get image dimensions
            img_height, img_width = image.shape[:2]

            # YouTube Shorts dimensions
            shorts_width = 1080
            shorts_height = 1920

            # Resize image width to match Shorts width while maintaining aspect ratio
            scale = shorts_width / img_width
            new_height = int(img_height * scale)
            image = cv2.resize(image, (shorts_width, new_height))

            # Create extended image with duplicated top/bottom sections
            top_section = image[:shorts_height, :]
            extended_image = np.concatenate([image, top_section])

            # Create temporary video file
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video_path, fourcc, 60, (shorts_width, shorts_height))

            # Calculate scroll speed (pixels per frame)
            total_frames = duration * 60  # 60 fps
            scroll_distance = extended_image.shape[0] - shorts_height
            scroll_speed = scroll_distance / total_frames

            # Create scrolling effect
            for frame_num in range(int(total_frames)):
                # Calculate current scroll position
                scroll_pos = int(frame_num * scroll_speed)
                
                # Extract current window view
                window = extended_image[scroll_pos:scroll_pos + shorts_height, 0:shorts_width]
                
                # Handle case where window is smaller than shorts height at end of scroll
                if window.shape[0] < shorts_height:
                    # Create black frame
                    frame = np.zeros((shorts_height, shorts_width, 3), dtype=np.uint8)
                    # Place window at top
                    frame[0:window.shape[0], 0:shorts_width] = window
                else:
                    frame = window

                out.write(frame)

            out.release()

            # Load the video
            video = VideoFileClip(temp_video_path)

            # Load background music and adjust volume
            current_dir = os.path.dirname(os.path.abspath(__file__))
            wav_path = os.path.join(current_dir, "soundclips", "background.wav")
            mp3_path = os.path.join(current_dir, "soundclips", "background.mp3")
            if not os.path.exists(mp3_path):
                AudioSegment.from_wav(wav_path).export(mp3_path, format="mp3")
            bg_music = AudioFileClip(mp3_path)
            bg_music = bg_music.volumex(1.25)  # Reduce volume to 10%
            
            # Loop bg_music if shorter than video
            if bg_music.duration < video.duration:
                bg_music = bg_music.loop(duration=video.duration)
            else:
                bg_music = bg_music.subclip(0, video.duration)

            # Create commentary audio
            commentary = AudioSegment.silent(duration=int(duration * 1000))  # Duration in ms
            
            # Calculate timing for each section
            section_duration = (duration * 1000) / 6  # 6 sections total, time in ms
            
            # Commentary sound clips mapping
            sound_clips = {
                1: "CriticsFavorite.mp3",
                2: "AudienceFavorite.mp3", 
                3: "MostSuccessful.mp3",
                4: "CriticsLeastFavorite.mp3",
                5: "AudienceLeastFavorite.mp3",
                6: None   # Last section - no sound
            }

            # Add commentary clips at appropriate times
            for section in range(1, 6):
                clip_file = sound_clips[section]
                if clip_file:
                    clip_path = os.path.join(current_dir, "soundclips", clip_file)
                    if os.path.exists(clip_path):
                        section_clip = AudioSegment.from_file(clip_path)
                        position = int((section - 1) * section_duration)
                        commentary = commentary.overlay(section_clip, position=position)

            # Export commentary to our temp directory
            commentary.export(temp_audio_path, format="mp3")
            commentary_clip = AudioFileClip(temp_audio_path)
            commentary_clip = commentary_clip.volumex(1.5)
            # Combine video with both audio tracks
            final_video = video.set_audio(CompositeVideoClip([
                video.set_audio(bg_music),
                video.set_audio(commentary_clip)
            ]).audio)

            # Write final video
            final_video.write_videofile(output_path, codec='libx264', audio_codec='aac')

            # Cleanup
            try:
                video.close()
                bg_music.close()
                commentary_clip.close()
                os.remove(temp_video_path)
                os.remove(temp_audio_path)
                # Optionally remove temp directory if empty
                if not os.listdir(temp_dir):
                    os.rmdir(temp_dir)
            except Exception as e:
                print(f"Cleanup error (non-fatal): {e}")
                
        except Exception as e:
            print(f"Error creating looping video: {e}")
            import traceback
            traceback.print_exc()

    @staticmethod
    def create_scrolling_video(image_path, output_path, duration=10):
        """Create a video scrolling through a tall image over specified duration
        Formatted for YouTube Shorts (1080x1920 vertical video)
        """
        image_path = os.path.normpath(image_path)
        # Read the input image
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Failed to load image: {image_path}")
            return

        # Get image dimensions
        img_height, img_width = image.shape[:2]

        # YouTube Shorts dimensions
        shorts_width = 1080
        shorts_height = 1920

        # Resize image width to match Shorts width while maintaining aspect ratio
        scale = shorts_width / img_width
        new_height = int(img_height * scale)
        image = cv2.resize(image, (shorts_width, new_height))

        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 60, (shorts_width, shorts_height))

        # Calculate scroll speed (pixels per frame)
        total_frames = duration * 60  # 60 fps
        scroll_speed = (new_height - shorts_height) / total_frames

        # Create scrolling effect
        for frame_num in range(int(total_frames)):
            # Calculate current scroll position
            scroll_pos = int(frame_num * scroll_speed)
            
            # Extract current window view
            window = image[scroll_pos:scroll_pos + shorts_height, 0:shorts_width]
            
            # Handle case where window is smaller than shorts height at end of scroll
            if window.shape[0] < shorts_height:
                # Create black frame
                frame = np.zeros((shorts_height, shorts_width, 3), dtype=np.uint8)
                # Place window at top
                frame[0:window.shape[0], 0:shorts_width] = window
            else:
                frame = window

            out.write(frame)

        out.release()
        pass
def main():
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input and output directories
    input_dir = os.path.join(base_dir, "infographic images")
    output_dir = os.path.join(base_dir, "infographic videos")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get all image files from input directory
    image_files = [f for f in os.listdir(input_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]

    for image_file in image_files:
        input_path = os.path.join(input_dir, image_file)
        
        # Create output filename by replacing image extension with .mp4
        output_filename = os.path.splitext(image_file)[0] + ".mp4"
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"Processing {image_file}...")
        # VideoManager.create_scrolling_video(input_path, output_path)
        VideoManager.create_looping_video(input_path, output_path)
        print(f"Created video: {output_filename}")

if __name__ == "__main__":
    main()
