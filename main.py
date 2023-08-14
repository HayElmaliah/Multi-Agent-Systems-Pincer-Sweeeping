from simulation.spiral_pincer import simulate as spiral_simulate
from simulation.circular_pincer import simulate as circular_simulate  # Assuming you have a function named 'simulate' in circular_pincer.py
from tkinter import Tk, Label, Entry, Button, IntVar, Spinbox, StringVar, Frame

# GUI function
def launch_gui():
    def on_submit():
        num_agents = int(num_agents_var.get())
        r_value = r_var.get()
        if selected_mode.get() == "spiral":
            spiral_simulate(num_agents, 50, r_value)  # Hardcoded R0 value as 50
        else:
            circular_simulate(num_agents, 50, r_value)
        root.quit()

    def update_r_value(*args):
        r_var.set(10 * int(num_agents_var.get()))

    def select_mode(mode):
        selected_mode.set(mode)
        if mode == "spiral":
            slide_frame.place(x=0, y=0)
            spiral_button.config(bg='#2980b9', fg='#ecf0f1')
            circular_button.config(bg='#3498db', fg='#2c3e50')
        else:
            slide_frame.place(x=100, y=0)
            circular_button.config(bg='#2980b9', fg='#ecf0f1')
            spiral_button.config(bg='#3498db', fg='#2c3e50')

    root = Tk()
    root.title("Pincer Movement Simulation")

    # Styling
    root.configure(bg='#2c3e50')  # Background color
    font_style = ("Arial", 12)
    button_font_style = ("Arial", 12, "bold")

    Label(root, text="Pincer Movement Simulation", font=("Arial", 16, "bold"), bg='#2c3e50', fg='#ecf0f1').pack(pady=20)

    Label(root, text="Number of Agents:", font=font_style, bg='#2c3e50', fg='#ecf0f1').pack(pady=10)
    num_agents_var = StringVar(value='8')
    num_agents_var.trace("w", update_r_value)
    Spinbox(root, values=('2', '4', '8'), textvariable=num_agents_var, width=5, font=font_style).pack(pady=10)

    Label(root, text="Sensor Length (r):", font=font_style, bg='#2c3e50', fg='#ecf0f1').pack(pady=10)
    r_var = IntVar(value=20)
    Entry(root, textvariable=r_var, width=10, font=font_style).pack(pady=10)

    # Mode selection
    selected_mode = StringVar(value="spiral")
    mode_frame = Frame(root, bg='#2c3e50')
    mode_frame.pack(pady=20)
    slide_frame = Frame(mode_frame, bg='#3498db', width=100, height=30)
    slide_frame.place(x=0, y=0)
    spiral_button = Button(mode_frame, text="Spiral", command=lambda: select_mode("spiral"), font=button_font_style, bg='#2980b9', fg='#ecf0f1', width=10)
    spiral_button.grid(row=0, column=0)
    circular_button = Button(mode_frame, text="Circular", command=lambda: select_mode("circular"), font=button_font_style, bg='#3498db', fg='#2c3e50', width=10)
    circular_button.grid(row=0, column=1)

    Button(root, text="Start Simulation", command=on_submit, font=button_font_style, bg='#3498db', fg='#ecf0f1').pack(pady=20)

    root.mainloop()

launch_gui()
