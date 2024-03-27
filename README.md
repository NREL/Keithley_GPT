# Keithley_GPT: An open-source library for Keithley 2400 Series SMUs Control and Analysis

Keithley_GPT is a comprehensive Python module accompanied by a user-friendly GUI, designed for the control of Keithley 2400 series Source Measure Units (SMUs). It includes a high-performance implementation compatible with Numba for the self-adaptive differential evolution algorithm, enhancing the analysis of IV (current-voltage) data. This tool is crafted to support researchers and engineers in electrical measurement and analysis tasks with ease and efficiency.

## Features

### DE (Differential Evolution)
- **Numba-Compatible Implementation**: Utilizes the self-adaptive differential evolution algorithm for optimization tasks. This implementation is based on the method introduced by Brest, Janez, et al., in their study "Self-adapting control parameters in differential evolution: A comparative study on numerical benchmark problems," published in IEEE Transactions on Evolutionary Computation, Vol. 10, No. 6, 2006, pp. 646-657.

### GUI (Graphical User Interface)
- **ChatGPT-Crafted**: Provides a straightforward and intuitive interface for interacting with Keithley 2400 series SMUs, making it accessible to users of all skill levels.

### Keithley2400GPT (Control Class)
- **ChatGPT-Crafted**: A dedicated control class for managing Keithley 2400 SMUs, designed to simplify the process of setting up and conducting measurements.

### IV_Characterization
- **Example Code**: Demonstrates how to acquire current-voltage data utilizing the Keithley2400GPT control class, serving as a practical guide for users.

### SDM_Extraction
- **Script**: Facilitates the extraction of single diode parameters from IV data, streamlining the analysis process.

### Fittings
- **Jupyter Notebook**: Employed for generating figures based on the data collected, aiding in the visualization and interpretation of results.

### LambertW Approximation
- **Method Evaluation**: Offers an evaluation of the main branch of the Lambert W function, approximated via the Newton-Raphson method. This evaluation is compared against results from the SciPy implementation, providing a reliability benchmark.
