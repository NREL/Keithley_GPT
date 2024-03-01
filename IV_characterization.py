import os
from Keithley2400Controller import Keithley2400Controller
import DE

# ===== Keithley 2400 setup ===== #
controller = Keithley2400Controller(timeout=10000)
controller.connect()
print(controller.identify())
controller.select_panel('FRONT')
controller.set_measurement_mode(2)

voltage, current = controller.iv_sweep(source_type='VOLT', measure_type='CURR', 
                                        start_level=-1, stop_level=1, step_level=0.5, 
                                        measure_compliance=0.5, source_range=None, 
                                        measure_range=None, nplc=1)

# ===== Save IV data ===== #
iv_folder = "./iv_files"
file_path = 'iv_curve.txt'
with open(os.path.join(iv_folder,file_path), 'w') as file:
    for s, m in zip(voltage, current):
        file.write(f"{s}\t{m}\n")

# ===== Run Parameter Extraction ===== #
results_folder = "./Results"
DE.main(iv_folder, results_folder, vmin = -2, vmax = 2, 
        runs = 10, popsize = 100, gmax = 5e4, 
        temperature_celsius = 25.0)
