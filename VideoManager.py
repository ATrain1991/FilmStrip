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
    def process_video(actor_name, duration_seconds=10):
        """Process and move recorded video in YouTube Shorts format (9:16, 1080x1920, 60fps)"""
        try:
            time.sleep(1.0)
            
            video_files = [f for f in os.listdir() if f.startswith("actor_scroll_") and f.endswith(".mp4")]
            if not video_files:
                return
                
            latest_video = max(video_files, key=os.path.getctime)
            cap = cv2.VideoCapture(latest_video)
            if not cap.isOpened():
                if DEBUG:
                    logger.error("Error: Could not open video file")
                return
                    
            actor_dir = os.path.join(os.getcwd(), actor_name)
            os.makedirs(actor_dir, exist_ok=True)
            new_name = f"{actor_name.replace(' ', '_')}_shorts.mp4"
            out_path = os.path.join(actor_dir, new_name)
            
            # YouTube Shorts specifications
            target_width = 1080  # 9:16 aspect ratio
            target_height = 1920
            target_fps = 60.0  # Recommended for Shorts
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(out_path, fourcc, target_fps, (target_width, target_height))
            
            if not out.isOpened():
                if DEBUG:
                    logger.error("Error: Could not create output video file")
                return
                
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Calculate dimensions for center crop
                height, width = frame.shape[:2]
                aspect_ratio = target_height / target_width
                
                # Calculate crop dimensions to maintain aspect ratio
                if width * aspect_ratio > height:
                    # Width needs to be cropped
                    new_width = int(height / aspect_ratio)
                    x_offset = (width - new_width) // 2
                    frame = frame[:, x_offset:x_offset + new_width]
                else:
                    # Height needs to be cropped
                    new_height = int(width * aspect_ratio)
                    y_offset = (height - new_height) // 2
                    frame = frame[y_offset:y_offset + new_height, :]
                
                # Resize to target dimensions
                frame = cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
                out.write(bgr_frame)
                
            cap.release()
            out.release()
            os.remove(latest_video)
            
        except Exception as e:
            if DEBUG:
                logger.error(f"Error processing video: {e}")

    def start_recording(self, widget, scroll_area):
        """Start recording the widget content"""
        try:
            size = widget.size()
            filename = f"actor_scroll_{time.strftime('%Y%m%d_%H%M%S')}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(filename, fourcc, 15.0,
                                              (size.width(), size.height()))
            self.recording = True
            self.frame_count = 0
            return self.video_writer is not None
            
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            return False

    def capture_frame(self, widget):
        """Capture a single frame from the widget"""
        if not self.recording:
            return None
            
        try:
            screen = QApplication.primaryScreen()
            pixmap = screen.grabWindow(widget.winId())
            image = pixmap.toImage()
            
            width = image.width()
            height = image.height()
            ptr = image.bits()
            ptr.setsize(image.sizeInBytes())
            arr = np.array(ptr).reshape(height, width, 4)
            
            frame = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            self.frame_count += 1
            if self.frame_count % 2 == 0:
                self.video_writer.write(frame)
            
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None

    def stop_recording(self):
        """Stop the recording process"""
        self.recording = False
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

    def create_scrolling_video(self, image_path, output_path, duration=10):
        """Create a video scrolling through a tall image over specified duration
        Formatted for YouTube Shorts (1080x1920 vertical video)
        
        Args:
            image_path (str): Path to input image
            output_path (str): Path for output video 
            duration (int): Duration in seconds (default 10)
        """
        try:
            # Read input image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image at {image_path}")
                
            # Get dimensions
            img_height, img_width = image.shape[:2]
            
            # Resize image to 1080 width if needed while maintaining aspect ratio
            if img_width != 1080:
                scale = 1080 / img_width
                new_height = int(img_height * scale)
                image = cv2.resize(image, (1080, new_height))
                img_height = new_height
            
            # Set output video parameters for YouTube Shorts
            fps = 60
            total_frames = fps * duration
            output_height = 1920  # YouTube Shorts height
            
            # Calculate scroll increment per frame
            scroll_per_frame = (img_height - output_height) / total_frames
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (1080, output_height))
            
            # Generate each frame
            for frame_num in range(total_frames):
                # Calculate scroll position
                scroll_pos = int(frame_num * scroll_per_frame)
                
                # Extract visible portion (1080x1920)
                frame = image[scroll_pos:scroll_pos + output_height, :1080]
                
                # If frame is smaller than required height, pad with black
                if frame.shape[0] < output_height:
                    padding = np.zeros((output_height - frame.shape[0], 1080, 3), dtype=np.uint8)
                    frame = np.vstack((frame, padding))
                
                # Write frame
                out.write(frame)
                
            # Release video writer
            out.release()
            
        except Exception as e:
            logger.error(f"Error creating scrolling video: {e}")
            raise

