import pandas as pd
import matplotlib.pyplot as plt

def plot_pid_data(csv_path, output_path="pid_plot.png"):
    data = pd.read_csv(csv_path)

    time = [i * 0.25 for i in range(len(data))] 

    data["adjusted_speed_kmh"] = data["adjusted_speed"] * 3.6
    data["current_speed_kmh"] = data["current_speed"] * 3.6
    data["error_kmh"] = data["error"] * 3.6


    fig, ax = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax[0].plot(time, data["adjusted_speed_kmh"], label="Adjusted Speed (km/h)")
    ax[0].plot(time, data["current_speed_kmh"], label="Current Speed (km/h)")
    ax[0].set_title("PID Speeds Over Time")
    ax[0].set_ylabel("Speed (km/h)")
    ax[0].legend()
    ax[0].grid()

    ax[1].plot(time, data["error_kmh"], label="Error (km/h)", color="red")
    ax[1].set_title("PID Error Over Time")
    ax[1].set_xlabel("Time (s)")
    ax[1].set_ylabel("Error (km/h)")
    ax[1].legend()
    ax[1].grid()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Plot saved to {output_path}")
    plt.show()

csv_path = "pid_data.csv"  
output_path = "pid_plot_with_error.png" 
plot_pid_data(csv_path, output_path)
