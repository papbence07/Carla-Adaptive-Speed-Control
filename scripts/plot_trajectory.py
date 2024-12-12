import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from PIL import Image, ImageDraw, ImageFont, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
background_image_path = 'output/town01_topview.png'
background = Image.open(background_image_path)
image_width, image_height = background.size 

camera_position = {'x': 130, 'y': 150} 
image_extent = 50  
x_min = camera_position['x'] - image_extent 
x_max = camera_position['x'] + image_extent 
y_min = camera_position['y'] - image_extent
y_max = camera_position['y'] + image_extent

reference_trajectory = pd.read_csv('reference_trajectory_curve.csv')
actual_trajectory = pd.read_csv('actual_trajectory_curve.csv')

def transform_coordinates(df, x_min, x_max, y_min, y_max, image_width, image_height):
    df['x_transformed'] = (df['x'] - x_min) / (x_max - x_min) * image_width
    df['y_transformed'] = (df['y'] - y_min) / (y_max - y_min) * image_height
    return df

tree = KDTree(reference_trajectory[['x', 'y']])
distances, _ = tree.query(actual_trajectory[['x', 'y']])
sse = np.mean(distances)

reference_trajectory = transform_coordinates(reference_trajectory, x_min, x_max, y_min, y_max, image_width, image_height)
actual_trajectory = transform_coordinates(actual_trajectory, x_min, x_max, y_min, y_max, image_width, image_height)

image_with_points = background.copy()
draw = ImageDraw.Draw(image_with_points)

for _, row in reference_trajectory.iterrows():
    x, y = row['x_transformed'], row['y_transformed']
    draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill='blue', outline='blue')  

for _, row in actual_trajectory.iterrows():
    x, y = row['x_transformed'], row['y_transformed']
    draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill='red', outline='red')  

try:
    font = ImageFont.truetype("arial.ttf", 24)
except IOError:
    font = ImageFont.load_default()

legend_width, legend_height = 300, 150
padding = 20  

legend_x = image_width - legend_width - padding
legend_y = image_height - legend_height - padding

draw.rectangle([legend_x, legend_y, legend_x + legend_width, legend_y + legend_height], fill="white", outline="black")

draw.text((legend_x + 20, legend_y + 20), "Reference trajectory", fill="blue", font=font)
draw.text((legend_x + 20, legend_y + 60), "Actual trajectory", fill="red", font=font)
draw.text((legend_x + 20, legend_y + 100), f"Error: {sse:.2f}", fill="black", font=font)

image_with_points.save('trajectory_curves.png')
image_with_points.show()
