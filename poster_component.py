from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap
from models import noDB_actor
import image_resize


class ActorPosterComponent(QWidget):
    def __init__(self, actor:noDB_actor):
        super().__init__()
        """
        Initialize the actor poster component with statistics
        
        Args:
            actor (noDB_actor): Actor object containing all relevant information
        """
        super().__init__()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        
        # Main image (9:16 aspect ratio)
        main_image_label = QLabel()
        main_pixmap = QPixmap(actor.get_main_image_path())
        self.main_width = 270
        scaled_pixmap = main_pixmap.scaled(QSize(self.main_width, 960), Qt.AspectRatioMode.KeepAspectRatio)
        main_image_label.setPixmap(scaled_pixmap)
        main_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(main_image_label)
        
        # Stats container with two rows
        stats_container = QWidget()
        stats_container.setFixedWidth(self.main_width)
        stats_container.setStyleSheet("background-color: white;")
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(5)
        stats_layout.setContentsMargins(0, 10, 10, 5)
        stats_container.setLayout(stats_layout)
        
        # Top row with name and birthday/age
        top_row = QWidget()
        top_row.setStyleSheet("background-color: white;")
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Actor name
        name_label = QLabel(actor.name)
        name_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        top_layout.addWidget(name_label)
        
        # Birthday and age
        birthday_container = QWidget()
        birthday_container.setStyleSheet("background-color: white;")
        birthday_layout = QHBoxLayout()
        birthday_layout.setSpacing(2)
        
        date_label = QLabel(f"{actor.birthdate}")
        date_label.setStyleSheet("font-size: 12px;")
        birthday_layout.addWidget(date_label)
        
        age_label = QLabel(f"({actor.age} years)")
        age_label.setStyleSheet("font-size: 14px;")
        birthday_layout.addWidget(age_label)
        
        birthday_container.setLayout(birthday_layout)
        top_layout.addWidget(birthday_container)
        
        top_row.setLayout(top_layout)
        
        # Bottom row with ratings and box office
        bottom_row = QWidget()
        bottom_row.setStyleSheet("background-color: white;")
        bottom_layout = QHBoxLayout()
        
        # Tomato meter with icon
        tomato_container = QWidget()
        tomato_container.setStyleSheet("background-color: white;")
        tomato_layout = QHBoxLayout()
        tomato_icon = QLabel()
        avg_tomatometer = actor.get_average_tomatometer()
        tomato_icon_path = "icons/FreshTomato.png" if avg_tomatometer > 60 else "icons/RottenTomato.png"
        tomato_pixmap = QPixmap(tomato_icon_path).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio)
        tomato_icon.setPixmap(tomato_pixmap)
        tomato_layout.addWidget(tomato_icon)
        tomato_label = QLabel(f"{avg_tomatometer}%")
        tomato_layout.addWidget(tomato_label)
        tomato_container.setLayout(tomato_layout)
        bottom_layout.addWidget(tomato_container)
        
        # Popcorn meter with icon
        popcorn_container = QWidget()
        popcorn_container.setStyleSheet("background-color: white;")
        popcorn_layout = QHBoxLayout()
        popcorn_icon = QLabel()
        avg_popcornmeter = actor.get_average_popcornmeter()
        popcorn_icon_path = "icons/FreshPopcorn.png" if avg_popcornmeter > 60 else "icons/RottenPopcorn.png"
        popcorn_pixmap = QPixmap(popcorn_icon_path).scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio)
        popcorn_icon.setPixmap(popcorn_pixmap)
        popcorn_layout.addWidget(popcorn_icon)
        popcorn_label = QLabel(f"{avg_popcornmeter}%")
        popcorn_layout.addWidget(popcorn_label)
        popcorn_container.setLayout(popcorn_layout)
        bottom_layout.addWidget(popcorn_container)
        
        # Box office with icon
        box_office_container = QWidget()
        box_office_container.setStyleSheet("background-color: white;")
        box_office_layout = QHBoxLayout()
        box_office_icon = QLabel()
        box_office_pixmap = QPixmap("icons/box_office.png").scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio)
        box_office_icon.setPixmap(box_office_pixmap)
        box_office_layout.addWidget(box_office_icon)
        box_office_label = QLabel(f"${actor.NumerizeTotalBoxOffice()}")
        box_office_layout.addWidget(box_office_label)
        box_office_container.setLayout(box_office_layout)
        bottom_layout.addWidget(box_office_container)
        
        bottom_row.setLayout(bottom_layout)
        
        # Add rows to stats layout
        stats_layout.addWidget(top_row)
        stats_layout.addWidget(bottom_row)
        
        # Add stats container to main layout
        main_layout.addWidget(stats_container)

