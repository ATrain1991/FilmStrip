import cv2

class VideoManager:
    @staticmethod
    def process_video(output_path: str, duration: int):
        """
        Process and save the video file
        
        Args:
            output_path: Path where the final video should be saved
            duration: Duration of the video in seconds
        """
        # Read the original video
        cap = cv2.VideoCapture(output_path)
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(f'processed_{output_path}', fourcc, fps, (width, height))
        
        # Process each frame
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Write the frame
            out.write(frame)
            
        # Release everything
        cap.release()
        out.release()
