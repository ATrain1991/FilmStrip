



import numpy as np


def stitch_film_strips(movie_images: list[np.ndarray],actor_image: list[np.ndarray] = None ):
    """
    Stitches together multiple film strip images vertically with a small overlap
    
    Args:
        movie_images: List of film strip images to stitch together
        
    Returns:
        Combined image with all strips stitched vertically
    """
    if not movie_images:
        return None
    if actor_image is not None:
        movie_images.insert(0, actor_image)
        
    # Get dimensions from first image
    height, width = movie_images[0].shape[:2]
    
    # Calculate total height needed
    total_height = height * len(movie_images)
    
    # Create output image
    result = np.zeros((total_height, width, 3), dtype=np.uint8)
    
    # Place images vertically without overlap
    y_pos = 0
    for img in movie_images:
        result[y_pos:y_pos + height] = img
        y_pos += height
        
    return result