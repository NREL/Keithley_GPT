import numpy as np
from numba import jit, prange
from numpy import random
from math import log10
import os
from os import listdir
from os.path import isfile, join
from datetime import datetime
import sys

@jit(nopython=True)
def differential_evolution(popsize, gmax, lbound, ubound):

    # ---  Initialize arrays --- #
    dimension = len(lbound)
    pop = np.zeros((popsize, dimension))
    for j in range(dimension):
        if lbound[j] < 0:
            pop[:, j] = random.uniform(lbound[j], ubound[j], popsize)
        else:
            pop[:, j] = 10 ** random.uniform(log10(lbound[j]), log10(ubound[j]), popsize)
    score = np.zeros((popsize, 1))
    donor = np.zeros((popsize, dimension - 2))
    trial = np.zeros((popsize, dimension - 2))

    # --- Initial best individual --- #
    for i in range(popsize):
        score[i] = objective(pop[i, :])
    best_index = np.argmin(score)

    # --- Differential Evolution loop --- #
    for generation in range(gmax):
        for i in range(popsize):

            # --- Selection of random individuals, excluding current individual --- #
            candidates = np.arange(popsize)
            candidates = np.delete(candidates, i)
            random_index = random.choice(candidates, 3, replace=False)

            # --- Mutation --- #
            donor[i, :] = pop[i, :-2] \
                + pop[i, dimension - 2] * (pop[best_index, :-2] - pop[i, :-2]) \
                + pop[i, dimension - 2] * (pop[random_index[0], :-2] - pop[random_index[1], :-2])  # current-to-best/1
            
            # --- Crossover --- #
            jrand = random.choice(dimension - 2)
            for j in range(dimension - 2):
                random_number = random.rand()
                if random_number <= pop[i, dimension - 1] or j == jrand:
                    trial[i, j] = donor[i, j]
                else:
                    trial[i, j] = pop[i, j]

            # --- Penalty function --- #
            for j in range(dimension - 2):
                if trial[i, j] > ubound[j] or trial[i, j] < lbound[j]:
                    if lbound[j] >= 0 and ubound[j] > 0:  # Positive range
                        trial[i, j] = 10 ** random.uniform(log10(lbound[j]), log10(ubound[j]))
                    else:
                        trial[i, j] = random.uniform(lbound[j], ubound[j])

            # --- Greedy Selection --- #
            if objective(trial[i]) < objective(pop[i]):
                pop[i, :-2] = trial[i, :]

            # --- Control parameters update --- #
            if random.rand() < 0.1:
                pop[i, dimension - 2] = 0.1 + random.rand() * 0.9
            if random.rand() < 0.1:
                pop[i, dimension - 1] = random.rand()

        # --- Calculates the objective for all individuals and selects the best one --- #
        for i in range(popsize):
            score[i] = objective(pop[i, :-2])
        best_index = np.argmin(score)
    return score[best_index], pop[best_index]

@jit(nopython=True, parallel=True)
def parallel(runs, popsize, gmax, lbound, ubound):
    score_list = np.zeros((runs, 1))
    solution_list = np.zeros((runs, len(lbound)))
    for i in prange(runs):
        seed = np.random.uniform(0,1e4)
        np.random.seed(round(seed))
        score, solution = differential_evolution(popsize, gmax, lbound, ubound)
        score_list[i] = score
        solution_list[i, :] = solution
    return score_list, solution_list

def load_raw_data(iv_folder, iv_curve, vmin, vmax, output_folder=None, write_to_file=False, output_filename="cleaned_iv_data.txt"):
    
    """Cleans a txt file with voltage and current data."""
    
    data = np.loadtxt(iv_folder + "/" + iv_curve, usecols=(0, 1))

    # Sort the data from reverse to forward bias (sort by voltage in ascending order)
    truncated_data = data[(data[:, 0] >= vmin) & (data[:, 0] <= vmax)]
    sorted_data_reverse_to_forward = truncated_data[truncated_data[:, 0].argsort()]
    
    # Separate the re-sorted data into voltage and current arrays
    voltage = sorted_data_reverse_to_forward[:, 0]
    current = sorted_data_reverse_to_forward[:, 1]
    
    if write_to_file and output_folder:
        # Ensure the output folder exists
        os.makedirs(output_folder, exist_ok=True)
        output_file_path = os.path.join(output_folder, output_filename)
        
        # Write the cleaned data to a text file
        np.savetxt(output_file_path, np.column_stack((voltage, current)), fmt='%e', header='Voltage Current')
        print(f"Data written to {output_file_path}")

    return voltage, current

# @jit(nopython=True)
# def objective(indv):
#     return np.power((indv[0]-2),2) + np.power((indv[1]-2),2)

voltage, current = load_raw_data("./", "test.txt", vmin=-2, vmax=2)

@jit(nopython=True)
def objective(indv):
    charge = 1.60e-19
    boltz = 1.38e-23
    vt = boltz * (25.0 + 273.15) / charge
    sim = indv[0] * (np.exp((voltage - current * indv[2]) / (indv[1] * vt)) - 1) + (voltage - current * indv[2]) / indv[3]
    normalized_error = ((current - sim) / (current)) ** 2
    return np.sqrt(np.sum(normalized_error) / len(voltage))

if __name__ == '__main__':

    lbound = np.array([1e-15, 1,  1e-6, 1e-1,0.1, 1e-3])
    ubound = np.array([1e-3,  10, 1e3,  1e9, 0.9, 1.0])

    score_list, solution_list = parallel(runs=2, popsize=100, gmax=1000, lbound=lbound, ubound=ubound)
    print(solution_list)