import os
import cv2
import numpy as np
from Meter import Meter, MeterType, Poster, Movie

def create_stacked_background(num_strips, strip_width, strip_height, overlap_percent=0.1):
    """
    Creates vertically stacked background strips with overlap
    
    Args:
        num_strips: Number of background strips to stack
        strip_height: Height of each strip
        strip_width: Width of each strip
        overlap_percent: Percentage of overlap between strips (0-1)
        
    Returns:
        Combined background image
    """
    # Calculate total height accounting for overlap
    overlap_pixels = int(strip_height * overlap_percent)
    total_height = strip_height * num_strips # Remove overlap calculation to get full height
    
    # Create blank background (ensure integers for dimensions)
    background = np.zeros((total_height, int(strip_width), 3), dtype=np.uint8)
    
    # Create and stack strips
    for i in range(num_strips):
        # Create strip with random noise/pattern
        strip = np.random.randint(20, 40, (strip_height, strip_width, 3), dtype=np.uint8)
        
        # Calculate y position without overlap reduction
        y_pos = i * strip_height
        
        # Place strip at full height
        background[y_pos:y_pos + strip_height, :] = strip
            
    return background

def stitch_movies(movies: list[Movie], background=None):
    # Get dimensions from first movie's poster
    first_movie = movies[0]
    first_poster_tuple = first_movie.get_poster_tuple()
    _, _, _, width, height = first_poster_tuple
    
    # Calculate total height needed
    total_height = height * len(movies)
    
    # Create blank canvas or use provided background
    if background is None:
        print(f"Creating background with height: {total_height}")
        result = np.zeros((total_height, width, 3), dtype=np.uint8)
    else:
        result = background.copy()
        
    # Stitch movies vertically
    for i, movie in enumerate(movies):
        # Calculate y position for this movie
        y_offset = i * height
        
        # Get poster tuple and update y position
        poster_tuple = list(movie.get_poster_tuple())
        poster_tuple[2] = y_offset  # Update y coordinate
        
        # Get meter tuples and update y positions
        tmeter_tuple = list(movie.get_tmeter_tuple())
        pmeter_tuple = list(movie.get_pmeter_tuple())
        tmeter_tuple[2] += y_offset
        pmeter_tuple[2] += y_offset
        
        # Get text tuples and update y positions
        year_tuple = list(movie.get_year_tuple())
        box_office_tuple = list(movie.get_box_office_tuple())
        tmeter_text = list(movie.get_tmeter_text_tuple())
        pmeter_text = list(movie.get_pmeter_text_tuple())
        
        year_tuple[2] += y_offset
        box_office_tuple[2] += y_offset
        tmeter_text[2] += y_offset
        pmeter_text[2] += y_offset
        
        # Overlay images and text for this movie section
        images = [
            tuple(poster_tuple),
            tuple(tmeter_tuple),
            tuple(pmeter_tuple)
        ]
        
        texts = [
            tuple(year_tuple),
            tuple(box_office_tuple),
            tuple(tmeter_text),
            tuple(pmeter_text)
        ]
        
        overlay_images_and_text(result, images, texts)
    
    return result
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


# def create_film_strip2(movies: list[Movie], background=None):
#     """
#     Creates or updates a film strip with custom images and text
    
#     Args:
#         movie: Movie object
#         Tmeter: Meter object
#         Pmeter: Meter object
#         strip_index: Which background strip to use (0-5)
#         background: Optional existing background image to update. If None, creates new background
        
#     Returns:
#         Final composited image
#     """
#     # Create base background by stacking film strips if not provided
#     if background is None:
#         create_stacked_background(6, 1920, 1080, 0.1)
#         print("No background provided, creating new background")
#         return None
#     for movie in movies:
#     # Format image overlay data
#         images = [
#             movie.get_poster_tuple(),    # First image position
#             movie.get_tmeter_tuple(),   # Second image position  
#             movie.get_pmeter_tuple()    # Third image position
#         ]
        
#         # Format text overlay data 
#         texts = [
#             movie.get_year_tuple(),   # First text position
#             movie.get_box_office_tuple(),  # Second text position
#             movie.get_tmeter_text_tuple(),  # Third text position
#             movie.get_pmeter_text_tuple()   # Fourth text position
#         ]
    
    
#         # Overlay images and text
#     result = overlay_images_and_text(background, images, texts)
    
#     return result
# def example_usage2():
#     """Example usage of create_film_strip function"""
#     current_dir = os.path.dirname(os.path.abspath(__file__))
    
#     # Fix the paths by using os.path.join
#     background_image = os.path.join(current_dir, "icons", "film_strip.png")
#     poster_path = os.path.join(current_dir, "Will Smith", "Independence_Day.jpg")
#     tomato_path = os.path.join(current_dir, "icons", "FreshTomato.png")
#     popcorn_path = os.path.join(current_dir, "icons", "FreshPopcorn.png")
    
#     # Use the full paths
#     background = (background_image, 0, 0, 1920, 1080)
#     poster_tuple = (poster_path, 156, 144, 770, 1365)
#     tomato_tuple = (tomato_path, 156, 1510, 300, 300)
#     popcorn_tuple = (popcorn_path, 626, 1510, 300, 300)
    
