import numpy as np

class StanleyController:
    def __init__(self, wheelbase, default_speed, mu=0.25, k=0.01):
        self.wheelbase = wheelbase
        self.default_speed = default_speed
        self.mu = mu
        self.k = k
        self.min_turn_speed = default_speed 

    @staticmethod
    def calculate_turning_radius(waypoints, current_index):
        if current_index + 2 >= len(waypoints):
            return float('inf')  

        x1, y1 = waypoints[current_index]
        x2, y2 = waypoints[current_index + 1]
        x3, y3 = waypoints[current_index + 2]

        A = np.array([
            [x1 - x2, y1 - y2],
            [x2 - x3, y2 - y3]
        ])
        b = np.array([
            (x1**2 - x2**2 + y1**2 - y2**2) / 2,
            (x2**2 - x3**2 + y2**2 - y3**2) / 2
        ])
        try:
            center = np.linalg.solve(A, b)
            radius = np.sqrt((x1 - center[0])**2 + (y1 - center[1])**2)
            return radius
        except np.linalg.LinAlgError:
            return float('inf')  # If the line is straight, no turn exists

    def modify_target_speed(self, waypoints, vehicle_location, current_speed, vehicle_yaw):
        """
        Limits the target speed based on the turning radius and ensures that the speed
        only returns to the default value once the vehicle is aligned with the trajectory.
        The turn speed is the minimum of the calculated maximum speeds until the vehicle
        aligns with the trajectory.
        """
        closest_index = np.argmin([
            np.linalg.norm([waypoint[0] - vehicle_location.x, waypoint[1] - vehicle_location.y])
            for waypoint in waypoints
        ])

        turn_speeds = []
        for i in range(closest_index, min(closest_index + 5, len(waypoints) - 2)):  # Check 5 waypoints ahead
            radius = self.calculate_turning_radius(waypoints, i)
            if radius < float('inf'): 
                turn_speeds.append(np.sqrt(self.mu * 9.81 * radius))

        max_speed_in_turn = min(turn_speeds) if turn_speeds else self.default_speed
        self.min_turn_speed = min(self.min_turn_speed, max_speed_in_turn)

        if closest_index + 1 < len(waypoints):
            next_waypoint = waypoints[closest_index + 1]
            dx = next_waypoint[0] - vehicle_location.x
            dy = next_waypoint[1] - vehicle_location.y

            path_yaw = np.arctan2(dy, dx)
            heading_error = abs(path_yaw - vehicle_yaw)

            if heading_error < np.radians(3) and abs(dx) < 0.5 and abs(dy) < 0.5:  # Tolerance values
                self.min_turn_speed = self.default_speed  
                return self.default_speed

        return min(self.default_speed, self.min_turn_speed)
    

    def stanley_control(self, vehicle_location, vehicle_yaw, waypoints, velocity, target_speed):
        closest_distance = float('inf')
        closest_waypoint = None

        for waypoint in waypoints:
            dx = waypoint[0] - vehicle_location.x
            dy = waypoint[1] - vehicle_location.y
            distance = np.sqrt(dx**2 + dy**2)

            heading_to_waypoint = np.arctan2(dy, dx)
            if abs(heading_to_waypoint - vehicle_yaw) > np.pi / 2:
                continue

            if distance < closest_distance:
                closest_distance = distance
                closest_waypoint = waypoint

        if closest_waypoint is None:
            return 0.0, target_speed 

        # Lateral error correction
        dx = closest_waypoint[0] - vehicle_location.x
        dy = closest_waypoint[1] - vehicle_location.y
        cross_track_error = np.hypot(dx, dy)
        error_sign = np.sign(np.cross([dx, dy, 0], [np.cos(vehicle_yaw), np.sin(vehicle_yaw), 0])[-1])
        cross_track_error *= error_sign

        # Heading error calculation
        path_yaw = np.arctan2(dy, dx)
        heading_error = path_yaw - vehicle_yaw

        # Dynamically adjusted heading gain based on conditions
        if abs(heading_error) > np.radians(45) > 2.0 or velocity < 5:
            heading_gain = 0.25  # Larger gain in critical situations
        else:
            heading_gain = 0.01  # Default gain

        steer_angle = heading_gain * heading_error + np.arctan(self.k * cross_track_error / (velocity + 1e-3))
        adjusted_speed = self.modify_target_speed(waypoints, vehicle_location, velocity, vehicle_yaw)

        return steer_angle, adjusted_speed
    

    def update_default_speed(self, new_target_speed):
        self.default_speed = new_target_speed