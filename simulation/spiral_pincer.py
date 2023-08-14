import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# def calculate_angle(x, y):
#     """Calculate the angle of a point with respect to the center of the circle."""
#     return np.arctan2(y, x)

# def are_approximately_equal_angles(angle1, angle2, threshold=0.1):
#     """Check if two angles are approximately equal."""
#     diff = np.abs(angle1 - angle2)
#     return np.isclose(diff, 0, atol=threshold)

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
    # Define the constant evader velocity Vt
    pace = n_sweepers**2 if n_sweepers > 2 else n_sweepers**4
    Vt = 1 / pace  # You can adjust this value as needed
    # Vt = 1.0
    Vs = Vt * np.sqrt((((2 * np.pi / n_sweepers)**2) / (np.log((R0 + r/n_sweepers) / (R0 - r/n_sweepers))**2)) + 1) + 0.1

    def calculate_delta(Ri):
        return (Vt / (Vs + Vt)) * ((r / n_sweepers) * (1 + np.exp((2 * np.pi * Vt) / (n_sweepers * np.sqrt(Vs**2 - Vt**2)))) + Ri * (1 - np.exp((2 * np.pi * Vt) / (n_sweepers * np.sqrt(Vs**2 - Vt**2)))))
    
    delta = calculate_delta(R0)
    sensor_length = 2 * r / n_sweepers

    # Initialize sweepers
    pair_angles = np.linspace(0, 2 * np.pi, n_sweepers // 2, endpoint=False) + np.pi / 2
    sweeper_angles = []
    for angle in pair_angles:
        sweeper_angles.append(angle)
        sweeper_angles.append(angle - 0.01)

    sweeper_x = R0 * np.cos(sweeper_angles)
    sweeper_y = R0 * np.sin(sweeper_angles)
    sweeper_directions = np.array([1 if i % 2 == 0 else -1 for i in range(n_sweepers)])

    first_sweeper_angle = pair_angles[0]
    sorted_sweepers_angles = sorted(sweeper_angles, reverse=False)
    first_sweeper_angle_index = sorted_sweepers_angles.index(first_sweeper_angle)
    sorted_index_of_zero_sweeper_pair = (first_sweeper_angle_index + 1) % len(sorted_sweepers_angles)
    zero_sweeper_pair_angle = sorted_sweepers_angles[sorted_index_of_zero_sweeper_pair]
    index_of_zero_sweeper_pair = sweeper_angles.index(zero_sweeper_pair_angle)

    sweeper_history_x = [[] for _ in range(n_sweepers)]
    sweeper_history_y = [[] for _ in range(n_sweepers)]

    # Initialize evaders
    n_evaders = 10
    evader_angles = np.random.uniform(0, 2 * np.pi, n_evaders)
    evader_radii = np.random.uniform(0, R0 - r/n_sweepers, n_evaders) # for some reason this way we get them to start at R0 (fix of +r/n deviation)
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
    history_lines = [ax.plot([], [], 'k-', linewidth=0.5)[0] for _ in range(n_sweepers)]

    # Add a flag to indicate when the animation should stop
    animation_should_stop = False

    # Introduce a cumulative_theta list to keep track of the cumulative change in angle for each sweeper
    cumulative_theta = [0] * n_sweepers

    initial_separation = True

    def init():
        """Initialize the animation with default data."""
        nonlocal animation_should_stop
        sweepers.set_data(sweeper_x, sweeper_y)
        evaders.set_offsets(np.c_[evader_x, evader_y])
        for i in range(n_sweepers):
            angle = np.arctan2(sweeper_y[i], sweeper_x[i])
            start_x = sweeper_x[i]
            start_y = sweeper_y[i]
            end_x = sweeper_x[i] - sensor_length * np.cos(angle)
            end_y = sweeper_y[i] - sensor_length * np.sin(angle)
            sensors[i].set_data([start_x, end_x], [start_y, end_y])
        return [sweepers, evaders] + sensors

    time_counter_radius = 0
    time_counter_angle = 0

    def update(frame):
        nonlocal sweeper_x, sweeper_y, R0, Vs, delta, animation_should_stop, cumulative_theta, sweeper_history_x, sweeper_history_y, history_lines, initial_separation, time_counter_radius, time_counter_angle

        # If the animation should stop, just return the current state
        if animation_should_stop:
            return [sweepers, evaders] + sensors

        # Move sweepers along the spiral
        for i in range(n_sweepers):
            # Calculate the angle theta(t_theta) using the given formula
            angle = np.arctan2(sweeper_y[i], sweeper_x[i])
            angle += sweeper_directions[i] * time_counter_angle * (Vs / R0) * (1 / pace)
            if angle > np.pi:
                angle -= 2*np.pi
            if angle < -np.pi:
                angle += 2*np.pi
            # Calculate the updated radius Rs(t_theta) for the spiral movement
            Rs_t_theta = Vt * time_counter_radius + R0 - r/n_sweepers
            # Update the sweeper positions based on the updated radius and angle
            sweeper_x[i] = Rs_t_theta * np.cos(angle)
            sweeper_y[i] = Rs_t_theta * np.sin(angle)
        time_counter_radius += 1
        time_counter_angle += 1

        for i in range(n_sweepers):
            sweeper_history_x[i].append(sweeper_x[i])
            sweeper_history_y[i].append(sweeper_y[i])

        # Check for sweepers meeting and adjust directions and radius
        if time_counter_angle > (r / n_sweepers):
            for i in range(n_sweepers):
                # angle_i = calculate_angle(sweeper_x[i], sweeper_y[i])
                for j in range(n_sweepers):
                    if i != j:
                        angle_0 = np.arctan2(sweeper_y[0], sweeper_x[0])
                        if (n_sweepers != 2 and sweeper_directions[0] == 1 and np.isclose(angle_0, (sweeper_angles[0] + sweeper_angles[index_of_zero_sweeper_pair])/2, atol=0.05)) \
                                or (n_sweepers != 2 and sweeper_directions[0] == -1 and np.isclose(angle_0, sweeper_angles[0], atol=0.05)) \
                                or (n_sweepers == 2 and sweeper_directions[0] == 1 and np.isclose(np.abs(angle_0 - (sweeper_angles[index_of_zero_sweeper_pair] + np.pi)) % (2*np.pi), 0, atol=0.1)) \
                                or (n_sweepers == 2 and sweeper_directions[0] == -1 and np.isclose(np.abs(angle_0 - sweeper_angles[index_of_zero_sweeper_pair]) % (2*np.pi), 0, atol=0.1)):
                            R0 -= delta
                            delta = calculate_delta(R0)
                            time_counter_radius = 0
                            time_counter_angle = 0
                            for i in range(n_sweepers):
                                sweeper_directions[i] *= -1

        if R0 <= 2*r/n_sweepers:
            animation_should_stop = True
            return [sweepers, evaders] + sensors

        # Update evader colors based on proximity to sweepers' sensors
        for i in range(n_evaders):
            for j in range(n_sweepers):
                start = (sensors[j].get_xdata()[0], sensors[j].get_ydata()[0])
                end = (sensors[j].get_xdata()[1], sensors[j].get_ydata()[1])
                if point_on_line(evader_x[i], evader_y[i], start, end, buffer=((2*r/n_sweepers))) and (np.sqrt((evader_x[i]-sweeper_x[j])**2 + (evader_y[i]-sweeper_y[j])**2)) <= ((2*r/n_sweepers)*1.1):
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
            start_x = sweeper_x[i]
            start_y = sweeper_y[i]
            end_x = sweeper_x[i] - sensor_length * np.cos(angle)
            end_y = sweeper_y[i] - sensor_length * np.sin(angle)
            sensors[i].set_data([start_x, end_x], [start_y, end_y])

        for i in range(n_sweepers):
            history_lines[i].set_data(sweeper_history_x[i], sweeper_history_y[i])

        return [sweepers, evaders] + sensors + history_lines

    ani = FuncAnimation(fig, update, frames=360, init_func=init, repeat=True, blit=True, interval=200/pace)
    # ani = FuncAnimation(fig, update, frames=360, init_func=init, repeat=True, blit=True)
    plt.show()