class PosterComponent(QWidget):
    
    def __init__(self, main_image_path, sub_images_data, year, soundbite_path):
        sub_image_scale_percent = 60 # 50% of the width of the main image
        self.year = year
        self.soundbite_path = soundbite_path
        """
        Initialize the poster component
        
        Args:
            main_image_path (str): Path to the main image
            sub_images_data (list): List of tuples containing (image_path, description) for sub-images
        """
        super().__init__()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0) # Changed from 5 to 0 to remove padding
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)
        
        # Main image (9:16 aspect ratio)
        main_image_label = QLabel()
        main_pixmap = QPixmap(main_image_path)
        self.main_width = 270
        scaled_pixmap = main_pixmap.scaled(QSize(self.main_width, 480), Qt.AspectRatioMode.KeepAspectRatio)
        main_image_label.setPixmap(scaled_pixmap)
        main_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(main_image_label)
        
        # Add black line separator
        separator = QWidget()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color: black;")
        main_layout.addWidget(separator)
        
        # Sub-images container with horizontal layout
        sub_images_container = QWidget()
        sub_images_container.setFixedWidth(self.main_width)
        sub_images_container.setStyleSheet("background-color: white;")
        sub_images_layout = QHBoxLayout()
        sub_images_layout.setSpacing(5)
        sub_images_layout.setContentsMargins(0, 0, 0, 0)
        sub_images_container.setLayout(sub_images_layout)
        
        # Calculate sizes
        num_sub_images = len(sub_images_data)
        spacing = 5
        total_spacing = spacing * (num_sub_images - 1)
        sub_component_width = (self.main_width - total_spacing) // num_sub_images
        sub_image_size = int(sub_component_width * sub_image_scale_percent/100)  # Reduced image size to 50% to accommodate text
        
        # Add each sub-image with its description
        for img_path, description, scale in sub_images_data:
            # Create a container for each image-text pair
            item_container = QWidget()
            item_container.setStyleSheet("background-color: white;")
            item_layout = QHBoxLayout()  # Changed to QHBoxLayout to place text right of image
            item_layout.setSpacing(2)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_container.setLayout(item_layout)
            item_container.setFixedWidth(sub_component_width)
            sub_component_width = (self.main_width - total_spacing) // num_sub_images
            sub_image_size = int(sub_component_width * scale/100) 
            # Sub-image
            sub_image_label = QLabel()
            sub_pixmap = QPixmap(img_path)
            sub_scaled_pixmap = sub_pixmap.scaled(
                QSize(sub_image_size, sub_image_size), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            sub_image_label.setPixmap(sub_scaled_pixmap)
            sub_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Description text
            # If this is the box office icon, numerize the description
            if "box_office.png" in img_path:
                from numerize import numerize
                try:
                    value = float(description.replace("$", "").replace(",", ""))
                    description = "$" + numerize.numerize(value)
                except ValueError:
                    pass
                    
            description_label = QLabel(description)
            description_label.setWordWrap(True)
            description_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
            # Set font size for description
            font = description_label.font()
            font.setPointSize(8)  # Reduced font size
            description_label.setFont(font)
            
            # Set fixed width for description to prevent overflow
            description_label.setFixedWidth(sub_component_width - sub_image_size - 10)  # 10 for padding
            
            # Add widgets to horizontal layout
            item_layout.addWidget(sub_image_label)
            item_layout.addWidget(description_label)
            sub_images_layout.addWidget(item_container)
        
        main_layout.addWidget(sub_images_container)

        
# Example usage
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Example data
    main_img = "Tom Hardy\Mad_Max_Fury_Road.jpg"
    # main_img = image_resize.resize_image_return(main_img, 540, 960)
    tomato_meter = 67
    popcorn_meter = 95
    box_office = "10.5M"
    sub_images = [
        ("icons\FreshTomato.png", f"{tomato_meter}%", 60),
        ("icons\FreshPopcorn.png", f"{popcorn_meter}%", 60),
        ("icons\\box_office.png", box_office, 45)
    ]
    
    # Create and show poster
    poster = PosterComponent(main_img, sub_images, tomato_meter, popcorn_meter, box_office)
    poster.resize(1080, 1920)  # Increased height to show more content
    # poster.scale_factor = 0.5
    poster.setWindowFlags(poster.windowFlags() | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowMaximizeButtonHint)  # Make window resizable and stay on top
    # Center the window on screen
    screen = QApplication.primaryScreen().geometry()
    # window_geometry = poster.frameGeometry()
    # window_geometry.moveCenter(screen.center())
    # poster.move(window_geometry.topLeft())
    poster.show()
    
    # Keep window open until user closes it
    sys.exit(app.exec())
