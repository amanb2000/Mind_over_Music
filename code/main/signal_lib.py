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

def eeg_to_file(eeg_in):
    """
    Function that takes the raw data from the Cortex API and parses out 
    the band powers. Those powers are saved to the a text file if a certain 
    threshold amount of time has elapsed since the last update.

    Note to self: Ordering of bands is alpha, low beta, high beta, gamma, and theta (5) 

    Parameters:
        eeg_in (string): Direct output from cortex.get_data() command.
    """

    ### Constants ###
    output_path = 'rawEEGData.txt'
    minimum_delay = 1 # number of seconds between each update to the output file.

    ### Main Code ###
    json_in = json.loads(eeg_in) # Converting input string to JSON

    power = json_in['pow']

    print("\n\n\n\n\nPower was: \n\n")
    print(power)
    print("\n\n\n")

    # Variables for tracking time between each file update.
    global last_time
    global this_time

    this_time = time.time()
    
    if this_time - last_time > 1:
        last_time = this_time

        # print(power) # Test statement for the headset

        # TODO: Take the average of each EEG band from the band power reported in each electrode.
        print("\n\n\nStarting to-file subroutine...\n\n\n\n\n\n")

        ### Writing to File ### 
        file1 = open(output_path, 'w')
        str_out = ''

        alpha = 0
        low_beta = 0
        high_beta = 0
        gamma = 0
        theta = 0

        cnt = 0
        for i in power:
            if cnt % 5 == 0:
                alpha += i
            elif cnt % 5 == 1:
                low_beta += i
            elif cnt % 5 == 2:
                high_beta += i
            elif cnt % 5 == 3:
                gamma += i
            else:
                theta += i
            cnt += 1

        str_out = "{} {} {} {} {}".format(alpha, low_beta, high_beta, gamma, theta)
        
        file1.write(str_out)
        print('String written to the output file at {}: \n'.format(output_path))

        print('{}\n'.format(str_out))

        file1.close()

    return


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


def jaw_clench(eeg_in):
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
        

