import numpy as np
from ultralytics import YOLO

class Detector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.class_names = ['bike', 'motobike', 'person', 'traffic_light_green',
                            'traffic_light_orange', 'traffic_light_red', 
                            'traffic_sign_30', 'traffic_sign_60', 'traffic_sign_90', 'vehicle']

    def detect(self, frame):
        results = self.model(frame)
        detections = results[0].boxes.data
        detected_classes = []
        for detection in detections:
            x1, y1, x2, y2, conf, cls = detection.cpu().numpy()
            cls_name = self.class_names[int(cls)]
            detected_classes.append((cls_name, conf, (x1, y1, x2, y2)))
        return detected_classes

    
    def process_image(self, image):
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = array.reshape((image.height, image.width, 4))
        return array[:, :, :3]

