import numpy as np

class PID:
    def __init__(self, kp, ki, kd, dt, output_limits=(-1.0, 1.0)):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt

        self.previous_error = 0.0
        self.integral = 0.0
        self.output_limits = output_limits 

    def compute(self, setpoint, current_value):
        error = setpoint - current_value
        print(f"Error: {error:.2f}")
        self.integral += error * self.dt

        self.integral = np.clip(self.integral, self.output_limits[0], self.output_limits[1])

        derivative = (error - self.previous_error) / self.dt
        self.previous_error = error

        control = self.kp * error + self.ki * self.integral + self.kd * derivative
        control = np.clip(control, self.output_limits[0], self.output_limits[1])

        return control
    