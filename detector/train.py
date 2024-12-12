from ultralytics import YOLO


def main():
    model = YOLO('yolov8n.yaml') # Create a new YOLO model from scratch

    model.train(data='data/data.yaml', epochs=150, optimizer='Adam', cos_lr=True, cache=True, augment=True, batch=64)


if __name__ == '__main__':
   main()
