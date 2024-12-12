import carla


def setup_carla():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.load_world('Town01')
    weather = carla.WeatherParameters.ClearNoon  # Options include ClearNoon, CloudySunset, WetNoon
    world.set_weather(weather)
    blueprint_library = world.get_blueprint_library()

    # Spawn vehicle
    vehicle_bp = blueprint_library.filter('vehicle.*')[0]
    spawn_point = carla.Transform(
        carla.Location(x=92.4, y=180, z=0), carla.Rotation(pitch=0.0, yaw=-90.0, roll=0.0)
    )
    vehicle = world.spawn_actor(vehicle_bp, spawn_point)

    # Attach camera
    camera_bp = blueprint_library.find('sensor.camera.rgb')
    camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

    return world, vehicle, camera


def get_speed(vehicle):
    velocity = vehicle.get_velocity()
    speed = 3.6 * (velocity.x**2 + velocity.y**2 + velocity.z**2)**0.5  # m/s to km/h
    return speed