import carla
import time

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.load_world('Town01')
weather = carla.WeatherParameters.ClearNoon 
world.set_weather(weather)

blueprint_library = world.get_blueprint_library()
camera_bp = blueprint_library.find('sensor.camera.rgb')

# Set top view
camera_bp.set_attribute('image_size_x', '1920')  
camera_bp.set_attribute('image_size_y', '1080')  
camera_bp.set_attribute('fov', '90')  

camera_transform = carla.Transform(
    carla.Location(x=130, y=150, z=50), 
    carla.Rotation(yaw=-90,pitch=-90)  
)

camera = world.spawn_actor(camera_bp, camera_transform)

def save_image(image):
    image.save_to_disk('output/%06d.png' % image.frame)

camera.listen(save_image)

try:
    time.sleep(1) 
finally:
    camera.stop()
    camera.destroy()
