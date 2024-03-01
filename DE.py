#!/usr/bin/env python

# ------ import packages -----------------#
import numpy as np
from numba import jit, prange
from numpy import random
from math import log10
import os
from os import listdir
from os.path import isfile, join
from datetime import datetime
import sys

class DE():
       
    def load_raw_data(self,iv_folder, iv_curve, vmin, vmax, output_folder=None, write_to_file=False, output_filename="cleaned_iv_data.txt"):
        
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

    @jit(nopython=True)
    def objective(self, indv, vt, voltage, current, points):
        adjusted_voltage = voltage - indv[4]
        sim = indv[0] * (np.exp((adjusted_voltage - current * indv[2]) / (indv[1] * vt)) - 1) + (adjusted_voltage - current * indv[2]) / indv[3]
        epsilon = 1e-10
        normalized_error = ((current - sim) / (current + epsilon)) ** 2
        return np.sqrt(np.sum(normalized_error) / points)

    # --- Self-adaptive Differential Evolution ------ #
    @jit(nopython=True)
    def differential_evolution(self, popsize, gmax, vt, voltage, current, points):

        # ---  Define parameter bounds --- #
        lbound = np.array([1e-15, 1,  1e-6, 1e-1, -1,     0.1, 1e-3])
        ubound = np.array([1e-3,  10, 1e3,  1e9,   1,     0.9, 1.0])
        dimension = len(lbound)

        # ---  Initialize arrays --- #
        pop = np.zeros((popsize, dimension))
        for j in range(dimension):
            if lbound[j] < 0:
                pop[:, j] = random.uniform(lbound[j], ubound[j], popsize)
            else:
                pop[:, j] = 10 ** random.uniform(log10(lbound[j]), log10(ubound[j]), popsize)

        score = np.zeros((popsize, 1))
        donor = np.zeros((popsize, dimension))
        trial = np.zeros((popsize, dimension))

        # --- Initial best individual --- #
        for i in range(popsize):
            score[i] = self.objective(pop[i, :], vt, voltage, current, points)
        best_index = np.argmin(score)

        # --- Differential Evolution loop --- #
        for generation in range(gmax):
            for i in range(popsize):

                # --- Selection of random individuals, excluding current individual --- #
                candidates = np.arange(popsize)
                candidates = np.delete(candidates, i)
                random_index = random.choice(candidates, 4, replace=False)

                # --- Mutation --- #
                donor[i, :] = pop[i, :] + pop[i, dimension - 2] * (pop[best_index, :] - pop[i, :]) + pop[i, dimension - 2] * (pop[random_index[0], :] - pop[random_index[1], :])  # current-to-best/1
                #donor[i,:] = pop[i,:]+pop[i,4]*(pop[random_index[0],:]-pop[random_index[1],:])+pop[i,4]*(pop[random_index[2],:]-pop[random_index[3],:]) 

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
                    if trial[i, j] > ubound[j]:
                        trial[i, j] = 10 ** random.uniform(log10(lbound[j]), log10(ubound[j]))
                    if trial[i, j] < lbound[j]:
                        trial[i, j] = 10 ** random.uniform(log10(lbound[j]), log10(ubound[j]))

                # --- Greedy Selection --- #
                if self.objective(trial[i, :], vt, voltage, current, points) < self.objective(pop[i, :], vt, voltage, current, points):
                    pop[i, :] = trial[i, :]
                else:
                    pop[i, :] = pop[i, :]

                # --- Control parameters update --- #
                if random.rand() < 0.1:
                    pop[i, dimension - 2] = 0.1 + random.rand() * 0.9
                if random.rand() < 0.1:
                    pop[i, dimension - 1] = random.rand()

            # --- Calculates the objective for all individuals and selects the best one --- #
            for i in range(popsize):
                score[i] = self.objective(pop[i, :], vt, voltage, current, points)
            best_index = np.argmin(score)
        return score[best_index], pop[best_index]

    # --- Define parallel loop function --- #
    @jit(nopython=True, parallel=True)
    def parallel(self, runs, popsize, gmax, vt, voltage, current, points):
        score_list = np.zeros((runs, 1))
        solution_list = np.zeros((runs, 7))
        for i in prange(runs):
            seed = np.random.uniform(0,10000)
            np.random.seed(round(seed))
            score, solution = self.differential_evolution(popsize, gmax, vt, voltage, current, points)
            score_list[i] = score
            solution_list[i, :] = solution
        return score_list, solution_list

    # --- Main Loop ------ #
    def process_iv_curve(self, results_folder, iv_folder, iv_file, vmin, vmax, runs, popsize, gmax, temperature_celsius):

        # --- Initialize parallel function --- #
        charge = 1.60e-19
        boltz = 1.38e-23
        vt = boltz * (temperature_celsius + 273.15) / charge
        
        voltage, current = self.load_raw_data(iv_folder, iv_file, vmin, vmax, output_folder=None, write_to_file=False)
        
        points = np.size(voltage)
        score_list = np.zeros((runs, 1))
        solution_list = np.zeros((runs, 7))
        score_list, solution_list = self.parallel(runs, popsize, gmax, vt, voltage, current, points)

        with open(results_folder + "/" + "Results_" + iv_file, "w") as text_file:
            text_file.write("Run Objective I0 n Rs Rsh Offset\n" )
            for j in range(runs):
                text_file.write(f"{j:d} {score_list[j,0]:.3e} {solution_list[j,0]:.3e} {solution_list[j,1]:.3e} {solution_list[j,2]:.3e} {solution_list[j,3]:.3e} {solution_list[j,4]:.3e}\n")
        
    def main(self, iv_folder, results_folder, vmin, vmax, runs, popsize, gmax, temperature_celsius):
        os.makedirs(results_folder, exist_ok=True)
        iv_curves = [f for f in listdir(iv_folder) if isfile(join(iv_folder, f))]
        total_files = len(iv_curves)
        for i in range(total_files):
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Extracting parameters from curve {(i + 1)} of {total_files}", flush=True)
            self.process_iv_curve(results_folder, iv_folder, iv_curves[i], vmin, vmax, runs, popsize, gmax, temperature_celsius)
            sys.stdout.flush()