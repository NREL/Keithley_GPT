import pyvisa

class Keithley2400Controller:
    def __init__(self, resource_name='ASRL5::INSTR', timeout=25000):
        self.resource_name = resource_name
        self.instrument = None
        self.timeout = timeout
        self.current_compliance = 0.01  # 10 mA default

    def connect(self):
        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(self.resource_name)
        self.instrument.timeout = self.timeout  # Set timeout
        self.instrument.write("*RST")  # Reset the instrument
        self.instrument.write("*CLS")  # Clear the status

    def identify(self):
        return self.instrument.query("*IDN?")

    def select_panel(self, panel='FRONT'):
        if panel.upper() == 'FRONT':
            self.instrument.write(":ROUT:TERM FRON")
        elif panel.upper() == 'REAR':
            self.instrument.write(":ROUT:TERM REAR")
        else:
            raise ValueError("Invalid panel option. Choose 'FRONT' or 'REAR'.")

    def set_measurement_mode(self, mode):
        if mode == 2:
            self.instrument.write(":SYST:RSEN OFF")  # 2-wire mode
        elif mode == 4:
            self.instrument.write(":SYST:RSEN ON")  # 4-wire mode
        else:
            raise ValueError("Invalid measurement mode. Choose 2 or 4.")

    def iv_sweep(self, source_type, measure_type, start_level, stop_level, step_level, 
                 measure_compliance, source_range=None, measure_range=None, nplc=1, 
                 source_delay=0.1, ovp=20):
        # Disable concurrent functions
        self.instrument.write(":SENS:FUNC:CONC OFF")

        # Calculate number of points for the sweep
        num_points = int(abs((stop_level - start_level)) / abs(step_level)) + 1

        # Set Over Voltage Protection (always present)
        self.instrument.write(f":SOUR:VOLT:PROT {ovp}")

        # Set source function and range
        self.instrument.write(f":SOUR:FUNC {source_type.upper()}")
        if source_type.upper() == 'CURR':
            if source_range is not None:
                self.set_source_current_range(source_range)
            else:
                self.instrument.write(":SOUR:CURR:RANG:AUTO ON")
        else:  # 'VOLT'
            if source_range is not None:
                self.set_source_voltage_range(source_range)
            else:
                self.instrument.write(":SOUR:VOLT:RANG:AUTO ON")

        # Set sense function and range
        self.instrument.write(f":SENS:FUNC '{measure_type.upper()}:DC'")
        if measure_type.upper() == 'CURR':
            self.instrument.write(f":SENS:CURR:PROT {measure_compliance}")
            if measure_range is not None:
                self.set_measure_current_range(measure_range)
            else:
                self.instrument.write(":SENS:CURR:RANG:AUTO ON")
        else:  # 'VOLT'
            self.instrument.write(f":SENS:VOLT:PROT {measure_compliance}")
            if measure_range is not None:
                self.set_measure_voltage_range(measure_range)
            else:
                self.instrument.write(":SENS:VOLT:RANG:AUTO ON")

        # Configure source for sweep
        self.instrument.write(f":SOUR:{source_type.upper()}:START {start_level}")
        self.instrument.write(f":SOUR:{source_type.upper()}:STOP {stop_level}")
        self.instrument.write(f":SOUR:{source_type.upper()}:STEP {step_level}")
        self.instrument.write(f":SOUR:{source_type.upper()}:MODE SWE")

        # Small correction for auto-range (human-added)
        if measure_range is not None:
            self.instrument.write(":SOUR:SWE:RANG FIX")
        else:
            self.instrument.write(":SOUR:SWE:RANG AUTO")
        self.instrument.write(":SOUR:SWE:SPAC LIN")

        # Set NPLC, trigger count and source delay
        self.set_nplc(nplc, measure_type)
        self.instrument.write(f":TRIG:COUN {num_points}")
        self.instrument.write(f":SOUR:DEL {source_delay}")

        # Enable output and initiate measurement
        self.instrument.write(":OUTP ON")
        raw_data = self.instrument.query_ascii_values(":READ?")

        # Disable output after measurement
        self.instrument.write(":OUTP OFF")

        voltage = [raw_data[i] for i in range(0, len(raw_data), 5)] # Manual correction: voltage instead of sourced values
        current = [raw_data[i + 1] for i in range(0, len(raw_data), 5)] # Manual correction: current instead of measured values

        return voltage, current

    def set_source_current_range(self, range_value):
        self.instrument.write(f":SOUR:CURR:RANG {range_value}")

    def set_source_voltage_range(self, range_value):
        self.instrument.write(f":SOUR:VOLT:RANG {range_value}")

    def set_measure_current_range(self, range_value):
        self.instrument.write(f":SENS:CURR:RANG {range_value}")

    def set_measure_voltage_range(self, range_value):
        self.instrument.write(f":SENS:VOLT:RANG {range_value}")

    def set_current_compliance(self, compliance):
        self.current_compliance = compliance
        self.instrument.write(f":SENS:CURR:PROT {compliance}")

    def set_nplc(self, nplc, measurement_type='CURR'):
            if measurement_type.upper() == 'CURR':
                self.instrument.write(f":SENS:CURR:NPLC {nplc}")
            elif measurement_type.upper() == 'VOLT':
                self.instrument.write(f":SENS:VOLT:NPLC {nplc}")
            else:
                raise ValueError("Invalid measurement type. Choose 'CURR' or 'VOLT'.")