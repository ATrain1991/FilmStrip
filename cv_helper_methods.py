import cv2
import numpy as np


def overlay_images_and_text(background, images, texts):
        """
        Overlays images and text on background
        
        Args:
            background: Background image array
            images: List of 3 (image_path, x, y, width, height) tuples
            texts: List of 4 (text, x, y, font_scale, color) tuples
            
        Returns:
            Final composited image
        """
        # Load background if it's a tuple (path, x, y, width, height)
        if background is None:
            print("No background provided, creating new background")
            return None
        
        # Overlay images
        for img_tuple in images:
            img_path = img_tuple[0]
            x, y, width, height = img_tuple[1:]
            img = cv2.imread(img_path)
            if img is not None:
                # Resize image first to match the requested dimensions
                img = cv2.resize(img, (width, height))
                
                # Ensure coordinates are within bounds
                y1 = max(0, y)
                y2 = min(y + height, background.shape[0])
                x1 = max(0, x)
                x2 = min(x + width, background.shape[1])
                
                if y2 > y1 and x2 > x1:
                    # Crop image to match the actual region being modified
                    img = img[:(y2-y1), :(x2-x1)]
                    
                    # Create mask matching the cropped image dimensions
                    mask = np.ones(img.shape[:2], dtype=np.float32)
                    mask = cv2.GaussianBlur(mask, (7,7), 0)
                    
                    for c in range(3):
                        background[y1:y2, x1:x2, c] = (
                            background[y1:y2, x1:x2, c] * (1 - mask) +
                            img[:,:,c] * mask
                        )
        
        # Add text
        
        for text, x, y, scale, color, font, size in texts:
            # Use better anti-aliasing and thickness for sharper text
            cv2.putText(background, text, (x, y), font, scale, color, size, cv2.LINE_AA)
            
        return background