import DE
from numba import jit
import numpy as np
import time

@jit(nopython=True)
def objective(indv):
    term1 = -20 * np.exp(-0.2 * np.sqrt(0.5 * (indv[0]**2 + indv[1]**2)))
    term2 = -np.exp(0.5 * (np.cos(2 * np.pi * indv[0]) + np.cos(2 * np.pi * indv[1])))
    value = term1 + term2 + np.e + 20
    return value

if __name__ == '__main__':

    lbound = np.array([-10,-10])
    ubound = np.array([10,10])

    total_time = 0
    num_runs = 100
    for _ in range(num_runs):
        start_time = time.time()
        score_list, solution_list = DE.parallel(objective,
                                                runs=10, popsize=100, gmax=10000, 
                                                lower_bound=lbound, upper_bound=ubound)
        end_time = time.time()
        total_time += end_time - start_time
        execution_time = end_time - start_time
    average_time = total_time / num_runs
    print(f"Average execution time over {num_runs} runs: {average_time} seconds")