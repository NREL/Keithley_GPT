import DE
from numba import jit
import numpy as np
import time

def create_objective_function(voltage, current):
    """Create a customized objective function with voltage and current data."""
    @jit(nopython=True)
    def objective(indv):
        charge = 1.60e-19
        boltz = 1.38e-23
        vt = boltz * (25.0 + 273.15) / charge
        sim = indv[0] * (np.exp((voltage - current * indv[2]) / (indv[1] * vt)) - 1) + (voltage - current * indv[2]) / indv[3]
        normalized_error = ((current - sim) / (current)) ** 2
        return np.sqrt(np.sum(normalized_error) / len(voltage))
    return objective

# @jit(nopython=True)
# def objective(indv):
#     return np.power((indv[0]-2),2) + np.power((indv[1]-2),2)

# @jit(nopython=True)
# def objective(indv):
#     term1 = -20 * np.exp(-0.2 * np.sqrt(0.5 * (indv[0]**2 + indv[1]**2)))
#     term2 = -np.exp(0.5 * (np.cos(2 * np.pi * indv[0]) + np.cos(2 * np.pi * indv[1])))
#     value = term1 + term2 + np.e + 20
#     return value

if __name__ == '__main__':

    # lbound = np.array([-10,-10])
    # ubound = np.array([10,10])

    voltage, current = DE.load_raw_data("iv.txt", vmin=-2, vmax=2)    
    custom_objective = create_objective_function(voltage, current)

    lbound = np.array([1e-15, 1,  1e-6, 1e-1])
    ubound = np.array([1e-3,  10, 1e3,  1e9])

    total_time = 0
    num_runs = 100
    for _ in range(num_runs):
        start_time = time.time()
        score_list, solution_list = DE.parallel(custom_objective,
                                                runs=10, popsize=100, gmax=10000, 
                                                lower_bound=lbound, upper_bound=ubound)
        end_time = time.time()
        total_time += end_time - start_time
        execution_time = end_time - start_time
    average_time = total_time / num_runs
    print(f"Average execution time over {num_runs} runs: {average_time} seconds")