import time
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QUrl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QHBoxLayout, QApplication
from PyQt6.QtMultimedia import QSoundEffect
import cv2
import numpy as np
import os
import logging
from VideoManager import VideoManager

logger = logging.getLogger(__name__)
DEBUG = False

class InfographGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.scroll_area = None
        self.scroll_animation = None
        self.scroll_timer = None
        # self.media_players = []  # Unused
        self.sound_effects = []
        self.current_sound = None
        self.setFixedWidth(1080)  # Set fixed width to 1080px
        self.setMinimumHeight(900)
        self.recording = False
        self.video_manager = VideoManager()

    def play_sound(self, soundbite_path):
        try:
            if DEBUG:
                logger.debug(f"\nAttempting to play sound: {soundbite_path}")
            wav_path = soundbite_path.replace('.mp3', '.wav')
            if DEBUG:
                logger.debug(f"Using WAV path: {wav_path}")
            
            if not os.path.exists(wav_path):
                if DEBUG:
                    logger.debug(f"WAV file not found: {wav_path}")
                return
            
            # Create new sound effect
            self.current_sound = QSoundEffect()
            self.sound_effects.append(self.current_sound)
            
            self.current_sound.setSource(QUrl.fromLocalFile(wav_path))
            self.current_sound.setVolume(1.0)
            
            # Wait for sound to load
            while not self.current_sound.isLoaded():
                QApplication.processEvents()
            
            if DEBUG:
                logger.debug(f"Sound loaded: {self.current_sound.isLoaded()}")
            
            # Play the sound
            self.current_sound.play()
            if DEBUG:
                logger.debug("Play command issued")
            
            # Set up a timer to clean up after 0.5 seconds
            QTimer.singleShot(500, lambda: self.cleanup_sound(self.current_sound))
            
        except Exception as e:
            logger.error(f"Error playing sound: {e}")
            import traceback
            traceback.print_exc()

    def cleanup_sound(self, sound_effect):
        """Remove the sound effect from our list"""
        if sound_effect in self.sound_effects:
            self.sound_effects.remove(sound_effect)

    def generateScroller(self, posters, actor_poster):
        try:
            # Only create main layout if it doesn't exist
            if not self.layout():
                main_layout = QHBoxLayout(self)
                main_layout.setContentsMargins(0, 0, 0, 0)
                main_layout.setSpacing(0)
                self.setLayout(main_layout)
            else:
                main_layout = self.layout()
                # Clear existing items from layout
                while main_layout.count():
                    item = main_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()

            # Create scroll area
            self.scroll_area = QScrollArea(self)
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.scroll_area.setFixedWidth(1080)

            # Create container for posters
            container = QWidget()
            container_layout = QVBoxLayout()
            container_layout.setSpacing(0)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            
            # Add actor poster at start and end of poster list
            if actor_poster and posters:
                # Add actor poster at beginning and end
                posters = [actor_poster] + posters + [actor_poster]
            elif actor_poster:
                posters = [actor_poster]
            
            # Add each poster with center alignment
            for poster in posters:
                container_layout.addWidget(poster, 0, Qt.AlignmentFlag.AlignHCenter)
            
            container.setLayout(container_layout)
            self.scroll_area.setWidget(container)
            
            # Add scroll area directly without stretching since we want fixed width
            main_layout.addWidget(self.scroll_area)
            
            # Make sure auto-scroll is properly initialized
            self.scroll_timer = QTimer(self)
            self.scroll_timer.timeout.connect(self.auto_scroll)
            self.is_scrolling = True  # Make sure this is set
            
        except Exception as e:
            logger.error(f"Error in generateScroller: {e}")
            import traceback
            traceback.print_exc()

    def generateFullImage(self, posters, actor_poster):
        try:
            # Create main layout
            main_layout = QHBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)  # Remove spacing in main layout
            self.setLayout(main_layout)
            
            # Create container for posters
            container = QWidget()
            container_layout = QVBoxLayout()
            container_layout.setSpacing(0)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            
            # Add actor poster at start and end of poster list
            if actor_poster and posters:
                # Add actor poster at beginning and end
                posters = [actor_poster] + posters + [actor_poster]
            elif actor_poster:
                posters = [actor_poster]
            
            # Add each poster with center alignment
            for poster in posters:
                container_layout.addWidget(poster, 0, Qt.AlignmentFlag.AlignHCenter)
            
            container.setLayout(container_layout)
            
            # Add container directly to main layout
            main_layout.addWidget(container)
            
        except Exception as e:
            logger.error(f"Error in generateFullImage: {e}")
            import traceback
            traceback.print_exc()

    def auto_scroll(self):
        try:
            if not hasattr(self, 'is_scrolling') or not self.is_scrolling:
                return
                
            scrollbar = self.scroll_area.verticalScrollBar()
            current_value = scrollbar.value()
            max_value = scrollbar.maximum()
            
            # If we're at the bottom, reset to top
            if current_value >= max_value:
                scrollbar.setValue(0)
                return
                
            # Create smooth scrolling animation
            if not hasattr(self, 'scroll_animation') or self.scroll_animation is None or self.scroll_animation.state() != QPropertyAnimation.State.Running:
                self.scroll_animation = QPropertyAnimation(scrollbar, b"value")
                self.scroll_animation.setDuration(500)  # 0.5 seconds per scroll
                self.scroll_animation.setStartValue(current_value)
                self.scroll_animation.setEndValue(min(current_value + 200, max_value))
                self.scroll_animation.start()
                
            # Check for sound triggers
            viewport_height = self.scroll_area.viewport().height()
            target_y = viewport_height * 0.6
            
            for widget in self.scroll_area.widget().findChildren(QWidget):
                if hasattr(widget, 'soundbite_path') and widget.soundbite_path:
                    widget_pos = widget.mapTo(self.scroll_area.viewport(), QPoint(0, int(widget.height()/2)))
                    if abs(widget_pos.y() - target_y) < 10:
                        self.play_sound(widget.soundbite_path)
                        break
                        
        except Exception as e:
            logger.error(f"Error in auto_scroll: {e}")
            import traceback
            traceback.print_exc()

    def start_auto_scroll(self):
        self.is_scrolling = True
        if self.scroll_timer and not self.scroll_timer.isActive():
            self.scroll_timer.start(150)
            
    def pause_auto_scroll(self):
        self.is_scrolling = False
        if self.scroll_timer and self.scroll_timer.isActive():
            self.scroll_timer.stop()
        if self.scroll_animation and self.scroll_animation.state() == QPropertyAnimation.State.Running:
            self.scroll_animation.stop()

    def start_recording(self):
        try:
            # Hide scrollbar before recording
            self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            
            if self.video_manager.start_recording(self, self.scroll_area):
                self.recording = True
                # Start frame capture timer
                self.capture_timer = QTimer()
                self.capture_timer.timeout.connect(self.capture_frame)
                self.capture_timer.start(33)  # ~30 fps capture
            
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            
    def capture_frame(self):
        if not self.recording:
            return
            
        try:
            self.video_manager.capture_frame(self)
            
            # Check if we've reached the end of scrolling
            scrollbar = self.scroll_area.verticalScrollBar()
            if scrollbar.value() >= scrollbar.maximum():
                self.stop_recording()
                self.pause_auto_scroll()
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            
    def stop_recording(self):
        self.recording = False
        # Restore scrollbar after recording
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.video_manager.stop_recording()
        if hasattr(self, 'capture_timer'):
            self.capture_timer.stop()
