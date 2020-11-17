import numpy as np
import bitstring
import time

"""
The pipeline takes in raw packets of data, storing, and returning the band powers. Heavily leveraging MannLab
`muse-processing` code.


"""
class LiveProcess:
    def __init__(self):
        self.samplingFreq = 256
        self.arrayLen = self.samplingFreq*5
        self.EEG = [0] # History of EEG value for an individual electrode.
        self.PSD = [0] # Power spectral densities, one per electrode.
        self.last_time = time.time()

    def addValue(self, value): # Function for the `linux_connect.py` script that already can process out values.
        self.EEG.append(value)
        # print(self.EEG)
        print(value)

        if len(self.EEG) > self.arrayLen:
            diff = len(self.EEG) - self.arrayLen
            self.EEG = self.EEG[diff:]

        if time.time() - self.last_time > 1:
            print('Present Band Powers')
            self.last_time = time.time()
            bands = self.getBands()

            str_out = ''

            for i in range(len(bands)):
                bands[i] /= 100000 
                str_out += str(bands[i]) + ' '


            print(str_out)

            save_file = open('rawEEGData.txt', 'w')
            save_file.write(str_out)
            save_file.close()

    def addPacket(self, packet):
        # print("DATA TYPE FOR PACKET: {}".format(type(packet)))

        packetIndex, data = self.unpackEEG(packet)
        self.EEG += data

        if len(self.EEG) > self.arrayLen:
            diff = len(self.EEG) - self.arrayLen
            self.EEG = self.EEG[diff:]

        if time.time() - self.last_time > 1:
            self.last_time = time.time()
            bands = self.getBands()

            str_out = ''

            for i in range(len(bands)):
                bands[i] /= 100000
                str_out += str(bands[i]) + ' '


            print(str_out)

            save_file = open('rawEEGData.txt', 'w')
            save_file.write(str_out)
            save_file.close()

    def getBands(self):
        freqs, ps = self.fftPSD(np.asarray(self.EEG), self.samplingFreq)

        mask = freqs > 0
    
        freqs = freqs[mask]
        ps = ps[mask]

        delta_mask = freqs < 4
        theta_mask = (4 < freqs) & (freqs < 7)
        alpha_mask = (8 < freqs) & (freqs < 15)
        beta_mask = (16 < freqs) & (freqs < 31)
        gamma_mask = freqs > 32


        delta = np.average(ps[delta_mask])
        theta = np.average(ps[theta_mask])
        alpha = np.average(ps[alpha_mask])
        beta = np.average(ps[beta_mask])
        gamma = np.average(ps[gamma_mask])

        return [alpha, beta, beta, gamma, theta] # Per Emotiv's standards

    def unpackEEG(self, packet):
        """Decode data packet of one eeg channel (from `delegate.py`)

        Each packet is encoded with a 16bit timestamp followed by 12 time samples with a 12 bit resolution.
        """

        # print("PACKET LOOKS LIKE: {}".format(packet))
        aa = bitstring.Bits(bytes=packet)
        pattern = "uint:16,uint:12,uint:12,uint:12,uint:12,uint:12,uint:12, \
        uint:12,uint:12,uint:12,uint:12,uint:12,uint:12"
        res = aa.unpack(pattern)
        packetIndex = res[0]
        data = res[2:]
        # data = res
        # 12 bits on a 2 mVpp range
        data = 0.48828125 * (np.array(data) - 2048)

        return packetIndex, list(data)


    # Calculate PSD using FFT
    def fftPSD(self, array, sample_f):
        ps = np.abs(np.fft.fft(array)) ** 2
        time_step = 1 / sample_f
        freqs = np.fft.fftfreq(array.size, time_step)
        idx = np.argsort(freqs)
        return freqs[idx], ps[idx]


