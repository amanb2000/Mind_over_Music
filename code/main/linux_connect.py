import datetime
import threading
import time

import numpy as np

import museProcessing.dataProc.concentration as Concen
import museProcessing.dataProc.mlConcentration as mlConcen
import museProcessing.dataProc.ssvep as ssvep
from museProcessing.muse.muse2 import Muse
from museProcessing.settings import Settings

from live_process import LiveProcess
lp = LiveProcess()


callbackTime = time.time()
samplingFreq = 256  # Muse's sampling frequency
samplingTime = 10  # size of our FFT window
saveSamples = int(samplingFreq * (samplingTime * 1.5))
procSamples = int(samplingFreq * samplingTime)
xs = [0, 0, 0, 0]
cnt = [0]
ys1 = [0, 0, 0, 0]
ys2 = [0, 0, 0, 0]
ys3 = [0, 0, 0, 0]
ys4 = [0, 0, 0, 0]
ys5 = [0, 0, 0, 0]


def CurrentTime():
    return ('%s') % (datetime.datetime.now().strftime('%Y-%m-%d%H:%M:%S'))


def appendData(val, valType):
    with open(FILENAME, "a") as myfile:
        myfile.writelines(CurrentTime() + "," + str(val) + "," + str(valType) + "\n")


def processEEG(d1, d2, d3, d4, d5):
    global cnt, xs, ys1, ys2, ys3, ys4, ys5
    cnt[0] = cnt[0] + 1

    print
    # xs.append(len(xs))
    # ys1.append(d1)
    #ys2.append(d2)
    ys3.append(d3)
    # ys4.append(d4)
    ys5.append(d5)



    lp.addValue(d3) # TODO: See which one/how to incorporate other electrode potentials

    


def eeg(data, trash=True):
    # print(data)
    global callbackTime
    callbackTime = time.time()
    eeg1 = data[0]
    eeg2 = data[1]
    eeg3 = data[2]
    eeg4 = data[3]
    eeg5 = data[4]
    for i in range(12):
        processEEG(eeg1[i], eeg2[i], eeg3[i], eeg4[i], eeg5[i])

        

def runListener():
    try:

        print("Connecting to Muse ...")
        my_muse = Muse(callback=eeg, address=Settings.MUSE_ADDRESS)
        p1 = threading.Thread(target=my_muse.runListener).start()

        print("Muse connected and streaming")
        # Watchdog to monitor Muse connection and reconnect if necessary
        while True:
            time.sleep(1)

    except Exception as e:
        print("Killing program")
        print(e)

    finally:
        print("Muse disconnected")



if __name__ == "__main__":
    Concen.initConcentration()

    runListener()
