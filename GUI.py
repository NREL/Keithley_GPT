import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import csv
from Keithley2400GPT import Keithley2400Controller
import matplotlib.ticker as ticker

class KeithleyGUI:
    def __init__(self, master):
        self.master = master
        master.title('Keithley 2400 Controller')

        # Initialize the instrument controller
        self.instrument = None  # Initialize without creating an object yet

        # Resource name field
        self.frame_resource = ttk.Frame(master)
        self.frame_resource.grid(row=0, column=0, padx=10, pady=5, sticky='ew')
        ttk.Label(self.frame_resource, text="Resource Name:").pack(side=tk.LEFT)
        self.resource_name_entry = ttk.Entry(self.frame_resource, width=30)
        self.resource_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.resource_name_entry.insert(0, 'ASRL5::INSTR')

        # Connection Frame
        self.frame_connection = ttk.Frame(master)
        self.frame_connection.grid(row=1, column=0, padx=10, pady=5, sticky='ew')
        self.connect_button = ttk.Button(self.frame_connection, text="Connect", command=self.connect_instrument)
        self.connect_button.pack(fill=tk.X)

        # Configuration Frame (Panel and Measurement Mode)
        self.frame_config = ttk.LabelFrame(master, text="Instrument Configuration", padding=(10, 10))
        self.frame_config.grid(row=2, column=0, padx=10, pady=5, sticky='ew')
        self.panel_var = tk.BooleanVar(value=True)  # True for FRONT, False for REAR
        ttk.Radiobutton(self.frame_config, text='Front Panel', variable=self.panel_var, value=True, command=self.change_panel).grid(row=0, column=0, padx=5, pady=5)
        ttk.Radiobutton(self.frame_config, text='Rear Panel', variable=self.panel_var, value=False, command=self.change_panel).grid(row=0, column=1, padx=5, pady=5)
        self.mode_var = tk.BooleanVar(value=False)  # False for 2-wire, True for 4-wire
        ttk.Radiobutton(self.frame_config, text='2-wire Mode', variable=self.mode_var, value=False, command=self.change_mode).grid(row=1, column=0, padx=5, pady=5)
        ttk.Radiobutton(self.frame_config, text='4-wire Mode', variable=self.mode_var, value=True, command=self.change_mode).grid(row=1, column=1, padx=5, pady=5)

        # Setup Frame
        self.frame_setup = ttk.LabelFrame(master, text="Setup Parameters", padding=(10, 10))
        self.frame_setup.grid(row=3, column=0, padx=10, pady=5, sticky='ew')

        # Setup fields
        self.setup_fields = {
            'Source Type': ttk.Combobox(self.frame_setup, values=['VOLT', 'CURR'], state="readonly"),
            'Measure Type': ttk.Combobox(self.frame_setup, values=['VOLT', 'CURR'], state="readonly"),
            'Start Level': ttk.Entry(self.frame_setup),
            'Stop Level': ttk.Entry(self.frame_setup),
            'Step Level': ttk.Entry(self.frame_setup),
            'Compliance': ttk.Entry(self.frame_setup),
            'NPLC': ttk.Entry(self.frame_setup),
            'Source Delay': ttk.Entry(self.frame_setup),
            'Source Range': ttk.Entry(self.frame_setup),
            'Measure Range': ttk.Entry(self.frame_setup)
        }
        for i, (label, widget) in enumerate(self.setup_fields.items()):
            ttk.Label(self.frame_setup, text=label).grid(row=i, column=0, padx=5, pady=5)
            widget.grid(row=i, column=1, padx=5, pady=5)

        # Autorange Toggle
        self.autorange = tk.BooleanVar(value=True)
        self.autorange_check = ttk.Checkbutton(self.frame_setup, text='Auto Range', variable=self.autorange, command=self.toggle_autorange)
        self.autorange_check.grid(row=len(self.setup_fields), columnspan=2, padx=5, pady=5)
        self.toggle_autorange()  # Initialize visibility of range entries

        # Plot Area
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master)
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=5, padx=10, pady=5)

        # Log Scale Toggles
        self.log_scale_x = tk.BooleanVar()
        self.log_scale_y = tk.BooleanVar()
        self.log_frame = ttk.Frame(master)
        self.log_frame.grid(row=5, column=1, sticky='ew')
        ttk.Checkbutton(self.log_frame, text='Log Scale X', variable=self.log_scale_x, command=self.update_plot).pack(side=tk.LEFT)
        ttk.Checkbutton(self.log_frame, text='Log Scale Y', variable=self.log_scale_y, command=self.update_plot).pack(side=tk.LEFT)

        # IV Sweep Button
        self.sweep_button = ttk.Button(master, text="Perform IV Sweep", command=self.perform_iv_sweep)
        self.sweep_button.grid(row=6, column=0, padx=10, pady=5, sticky='ew')

        # Save Data Button
        self.save_button = ttk.Button(master, text="Save Data", command=self.save_data)
        self.save_button.grid(row=6, column=1, padx=10, pady=5, sticky='ew')

    def connect_instrument(self):
        resource_name = self.resource_name_entry.get()
        try:
            self.instrument = Keithley2400Controller(resource_name)
            self.instrument.connect()
            messagebox.showinfo("Connection", "Successfully connected to the instrument.")
        except Exception as e:
            messagebox.showerror("Connection Failed", str(e))

    def change_panel(self):
        # Apply panel change to the instrument if connected
        if self.instrument:
            panel = 'REAR' if not self.panel_var.get() else 'FRONT'
            self.instrument.select_panel(panel)

    def change_mode(self):
        # Apply mode change to the instrument if connected
        if self.instrument:
            mode = 4 if self.mode_var.get() else 2
            self.instrument.set_measurement_mode(mode)


    def change_panel(self):
        # Apply panel change to the instrument if connected
        if self.instrument:
            panel = 'REAR' if not self.panel_var.get() else 'FRONT'
            self.instrument.select_panel(panel)

    def change_mode(self):
        # Apply mode change to the instrument if connected
        if self.instrument:
            mode = 4 if self.mode_var.get() else 2
            self.instrument.set_measurement_mode(mode)

    def perform_iv_sweep(self):
        # Gather the setup parameters
        source_type = self.setup_fields['Source Type'].get()
        measure_type = self.setup_fields['Measure Type'].get()
        start_level = float(self.setup_fields['Start Level'].get())
        stop_level = float(self.setup_fields['Stop Level'].get())
        step_level = float(self.setup_fields['Step Level'].get())
        compliance = float(self.setup_fields['Compliance'].get())
        nplc = float(self.setup_fields['NPLC'].get())
        source_delay = float(self.setup_fields['Source Delay'].get())
        source_range = None if self.autorange.get() else float(self.setup_fields['Source Range'].get())
        measure_range = None if self.autorange.get() else float(self.setup_fields['Measure Range'].get())

        threading.Thread(target=self.async_iv_sweep, args=(source_type, measure_type, start_level, stop_level, step_level, compliance, nplc, source_delay, source_range, measure_range)).start()

    def async_iv_sweep(self, source_type, measure_type, start_level, stop_level, step_level, compliance, nplc, source_delay, source_range, measure_range):
        try:
            # Execute the IV sweep
            self.voltage, self.current = self.instrument.iv_sweep(
                source_type, measure_type, start_level, stop_level, step_level,
                compliance, source_range, measure_range, nplc, source_delay
            )
            # Update the plot
            self.master.after(0, self.update_plot)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_plot(self):
        # Determine what is being sourced and measured
        source_type = self.setup_fields['Source Type'].get()
        measure_type = self.setup_fields['Measure Type'].get()
        if source_type == 'VOLT' and measure_type == 'CURR':
            x_data, y_data = self.voltage, self.current
            x_label, y_label = 'Voltage (V)', 'Current (A)'
        else:
            x_data, y_data = self.current, self.voltage
            x_label, y_label = 'Current (A)', 'Voltage (V)'

        self.plot.clear()
        # Apply log scale if selected and adjust data to absolute values for log scale
        if self.log_scale_x.get():
            x_data = np.abs(x_data)
            self.plot.set_xscale('log')
        else:
            self.plot.set_xscale('linear')

        if self.log_scale_y.get():
            y_data = np.abs(y_data)
            self.plot.set_yscale('log')
        else:
            self.plot.set_yscale('linear')

        self.plot.plot(x_data, y_data, marker='o', linestyle='-')
        self.plot.set_xlabel(x_label)
        self.plot.set_ylabel(y_label)
        self.plot.set_title('IV Sweep Results')

        # Set formatter for automatic scientific notation
        self.plot.xaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        self.plot.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        self.plot.ticklabel_format(style='sci', axis='both', scilimits=(-2,2), useOffset=False)

        # Update the plot
        self.canvas.draw()

    def save_data(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if filepath:
            with open(filepath, 'w', newline='') as file:
                writer = csv.writer(file, delimiter='\t')
                writer.writerow(["Voltage", "Current"])
                for v, c in zip(self.voltage, self.current):
                    writer.writerow([v, c])
            messagebox.showinfo("Save File", "Data saved successfully.")

    def toggle_autorange(self):
        state = 'disabled' if self.autorange.get() else 'normal'
        self.setup_fields['Source Range'].config(state=state)
        self.setup_fields['Measure Range'].config(state=state)

if __name__ == "__main__":
    root = tk.Tk()
    app = KeithleyGUI(root)
    root.mainloop()
