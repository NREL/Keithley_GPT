import os
from Keithley2400GPT import Keithley2400Controller
from matplotlib import pyplot as plt
import numpy as np

# ===== Keithley 2400 setup ===== #
controller = Keithley2400Controller(timeout=25000)
controller.connect()
controller.select_panel('FRONT')
controller.set_measurement_mode(2)

voltage, current = controller.iv_sweep(source_type='VOLT', measure_type='CURR', 
                                        start_level=2.0, stop_level=-10.0, step_level=-0.1,
                                        measure_compliance=0.1, source_range=None, 
                                        measure_range=None, nplc=1)

plt.figure(figsize=(10, 6))
plt.plot(np.array(voltage), np.abs(np.array(current)), marker='o')
plt.yscale('log')
plt.show()

# ===== Save IV data ===== #
iv_folder = "./D2/RT"
file_path = 'iv_curve.txt'
os.makedirs(iv_folder, exist_ok=True)
with open(os.path.join(iv_folder,file_path), 'w') as file:
    for s, m in zip(voltage, current):
        file.write(f"{s}\t{m}\n")


# # ===== Run Parameter Extraction ===== #
# results_folder = "./Results"
# DE.main(iv_folder, results_folder, vmin = -2, vmax = 2, 
#         runs = 10, popsize = 100, gmax = 5e4, 
#         temperature_celsius = 25.0)
