import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def point_on_line(px, py, start, end, buffer=0.1):
    # Extract coordinates
    x1, y1 = start
    x2, y2 = end

    # Vector from start to end (i.e., the sensor line)
    vec_line = [x2 - x1, y2 - y1]
    mag_vec_line = np.sqrt(vec_line[0]**2 + vec_line[1]**2)
    vec_line = [vec_line[0]/mag_vec_line, vec_line[1]/mag_vec_line]

    # Vector from start to point (i.e., from sweeper to evader)
    vec_point = [px - x1, py - y1]
    mag_vec_point = np.sqrt(vec_point[0]**2 + vec_point[1]**2)
    vec_point = [vec_point[0]/mag_vec_point, vec_point[1]/mag_vec_point]

    # Dot product
    dot_product = vec_line[0]*vec_point[0] + vec_line[1]*vec_point[1]

    # Check if vectors are parallel (either in the same or opposite direction) 
    # and distance is less than r/n with a buffer
    if (np.isclose(dot_product, 1, atol=buffer) or np.isclose(dot_product, -1, atol=buffer)) and mag_vec_point <= (mag_vec_line / 2 + buffer):
        return True
    return False

def simulate(n_sweepers, R0, r):
    step_size = 0.5
    initial_separation = True
    sensor_length = 2 * r / n_sweepers

    # Initialize sweepers
    pair_angles = np.linspace(0, 2 * np.pi, n_sweepers // 2, endpoint=False)
    sweeper_angles = []
    for angle in pair_angles:
        sweeper_angles.append(angle)
        sweeper_angles.append(angle)

    sweeper_x = R0 * np.cos(sweeper_angles)
    sweeper_y = R0 * np.sin(sweeper_angles)
    sweeper_directions = np.array([1 if i % 2 == 0 else -1 for i in range(n_sweepers)])

    # Initialize evaders
    n_evaders = 10
    evader_angles = np.random.uniform(0, 2 * np.pi, n_evaders)
    evader_radii = np.random.uniform(0, R0, n_evaders)
    evader_x = evader_radii * np.cos(evader_angles)
    evader_y = evader_radii * np.sin(evader_angles)
    evader_colors = ["red"] * n_evaders

    fig, ax = plt.subplots()
    ax.set_xlim(-R0-10, R0+10)
    ax.set_ylim(-R0-10, R0+10)
    ax.set_aspect('equal', 'box')

    sweepers, = ax.plot(sweeper_x, sweeper_y, 'bo')
    evader_colors = [0] * n_evaders  # 0 for red, 2 for green
    evaders = ax.scatter(evader_x, evader_y, c=evader_colors, cmap=plt.cm.RdYlGn, vmin=0, vmax=2)
    sensors = [ax.plot([], [], 'k-')[0] for _ in range(n_sweepers)]

    def init():
        """Initialize the animation with default data."""
        sweepers.set_data(sweeper_x, sweeper_y)
        evaders.set_offsets(np.c_[evader_x, evader_y])
        for i in range(n_sweepers):
            angle = np.arctan2(sweeper_y[i], sweeper_x[i])
            start_x = sweeper_x[i] - (sensor_length / 2) * np.cos(angle)
            start_y = sweeper_y[i] - (sensor_length / 2) * np.sin(angle)
            end_x = sweeper_x[i] + (sensor_length / 2) * np.cos(angle)
            end_y = sweeper_y[i] + (sensor_length / 2) * np.sin(angle)
            sensors[i].set_data([start_x, end_x], [start_y, end_y])
        return [sweepers, evaders] + sensors

    def update(frame):
        nonlocal sweeper_x, sweeper_y, R0, initial_separation

        if initial_separation:
            for i in range(n_sweepers):
                angle = np.arctan2(sweeper_y[i], sweeper_x[i])
                angle += sweeper_directions[i] * step_size / R0
                sweeper_x[i] = R0 * np.cos(angle)
                sweeper_y[i] = R0 * np.sin(angle)
            initial_separation = False
            return [sweepers, evaders] + sensors

        # Move sweepers along the circumference
        for i in range(n_sweepers):
            angle = np.arctan2(sweeper_y[i], sweeper_x[i])
            angle += sweeper_directions[i] * step_size / R0
            sweeper_x[i] = R0 * np.cos(angle)
            sweeper_y[i] = R0 * np.sin(angle)

        # Check for sweepers meeting and adjust directions and radius
        for i in range(n_sweepers):
            for j in range(n_sweepers):
                if i != j:
                    dist = np.sqrt((sweeper_x[j] - sweeper_x[i])**2 + (sweeper_y[j] - sweeper_y[i])**2)
                    if dist < 2 * step_size:
                        sweeper_directions[i] *= -1
                        R0 -= step_size

        # Update evader colors based on proximity to sweepers' sensors
        for i in range(n_evaders):
            for j in range(n_sweepers):
                start = (sensors[j].get_xdata()[0], sensors[j].get_ydata()[0])
                end = (sensors[j].get_xdata()[1], sensors[j].get_ydata()[1])
                if point_on_line(evader_x[i], evader_y[i], start, end, buffer=((r/n_sweepers)*0.03)) and (np.sqrt((evader_x[i]-sweeper_x[j])**2 + (evader_y[i]-sweeper_y[j])**2)) <= ((r/n_sweepers)+((r/n_sweepers)*0.03)):
                    evader_colors[i] = 2  # 2 for green

        move_mask = [color == 0 for color in evader_colors]
        if np.any(move_mask):
            evader_x[move_mask] += np.random.uniform(-1, 1, np.sum(move_mask))
            evader_y[move_mask] += np.random.uniform(-1, 1, np.sum(move_mask))

        # Update plot data
        sweepers.set_data(sweeper_x, sweeper_y)
        evaders.set_offsets(np.c_[evader_x, evader_y])
        evaders.set_array(np.array(evader_colors))

        # Update sensors
        for i in range(n_sweepers):
            angle = np.arctan2(sweeper_y[i], sweeper_x[i])
            start_x = sweeper_x[i] - (sensor_length / 2) * np.cos(angle)
            start_y = sweeper_y[i] - (sensor_length / 2) * np.sin(angle)
            end_x = sweeper_x[i] + (sensor_length / 2) * np.cos(angle)
            end_y = sweeper_y[i] + (sensor_length / 2) * np.sin(angle)
            sensors[i].set_data([start_x, end_x], [start_y, end_y])

        return [sweepers, evaders] + sensors

    ani = FuncAnimation(fig, update, frames=360, init_func=init, repeat=True, blit=True)
    plt.show()
