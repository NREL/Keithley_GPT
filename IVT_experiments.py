import McAllister
from Keithley2400GPT import Keithley2400Controller
from matplotlib import pyplot as plt
import numpy as np
from matplotlib import pyplot as plt
import os

# Create instrument instances
# mcallister = McAllister(host='169.254.160.136', port=502)
# keithley = Keithley2400Controller(timeout=25000)

# # Instrument setup
# mcallister.connect()
# mcallister.enable_remote_operation(enable=True)
# mcallister.enable_master(enable=True)

keithley = Keithley2400Controller(timeout=50000)
keithley.connect()
keithley.select_panel('FRONT')
keithley.set_measurement_mode(2)

# setpoint = 100.0  # Target temperature
# reach_result = mcallister.check_temperature_reach(setpoint)
# if reach_result:
#     stability_result, stable_temp = mcallister.check_temperature_stability(setpoint)
#     if stability_result:
#         print(f"Temperature stabilized at {stable_temp}.")
#     else:
#         print("Failed to stabilize temperature within timeout.")
# else:
#     print("Proceeding to stability check despite not reaching setpoint within timeout.")
#     stability_result, stable_temp = mcallister.check_temperature_stability(setpoint)
#     if stability_result:
#         print(f"Temperature stabilized at {stable_temp}.")
#     else:
#         print("Failed to stabilize temperature.")

# IV sweep
voltage, current = keithley.iv_sweep(source_type='VOLT', measure_type='CURR', 
                                        start_level=5.0, stop_level=-10.0, step_level=-0.1,
                                        measure_compliance=0.2, source_range=None, 
                                        measure_range=None, nplc=1)

plt.figure(figsize=(10, 6))
plt.plot(np.array(voltage), np.abs(np.array(current)), marker='o')
plt.yscale('log')
plt.show()

# ===== Save IV data ===== #
iv_folder = "./D2"
file_path = f'iv_curve_550.txt'
os.makedirs(iv_folder, exist_ok=True)
with open(os.path.join(iv_folder,file_path), 'w') as file:
    for s, m in zip(voltage, current):
        file.write(f"{s}\t{m}\n")


# Disable remote operation and power and close the connection
#mcallister.enable_master(enable=False)
#mcallister.enable_remote_operation(enable=False)
#mcallister.close()