#     # Example image paths
#     images = [
#         poster_tuple,
#         tomato_tuple,
#         popcorn_tuple
#     ]
#     Tmeter = Meter(MeterType.TOMATO, 98)
#     Pmeter = Meter(MeterType.POPCORN, 51)
#     poster = Poster(poster_path, 156, 144, 770, 1365)   
#     year = "1998"
#     box_office = "105M"


#     result = create_film_strip2(poster, Tmeter, Pmeter, 0, background)
#     # Example text items
    
#     # Create output directory if it doesn't exist
#     output_dir = os.path.join(current_dir, "output")
#     os.makedirs(output_dir, exist_ok=True)
    
#     # Save result
#     output_path = os.path.join(output_dir, "film_strip.jpg") 
#     cv2.imwrite(output_path, result)
#     # Open and display the output image
#     result_image = cv2.imread(output_path)
#     cv2.imshow('Film Strip Result', result_image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
# def example_usage():
#     """Example usage of create_film_strip function"""
#     current_dir = os.path.dirname(os.path.abspath(__file__))
    
#     # Fix the paths by using os.path.join
#     background_image = os.path.join(current_dir, "icons", "film_strip.png")
#     poster_path = os.path.join(current_dir, "Will Smith", "Independence_Day.jpg")
#     tomato_path = os.path.join(current_dir, "icons", "FreshTomato.png")
#     popcorn_path = os.path.join(current_dir, "icons", "FreshPopcorn.png")
    
#     # Use the full paths
#     background = (background_image, 0, 0, 1920, 1080)
#     poster_tuple = (poster_path, 156, 144, 770, 1365)
#     tomato_tuple = (tomato_path, 156, 1510, 300, 300)
#     popcorn_tuple = (popcorn_path, 626, 1510, 300, 300)
    
#     # Example image paths
#     images = [
#         poster_tuple,
#         tomato_tuple,
#         popcorn_tuple
#     ]
#     Tmeter = Meter(MeterType.TOMATO, 98)
#     Pmeter = Meter(MeterType.POPCORN, 89)
#     poster = Poster(poster_path, 156, 144, 770, 1365)   
#     year = "1998"
#     box_office = "105M"
#     tomatometer = "98%"
#     audience_score = "89%"

#     result = create_film_strip2(poster, Tmeter, Pmeter, 0, background)
#     # Example text items
#     text_items = [
#         year,
#         box_office, 
#         tomatometer,
#         audience_score
#     ]
    
#     # Create film strip using index 0
#     result = create_film_strip(
#         images,
#         text_items,
#         0,
#         background
#     )
    
#     # Create output directory if it doesn't exist
#     output_dir = os.path.join(current_dir, "output")
#     os.makedirs(output_dir, exist_ok=True)
    
#     # Save result
#     output_path = os.path.join(output_dir, "film_strip.jpg") 
#     cv2.imwrite(output_path, result)
#     # Open and display the output image
#     result_image = cv2.imread(output_path)
#     cv2.imshow('Film Strip Result', result_image)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
# def simple_usage():
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     poster_path = os.path.join(current_dir, "Will Smith", "Independence_Day.jpg")
#     Tmeter = Meter(MeterType.TOMATO, 98)
#     Pmeter = Meter(MeterType.POPCORN, 51)
#     poster = Poster(poster_path, 156, 144, 770, 1365)   
#     year = "1998"
#     box_office = "105M"
#     movie = Movie(poster,Tmeter,Pmeter,year,box_office)
#     # background= create_stacked_background(6, 1920, 1080, 0.1)
#     # result = create_film_strip2(movie, None, None, 0, background)
#     result = stitch_movies([movie,movie,movie], None)
#     cv2.imshow('Film Strip Result', result)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()

def create_single_film_strip(movie: Movie):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    background_image = os.path.join(current_dir, "icons", "film_strip.png")
    # Load background image
    background = cv2.imread(background_image)
    if background is None:
        raise ValueError(f"Could not load background image from {background_image}")
        
    # Get image and text tuples from movie
    images = [
        movie.get_poster_tuple(),
        movie.get_tmeter_tuple(),
        movie.get_pmeter_tuple()
    ]
    
    texts = [
        movie.get_year_tuple(),
        movie.get_box_office_tuple(), 
        movie.get_tmeter_text_tuple(),
        movie.get_pmeter_text_tuple()
    ]
    
    # Overlay movie content onto background
    result = overlay_images_and_text(background, images, texts)
    
    return result
if __name__ == "__main__":
    # simple_usage()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    poster_path = os.path.join(current_dir, "Will Smith", "Independence_Day.jpg")
    Tmeter = Meter(MeterType.TOMATO, 98)
    Pmeter = Meter(MeterType.POPCORN, 51)
    poster = Poster(poster_path, 156, 144, 770, 1365)   
    year = "1998"
    box_office = "105M"
    movie = Movie(poster,Tmeter,Pmeter,year,box_office)
    result = create_single_film_strip(movie)
    cv2.imwrite(os.path.join(current_dir, "output", "single_film_strip.jpg"), result)
    cv2.imshow('Film Strip Result', result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

