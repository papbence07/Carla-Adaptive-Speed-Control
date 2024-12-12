import os
import cv2
import time
import carla
import numpy as np
from datetime import datetime

from controllers.pid import PID
from detector.detector import Detector
from enviroment.data_logger import DataLogger
from controllers.stanley import StanleyController
from enviroment.carla import setup_carla, load_waypoints, get_speed


def main():
    target_speed = 40 / 3.6  # km/h -> m/s
    model_path = ""
    detector = Detector(model_path)
    pid = PID(kp=0.4, ki=0.5, kd=0.05, dt=0.2)
    lateral_controller = StanleyController(wheelbase=2.5, default_speed=target_speed, mu=0.3, k=0.01)

    results_name = datetime.today().strftime('%Y_%m_%d_%H%M%S')
    output_dir = os.path.join("results", results_name)
    output_frames_dir = os.path.join(output_dir, "frames")

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_frames_dir, exist_ok=True)

    logger = DataLogger(output_dir)

    global frame_counter
    zone_speed = target_speed
    stop = False

    frame_counter = 0
    world, vehicle, camera = setup_carla()

    csv_path = "reference_trajectory_straight.csv"
    trajectory_points = load_waypoints(csv_path)

    last_position = None 
   
    def on_image(image):
        nonlocal target_speed, zone_speed, stop, last_position
        global frame_counter

        frame = detector.process_image(image)
        frame = frame[:, :, :3].copy() 

        frame_counter += 1
        frame_path = os.path.join(output_frames_dir, f"frame_{frame_counter:05d}.png")

        detections = detector.detect(frame)
        for cls_name, conf, (x1, y1, x2, y2) in detections:
            # Filter detections with low confidence
            if conf < 0.5:
                continue

            if cls_name == "traffic_sign_30":
                target_speed = 25 / 3.6
                lateral_controller.update_default_speed(target_speed)
                zone_speed = target_speed
            elif cls_name == "traffic_sign_60":
                target_speed = 55 / 3.6
                lateral_controller.update_default_speed(target_speed)
                zone_speed = target_speed
            elif cls_name == "traffic_sign_90":
                target_speed = 85 / 3.6
                lateral_controller.update_default_speed(target_speed)
                zone_speed = target_speed
            elif cls_name == "traffic_light_red":
                target_speed = 0
                stop = True
            elif cls_name == "traffic_light_yellow":
                target_speed = 0
            elif cls_name == "traffic_light_green":
                target_speed = zone_speed
                stop = False
            else:
                continue 

            label = f"{cls_name}, Conf:{conf:.2f}"
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        location = vehicle.get_location()
        velocity = vehicle.get_velocity()
        yaw = np.radians(vehicle.get_transform().rotation.yaw)
        speed = np.sqrt(velocity.x**2 + velocity.y**2)

        steer, adjusted_speed = lateral_controller.stanley_control(vehicle.get_location(), yaw, trajectory_points, speed, target_speed)
        accel_pid = pid.compute(adjusted_speed, speed)

        accel = accel_pid
        if stop:
            accel = -2.0

        control = carla.VehicleControl()
        control.steer = steer
        if accel > 0:
            control.throttle = min(accel, 1.0)
            control.brake = 0.0
        else:
            control.throttle = 0.0
            control.brake = max(-accel, 2.0)
        vehicle.apply_control(control)

        current_position = (location.x, location.y)
        if last_position is None or (current_position != last_position and speed > 0.1):
            logger.log_waypoint(location.x, location.y)
            last_position = current_position

        error = target_speed - speed
        logger.log_pid_data(target_speed, speed, error)

        current_speed = get_speed(vehicle)
        cv2.putText(frame, f"Target Speed: {target_speed*3.6:.2f} km/h", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Current Speed: {current_speed:.2f} km/h", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"x={location.x:.2f}, y={location.y:.2f}, z={location.z:.2f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imwrite(frame_path, frame)
        cv2.imshow("Traffic Sign Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return
        
    camera.listen(on_image)

    try:
        while True:
            time.sleep(0.25)
    except KeyboardInterrupt:
        print("Quit...")
    finally:
        logger.save_waypoints()
        logger.save_pid_data()
        camera.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
