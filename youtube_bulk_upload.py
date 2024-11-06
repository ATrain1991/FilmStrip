from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from PIL import Image
import cv2
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.download_util import load_file_from_url
from realesrgan import RealESRGANer
import torch
import os
import json
from pathlib import Path
import time

class ThumbnailProcessor:
    def __init__(self):
        self.target_width = 1280
        self.target_height = 720
        self.max_file_size = 2 * 1024 * 1024  # 2MB in bytes
        
        # Initialize RealESRGAN
        self.setup_upscaler()
        
    def setup_upscaler(self):
        """Initialize the RealESRGAN upscaler"""
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        model_path = 'RealESRGAN_x4plus.pth'
        
        # Download model if not exists
        if not os.path.exists(model_path):
            load_file_from_url(
                'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth',
                model_path
            )
        
        self.upscaler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=True
        )
    
    def resize_image(self, image, upscale=False):
        """Resize image to target resolution, maintaining aspect ratio"""
        # Calculate aspect ratio
        aspect_ratio = self.target_width / self.target_height
        img_aspect_ratio = image.width / image.height
        
        if upscale and (image.width < self.target_width or image.height < self.target_height):
            # Convert PIL image to cv2 format for upscaling
            cv2_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            # Upscale using RealESRGAN
            output, _ = self.upscaler.enhance(cv2_img, outscale=4)
            # Convert back to PIL
            image = Image.fromarray(cv2.cvtColor(output, cv2.COLOR_BGR2RGB))
        
        # Calculate new dimensions
        if img_aspect_ratio > aspect_ratio:
            new_width = self.target_width
            new_height = int(new_width / img_aspect_ratio)
        else:
            new_height = self.target_height
            new_width = int(new_height * img_aspect_ratio)
        
        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create new image with target dimensions and paste resized image
        final = Image.new('RGB', (self.target_width, self.target_height), (0, 0, 0))
        x_offset = (self.target_width - new_width) // 2
        y_offset = (self.target_height - new_height) // 2
        final.paste(resized, (x_offset, y_offset))
        
        return final
    
    def optimize_file_size(self, image, max_quality=95):
        """Optimize image file size while maintaining quality"""
        quality = max_quality
        while quality > 5:
            # Save image to bytes buffer
            from io import BytesIO
            buffer = BytesIO()
            image.save(buffer, format='JPEG', quality=quality)
            size = buffer.tell()
            
            if size <= self.max_file_size:
                return buffer.getvalue()
            
            quality -= 5
        
        raise ValueError("Unable to optimize image to under 2MB while maintaining acceptable quality")
    
    def process_thumbnail(self, image_path, output_path=None, upscale=True):
        """Process thumbnail to meet YouTube requirements"""
        try:
            # Open and convert to RGB
            image = Image.open(image_path).convert('RGB')
            
            # Resize image
            processed = self.resize_image(image, upscale=upscale)
            
            # Optimize file size
            image_data = self.optimize_file_size(processed)
            
            # Save processed image
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                return output_path
            else:
                output_path = f"{os.path.splitext(image_path)[0]}_processed.jpg"
                with open(output_path, 'wb') as f:
                    f.write(image_data)
                return output_path
                
        except Exception as e:
            print(f"Error processing thumbnail: {str(e)}")
            return None

class YoutubeShortsUploader:
    def __init__(self, client_secrets_file):
        self.client_secrets_file = client_secrets_file
        self.credentials = None
        self.youtube = None
        self.thumbnail_processor = ThumbnailProcessor()
        
    def authenticate(self):
        """Authenticate with YouTube API using OAuth 2.0"""
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
                  'https://www.googleapis.com/auth/youtube.force-ssl']
        
        if os.path.exists('token.json'):
            self.credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not self.credentials or not self.credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, SCOPES)
            self.credentials = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(self.credentials.to_json())
        
        self.youtube = build('youtube', 'v3', credentials=self.credentials)
    
    def set_thumbnail(self, video_id, thumbnail_path):
        """Set a custom thumbnail for a video"""
        if not os.path.exists(thumbnail_path):
            print(f"Thumbnail file not found: {thumbnail_path}")
            return False
            
        try:
            # Process thumbnail
            processed_thumbnail = self.thumbnail_processor.process_thumbnail(
                thumbnail_path,
                output_path=f"{os.path.splitext(thumbnail_path)[0]}_youtube.jpg"
            )
            
            if not processed_thumbnail:
                return False
            
            # Upload processed thumbnail
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(
                    processed_thumbnail,
                    mimetype='image/jpeg',
                    resumable=True
                )
            )
            response = request.execute()
            print(f"Thumbnail set successfully for video {video_id}")
            
            # Clean up processed thumbnail
            os.remove(processed_thumbnail)
            return True
            
        except Exception as e:
            print(f"Error setting thumbnail: {str(e)}")
            return False
    
    # ... [rest of the YoutubeShortsUploader class remains the same] ...

def main():
    # Initialize uploader
    uploader = YoutubeShortsUploader('client_secrets.json')
    uploader.authenticate()
    
    # Example metadata file structure:
    # {
    #     "video1.mp4": {
    #         "title": "My Cool Short",
    #         "description": "Check out this awesome content!",
    #         "tags": ["funny", "viral", "shorts"],
    #         "thumbnail": "thumbnails/video1_thumb.jpg"
    #     }
    # }
    
    # Example of processing a single thumbnail
    # processor = ThumbnailProcessor()
    # processed_path = processor.process_thumbnail(
    #     "original_thumbnail.jpg",
    #     "processed_thumbnail.jpg",
    #     upscale=True
    # )
    
    # Perform bulk upload
    results = uploader.bulk_upload(
        directory='shorts_folder',
        metadata_file='metadata.json'
    )
    
    print("\nUpload Results:")
    for result in results:
        print(f"Uploaded {result['file']} - Video ID: {result['video_id']}")

if __name__ == '__main__':
    main()