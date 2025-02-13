import os
import cv2

def preprocess_videos(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for action in os.listdir(input_dir):
        action_path = os.path.join(input_dir, action)
        output_action_path = os.path.join(output_dir, action)
        os.makedirs(output_action_path, exist_ok=True)
        
        for video_file in os.listdir(action_path):
            video_path = os.path.join(action_path, video_file)
            cap = cv2.VideoCapture(video_path)
            frame_idx = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                resized_frame = cv2.resize(frame, (224, 224))
                frame_path = os.path.join(output_action_path, f'{os.path.splitext(video_file)[0]}_{frame_idx:04d}.jpg')
                cv2.imwrite(frame_path, resized_frame)
                frame_idx += 1
            cap.release()

preprocess_videos('./UCF101', './processed_videos')
