import numpy as np
def objective(indv):
    term1 = -20 * np.exp(-0.2 * np.sqrt(0.5 * (indv[0]**2 + indv[1]**2)))
    term2 = -np.exp(0.5 * (np.cos(2 * np.pi * indv[0]) + np.cos(2 * np.pi * indv[1])))
    value = term1 + term2 + np.e + 20
    return -value
indv = [-1.21160884e-09, 9.52166549e-01]
print(objective(indv))