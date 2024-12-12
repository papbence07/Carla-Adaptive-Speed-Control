import os
import csv

class DataLogger:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.waypoints = []
        self.pid_data = []
    
    def log_waypoint(self, x, y):
        self.waypoints.append((x, y))
    
    def log_pid_data(self, adjusted_speed, current_speed, error):
        self.pid_data.append((adjusted_speed, current_speed, error))
    
    def save_waypoints(self, filename="actual_trajectory.csv"):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["x", "y"])
            writer.writerows(self.waypoints)
    
    def save_pid_data(self, filename="pid_data.csv"):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["adjusted_speed", "current_speed", "error"])
            writer.writerows(self.pid_data)
