import DE
from numba import jit
import numpy as np

def create_objective_function(voltage, current):
    """Create a customized objective function with fixed voltage and current."""
    @jit(nopython=True)
    def objective(indv):
        charge = 1.60e-19
        boltz = 1.38e-23
        vt = boltz * (25.0 + 273.15) / charge
        sim = indv[0] * (np.exp((voltage - current * indv[2]) / (indv[1] * vt)) - 1) + (voltage - current * indv[2]) / indv[3]
        normalized_error = ((current - sim) / (current)) ** 2
        return np.sqrt(np.sum(normalized_error) / len(voltage))
    return objective

voltage, current = DE.load_raw_data("./", "test.txt", vmin=-2, vmax=2)    
custom_objective = create_objective_function(voltage, current)

# @jit(nopython=True)
# def objective(indv):
#     return np.power((indv[0]-2),2) + np.power((indv[1]-2),2)


if __name__ == '__main__':

    # lbound = np.array([-5,-5])
    # ubound = np.array([5,5])    

    lbound = np.array([1e-15, 1,  1e-6, 1e-1])
    ubound = np.array([1e-3,  10, 1e3,  1e9])

    score_list, solution_list = DE.parallel(custom_objective,runs=2, popsize=10, gmax=1000, 
                                         lower_bound=lbound, upper_bound=ubound)
    print(solution_list)