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
    def create_looping_video(image_path, output_path, duration=10):
        """Create a seamlessly looping video scrolling through a tall image over specified duration.
        The top and bottom 1920px are identical to create perfect loop when repeated.
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

        # Create extended image with duplicated top/bottom sections
        top_section = image[:shorts_height, :]
        extended_image = np.concatenate([image, top_section])

        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 60, (shorts_width, shorts_height))

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
