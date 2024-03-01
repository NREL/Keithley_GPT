import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyvisa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from Keithley2400Controller import Keithley2400Controller

# Assuming the Keithley2400Controller class is defined as provided earlier
# Make sure to include the Keithley2400Controller class definition above this code

class Keithley2400GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Keithley 2400 Controller")
        self.geometry("1280x1000")

        self.controller = Keithley2400Controller()
        
        # Create GUI components
        self.create_widgets()

    def create_widgets(self):
        # Connection frame
        connection_frame = ttk.Frame(self)
        connection_frame.pack(fill='x', padx=10, pady=5)

        # Initialization of variables before they are used
        self.source_type_var = tk.StringVar(value='VOLT')
        self.measure_type_var = tk.StringVar(value='CURR')
        self.start_level_var = tk.DoubleVar(value=0)
        self.stop_level_var = tk.DoubleVar(value=1)
        self.step_level_var = tk.DoubleVar(value=0.1)
        self.compliance_var = tk.DoubleVar(value=0.1)
        self.source_range_var = tk.DoubleVar(value=0.1)  # Corrected initialization
        self.measure_range_var = tk.DoubleVar(value=0.1)  # Corrected initialization
        self.nplc_var = tk.DoubleVar(value=1)
        self.source_delay_var = tk.DoubleVar(value=0.1)
        self.auto_range_var = tk.BooleanVar(value=True)        

        ttk.Label(connection_frame, text="Resource Name:").pack(side='left')
        self.resource_name_var = tk.StringVar(value='ASRL5::INSTR')
        resource_name_entry = ttk.Entry(connection_frame, textvariable=self.resource_name_var)
        resource_name_entry.pack(side='left', padx=5)
        
        connect_button = ttk.Button(connection_frame, text="Connect", command=self.connect)
        connect_button.pack(side='left', padx=5)

        # Panel selection
        panel_frame = ttk.LabelFrame(self, text="Select Panel")
        panel_frame.pack(fill='x', padx=10, pady=5, expand=True)
        
        self.panel_var = tk.StringVar(value='FRONT')
        front_radio = ttk.Radiobutton(panel_frame, text="Front", variable=self.panel_var, value='FRONT')
        front_radio.pack(side='left', padx=5)
        rear_radio = ttk.Radiobutton(panel_frame, text="Rear", variable=self.panel_var, value='REAR')
        rear_radio.pack(side='left', padx=5)
        
        panel_select_button = ttk.Button(panel_frame, text="Select", command=self.select_panel)
        panel_select_button.pack(side='left', padx=5)

        # Measurement mode
        mode_frame = ttk.LabelFrame(self, text="Set Measurement Mode")
        mode_frame.pack(fill='x', padx=10, pady=5, expand=True)

        self.mode_var = tk.IntVar(value=2)
        two_wire_radio = ttk.Radiobutton(mode_frame, text="2-wire", variable=self.mode_var, value=2)
        two_wire_radio.pack(side='left', padx=5)
        four_wire_radio = ttk.Radiobutton(mode_frame, text="4-wire", variable=self.mode_var, value=4)
        four_wire_radio.pack(side='left', padx=5)

        mode_select_button = ttk.Button(mode_frame, text="Set Mode", command=self.set_measurement_mode)
        mode_select_button.pack(side='left', padx=5)

        # IV Sweep settings (expanded)
        sweep_frame = ttk.LabelFrame(self, text="IV Sweep Settings")
        sweep_frame.pack(fill='x', padx=10, pady=5, expand=True)

        # Source and Measure Type
        ttk.Label(sweep_frame, text="Source Type:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.source_type_var = tk.StringVar(value='VOLT')
        ttk.Combobox(sweep_frame, textvariable=self.source_type_var, values=('VOLT', 'CURR')).grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(sweep_frame, text="Measure Type:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.measure_type_var = tk.StringVar(value='CURR')
        ttk.Combobox(sweep_frame, textvariable=self.measure_type_var, values=('VOLT', 'CURR')).grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        # Start, Stop, Step Levels
        ttk.Label(sweep_frame, text="Start Level:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.start_level_var = tk.DoubleVar(value=0)
        ttk.Entry(sweep_frame, textvariable=self.start_level_var).grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(sweep_frame, text="Stop Level:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.stop_level_var = tk.DoubleVar(value=1)
        ttk.Entry(sweep_frame, textvariable=self.stop_level_var).grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(sweep_frame, text="Step Level:").grid(row=4, column=0, padx=5, pady=5, sticky='w')
        self.step_level_var = tk.DoubleVar(value=0.1)
        ttk.Entry(sweep_frame, textvariable=self.step_level_var).grid(row=4, column=1, padx=5, pady=5, sticky='ew')

        # Compliance, Range, NPLC, Delay
        ttk.Label(sweep_frame, text="Compliance:").grid(row=5, column=0, padx=5, pady=5, sticky='w')
        self.compliance_var = tk.DoubleVar(value=0.1)
        ttk.Entry(sweep_frame, textvariable=self.compliance_var).grid(row=5, column=1, padx=5, pady=5, sticky='ew')

        # Auto Range toggle and related entries
        self.auto_range_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(sweep_frame, text="Auto Range", variable=self.auto_range_var).grid(row=6, columnspan=2, padx=5, pady=5, sticky='w')

        ttk.Label(sweep_frame, text="Source Range:").grid(row=7, column=0, padx=5, pady=5, sticky='w')
        self.source_range_entry = ttk.Entry(sweep_frame, textvariable=self.source_range_var, state='disabled')
        self.source_range_entry.grid(row=7, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(sweep_frame, text="Measure Range:").grid(row=8, column=0, padx=5, pady=5, sticky='w')
        self.measure_range_entry = ttk.Entry(sweep_frame, textvariable=self.measure_range_var, state='disabled')
        self.measure_range_entry.grid(row=8, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(sweep_frame, text="NPLC:").grid(row=9, column=0, padx=5, pady=5, sticky='w')
        self.nplc_var = tk.DoubleVar(value=1)
        ttk.Entry(sweep_frame, textvariable=self.nplc_var).grid(row=9, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(sweep_frame, text="Source Delay:").grid(row=10, column=0, padx=5, pady=5, sticky='w')
        self.source_delay_var = tk.DoubleVar(value=0.1)
        ttk.Entry(sweep_frame, textvariable=self.source_delay_var).grid(row=10, column=1, padx=5, pady=5, sticky='ew')

        # Auto Range toggle
        self.auto_range_var.trace_add("write", self.toggle_range_state)

        # Perform IV Sweep Button
        ttk.Button(sweep_frame, text="Perform IV Sweep", command=self.perform_iv_sweep).grid(row=11, columnspan=2, padx=5, pady=5, sticky='ew')

        # Plot area
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.plot = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Save data button
        save_data_button = ttk.Button(self, text="Save Data", command=self.save_data)
        save_data_button.pack(side='bottom', padx=5, pady=5)

        # Y-scale toggle
        self.log_scale_var = tk.BooleanVar(value=False)  # False = Linear, True = Log
        log_scale_checkbutton = ttk.Checkbutton(self, text="Log Scale Y-axis", variable=self.log_scale_var, command=self.toggle_y_scale)
        log_scale_checkbutton.pack()

    def toggle_y_scale(self):
        # Check the current state of the log_scale_var to determine the scale
        if self.log_scale_var.get():
            self.plot.set_yscale("log")
        else:
            self.plot.set_yscale("linear")
        
        # Refresh the plot
        self.canvas.draw()

    def toggle_range_state(self, *args):
        if self.auto_range_var.get():
            self.source_range_entry.configure(state='disabled')
            self.measure_range_entry.configure(state='disabled')
        else:
            self.source_range_entry.configure(state='normal')
            self.measure_range_entry.configure(state='normal')     

    def connect(self):
        try:
            self.controller.resource_name = self.resource_name_var.get()
            self.controller.connect()
            messagebox.showinfo("Connection", "Connected to Keithley 2400.")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def select_panel(self):
        try:
            panel = self.panel_var.get()
            self.controller.select_panel(panel)
            messagebox.showinfo("Panel Selection", f"{panel} panel selected.")
        except Exception as e:
            messagebox.showerror("Panel Selection Error", str(e))

    def set_measurement_mode(self):
        try:
            mode = self.mode_var.get()
            self.controller.set_measurement_mode(mode)
            messagebox.showinfo("Measurement Mode", f"{mode}-wire mode set.")
        except Exception as e:
            messagebox.showerror("Measurement Mode Error", str(e))

    def perform_iv_sweep(self):
        try:
            # Example call to the IV sweep method - adjust parameters as needed
            self.voltage, self.current = self.controller.iv_sweep(
                source_type=self.source_type_var.get(), 
                measure_type=self.measure_type_var.get(), 
                start_level=self.start_level_var.get(), 
                stop_level=self.stop_level_var.get(), 
                step_level=self.step_level_var.get(), 
                measure_compliance=self.compliance_var.get(),
                source_range=None if self.auto_range_var.get() else self.source_range_var.get(),
                measure_range=None if self.auto_range_var.get() else self.measure_range_var.get(),
                nplc=self.nplc_var.get(),
                source_delay=self.source_delay_var.get(),
                ovp=20  # Assuming a fixed OVP value for simplicity
            )
            self.plot_data(self.voltage, self.current)
        except Exception as e:
            messagebox.showerror("IV Sweep Error", str(e))

    def plot_data(self, x, y):
        # Clear the current plot
        self.plot.clear()

        # Determine the axis labels based on the source and measure types
        x_label = 'Voltage (V)' if self.source_type_var.get() == 'VOLT' else 'Current (A)'
        y_label = 'Current (A)' if self.measure_type_var.get() == 'CURR' else 'Voltage (V)'

        # Plot the data
        self.plot.plot(x, y, marker='o', linestyle='-')
        self.plot.set_xlabel(x_label)
        self.plot.set_ylabel(y_label)

        # You can adjust the title dynamically as well if needed
        plot_title = f'{self.measure_type_var.get()} vs. {self.source_type_var.get()}'
        self.plot.set_title(plot_title)

        # Apply the current y-scale setting
        self.toggle_y_scale()

        # Redraw the canvas to display the updated plot
        self.canvas.draw()

    def save_data(self):
        # Check if the data exists
        if hasattr(self, 'voltage') and hasattr(self, 'current'):
            file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if file_path:
                with open(file_path, 'w') as file:
                    for v, i in zip(self.voltage, self.current):
                        file.write(f"{v}, {i}\n")
                messagebox.showinfo("Save Data", "Data saved successfully.")
        else:
            messagebox.showerror("Save Data Error", "No data to save. Please perform an IV sweep first.")


if __name__ == "__main__":
    app = Keithley2400GUI()
    app.mainloop()
