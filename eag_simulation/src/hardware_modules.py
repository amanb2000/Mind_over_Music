"""
These hardware modules simulates the behavior of the hardware modules.
"""
import numpy as np
import scipy.signal as signal

x = np.linspace(0, 7, )


class HardwareModules:
    def __init__(self):
        pass

    def analog_to_digital(self):
        pass

    def second_order_butter_low_pass(self, input_data, gain, frequency):
        sos = signal.butter(2, frequency, btype="lowpass", output='sos')
        filtered = signal.sosfilt(sos, input_data)
        amplified = filtered * gain
        return amplified

    def second_order_butter_high_pass(self, input_data, gain, frequency):
        sos = signal.butter(2, frequency, btype="highpass", output='sos')
        filtered = signal.sosfilt(sos, input_data)
        amplified = filtered * gain
        return amplified

    def notch_filter(self, input_data, frequency, quality_factor=30.0):
        signal.iirnotch(frequency, quality_factor)
