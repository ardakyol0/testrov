import cv2
import numpy as np
import json
class VideoAnalyzer:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.movement_data = []
        self.circle_data = []
    def detect_circles(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 50)
        detected = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                detected.append((x, y, r))
        return detected
    
    def detect_yellow_circles(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([30, 255, 255])
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        yellow_circles = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:
                (x, y), radius = cv2.minEnclosingCircle(contour)
                yellow_circles.append((int(x), int(y), int(radius)))
        
        return yellow_circles
    def track_movement(self, frame, prev_frame):
        gray1 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        
        corners = cv2.goodFeaturesToTrack(gray2, maxCorners=100, qualityLevel=0.01, minDistance=10)
        if corners is not None and len(corners) > 0:
            new_corners, status, error = cv2.calcOpticalFlowPyrLK(gray2, gray1, corners, None)
            good_new = new_corners[status == 1]
            good_old = corners[status == 1]
            
            if len(good_new) > 0:
                displacement = good_new - good_old
                velocity = float(np.mean(np.sqrt(displacement[:, 0]**2 + displacement[:, 1]**2)))
                direction = float(np.mean(np.arctan2(displacement[:, 1], displacement[:, 0]) * 180 / np.pi))
                return {'velocity': velocity, 'direction': direction}
        
        return {'velocity': 0.0, 'direction': 0.0}
    def analyze_video(self):
        frame_count = 0
        prev_frame = None
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            circles = self.detect_circles(frame)
            yellow_circles = self.detect_yellow_circles(frame)
            self.circle_data.append({
                'frame': frame_count, 
                'circles_count': len(circles), 
                'circles': circles,
                'yellow_circles': yellow_circles
            })
            if prev_frame is not None:
                movement = self.track_movement(frame, prev_frame)
                movement['frame'] = frame_count
                self.movement_data.append(movement)
            prev_frame = frame.copy()
            frame_count += 1
        self.cap.release()
        return {
            'video_info': {
                'path': self.video_path,
                'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': float(self.cap.get(cv2.CAP_PROP_FPS)),
                'total_frames': frame_count
            },
            'movement_data': self.movement_data,
            'circle_detection_data': self.circle_data
        }
    def save_analysis_results(self, results, output_path):
        def convert_numpy(obj):
            if hasattr(obj, 'dtype'):
                if 'int' in str(obj.dtype):
                    return int(obj)
                elif 'float' in str(obj.dtype):
                    return float(obj)
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: convert_numpy(value) for key, value in obj.items()}
            elif isinstance(obj, tuple):
                return tuple(convert_numpy(item) for item in obj)
            return obj
        
        clean_results = convert_numpy(results)
        with open(output_path, 'w') as f:
            json.dump(clean_results, f)
