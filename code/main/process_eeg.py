import sys
import os
import time
from reinforcement_agent import DQN_Agent

### Constants ###
IN_FILE_PATH = 'rawEEGData.txt'
# OUT_FILE_PATH = '../../../../../../Applications/MOM/audioModulationControl.txt' # For 4-param VST.
OUT_FILE_PATH = '../../../../../../Applications/MOM/eegData.txt'
SAVE_FILE_PATH = 'data/v2-trial-'+str(time.ctime(time.time()))+'.csv' # File for saving the trial's data.

SAVE_FILE_HEADER = 'time, reward, loss, alpha, low beta, high beta, gamma, theta, mod1, mod2, mod3, mod4, mod5\n'

READ_PERIOD = 1 # 1 second between each of the reads of the rawEEGData.txt file.

NUM_OUTPUTS = 1

# Variables for regulating the frequency of reading EEG data
this_time = time.time()
last_time = 0

# Variables for tracking the 
output_values = [300, 300, 800, 300]
output_values = [50, 50, 50, 50]

adjustment_rate = -1

# Reinforcement Learning Agent
dqn = DQN_Agent(NUM_OUTPUTS) # 4 outputs to actuate up or down.

def main():
    print('\nStarting process-eeg read/write loop...\n')

    global this_time
    global last_time

    try:
        in_file = open(IN_FILE_PATH, 'r').read()
    except:
        print('ERR: Could not open input file from path {}'.format(IN_FILE_PATH))
    finally:
        print('\nSuccessfully located and opened input file at {}\n'.format(IN_FILE_PATH))
    
    try:
        out_file = open(OUT_FILE_PATH, 'a')
    except:
        print('ERR: Could not open output file from path {}'.format(OUT_FILE_PATH))
    finally:
        print('\nSuccessfully located and opened output file at {}\n'.format(OUT_FILE_PATH))

    try:
        save_file = open(SAVE_FILE_PATH, 'w')
    except:
        print('ERR: Could not open save file path from path {}'.format(SAVE_FILE_PATH))
    finally:
        print('\nSuccessfully located and opened the save file at {}\n'.format(SAVE_FILE_PATH))
        save_file.write(SAVE_FILE_HEADER)


    print('Running loop...')

    while True:
        this_time = time.time()
        if this_time - last_time > READ_PERIOD:
            last_time = this_time

            try:
                in_file = open(IN_FILE_PATH, 'r').read()
            except:
                print('ERR: Could not open input file from path {}'.format(IN_FILE_PATH))
            
            list_in = in_file.split(' ')
            nums_list = []

            band_powers = ''

            for i in range(len(list_in)):
                if list_in[i].strip() != '':
                    nums_list += [float(list_in[i])]
                    band_powers += str(float(list_in[i])) + ', '

            out_list, reward, loss = process_eeg(nums_list) # Currently a placeholder function for any 
                                                            # method of converting EEG signals to VST 
                                                            # instructions.

            try:
                out_file = open(OUT_FILE_PATH, 'w')
            except:
                print('ERR: Could not open output file from path {}'.format(OUT_FILE_PATH))

            mod_vals = ''
            str_out = ''
            cnt = 0
            for i in out_list:
                cnt += 1
                str_out += str(i)
                mod_vals += str(i)
                str_out += ' '
                if(cnt != 5):
                    mod_vals += ', '

            mod_vals += '\n'

            save_val = str(this_time) + ', ' + str(reward) + ', ' + str(loss) + ', ' + band_powers + mod_vals # String to be saved for the meditation record.

            save_file.write(save_val) # Output from the DQN
            out_file.write(str_out) # Writing the output from the DQN to the save file.

            out_file.close()

def process_eeg(power_bands):
    """
    Function to house any processing that ought to be done at each read of the EEG data.
    This is where one would make calls to a reinforcement learning agent so that it can 
    return a command to be relayed to the VST.

    Parameters:
        power_bands: A list of floats that represents the band powers for the 5 major EEG bands.

    Output: A list of numbers or strings that represents the instructions to be given to the VST.
    """
    action, reward, loss = dqn.run_data(power_bands) #  self.action, reward, loss

    # for i in range(len(output_values)):
    #     output_values[i] += differential[i] * adjustment_rate

    param_num = int(action/2)
    inc_dec = ((action%2)*2)-1
    

    if NUM_OUTPUTS == 1:
        for i in range(len(output_values)):
            output_values[i] += inc_dec*adjustment_rate
            output_values[i] = max(0, output_values[i])
            output_values[i] = min(999, output_values[i])
    else:
        output_values[param_num] += inc_dec*adjustment_rate

    for i in range(len(output_values)):
        output_values[i] = max(0, output_values[i])
        output_values[i] = min(999, output_values[i])

    # print(output_values)

    return output_values, reward, loss

if __name__ == "__main__":
    main()

