import sys
import os
import numpy as np
import pandas as pd
import serial
import struct
import time
import json

import statistics

last_time = 0
this_time = time.time()


f = open("fileout.txt","w+")

historical_data = [[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

def process_eeg(eeg_in): # Function for processing raw EEG in.
    json_in = json.loads(eeg_in)

    eeg_data = json_in["eeg"]
    count = eeg_data[0]
    interpolated = eeg_data[1]
    quality = eeg_data[2]
    eeg_data = eeg_data[3:17]


    global historical_data
    
    cnt = 0 # index 0

    stdevs = []
    
    for val in eeg_data:
        if True:
            try:
                stdevs.append(statistics.stdev(historical_data[0]))
            except:
                pass


        historical_data[cnt].append(val)
        while(len(historical_data[cnt]) > 255):
            historical_data[cnt].pop(0)

        cnt += 1
    try:
        # global f
        avg_stdev = (sum(stdevs) / len(stdevs))
        # f.write("{}\n".format(avg_stdev))

        print('\n\n\n\n\n\n\n\n{}\n\n\n\n\n\n\n'.format(avg_stdev))
    except:
        pass
 

    return


previous_average_power = []


def extract_band_power(eeg_in):
    """Takes in EEG power subscription string, processes it, and sends it to an arduino servo"""

    # Note to self: Ordering of bands is alpha, low beta, high beta, gamma, and theta (5) 

    global last_time
    global this_time
    
    this_time = time.time()

    power = json.loads(eeg_in)
    power = power['pow']
    # print(type(power))
    if this_time - last_time > 0.1:
        avg_value = 0       

        

        ind = 0 
        num_things = 0
        for i in power:
            if ind % 5 == 0 or True:
                avg_value += i
                num_things += 1
            ind+=1

        avg_value /= num_things
        
        if(avg_value < 3):
            # print(0)
            previous_average_power.append(0)
        else:
            previous_average_power.append(255)
            # print(1)

        while len(previous_average_power) > 10:
            previous_average_power.pop(0)

        # file1 = open("example.txt","a")
        # str1 = ''
        # str1 += '\n'
        # str1 += str(sum(previous_average_power)/len(previous_average_power))
        # file1.write(str1)
        # print('\n\n\n\n\n\n\n')
        # print(str1)
        # print('\n\n\n\n\n\n\n')
        # file1.close()
        
        try:
            file1 = open("example.txt","w")
            str1 = ''
            str1 += '\n'
            str1 += str(sum(previous_average_power)/len(previous_average_power))
            file1.write(str1)
            print('\n\n\n\n\n\n\n')
            print(str1)
            print('\n\n\n\n\n\n\n')
            file1.close()
        except:
            print('Try statement failed.')
            pass
        

