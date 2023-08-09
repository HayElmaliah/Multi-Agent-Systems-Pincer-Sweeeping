from simulation.pincer import simulate
from tkinter import Tk, Label, Entry, Button, IntVar

# GUI function
def launch_gui():
    def on_submit():
        num_agents = num_agents_var.get()
        radius = radius_var.get()
        r_value = r_var.get()
        simulate(num_agents, radius, r_value)
        root.quit()

    root = Tk()
    root.title("Pincer Movement Simulation")

    Label(root, text="Number of Agents (even number):").pack(pady=10)
    num_agents_var = IntVar(value=4)
    Entry(root, textvariable=num_agents_var).pack(pady=10)

    Label(root, text="Radius of Circle (R0):").pack(pady=10)
    radius_var = IntVar(value=50)
    Entry(root, textvariable=radius_var).pack(pady=10)

    Label(root, text="Sensor Length (r):").pack(pady=10)
    r_var = IntVar(value=25)
    Entry(root, textvariable=r_var).pack(pady=10)

    Button(root, text="Start Simulation", command=on_submit).pack(pady=20)

    root.mainloop()

launch_gui()
