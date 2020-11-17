# Main: Mind over Music

Run the programs in this folder to connect to the EEG headset, process the data, and send it to the modulation system. 

## Instructions (Muse Connection)

*Ensure that you have followed the root-directory `README.md` instructions beforehand...*

1. Run `udpserver.py`. This will receive Bluetooth packets from the ESP32 and process them, outputting them to a text file called `rawEEGData.txt`. You can also monitor `rawEEGData.txt` in a text editor like VSCode that tracks changes to files in real-time.

2. Open a new terminal tab/window and run `process-eeg.py` concurrently. This will receive the processed EEG data from the UDP server and will use Deep Reinforcement Learning to further process the data.

3. The system is now outputting data to the audio modulation system. Open your Digital Audio Workstation and follow the instructions in `/code/audio_modulation/Linux/README.md` to use the audio modulation tools.

The feedback system should now be in full swing, with the data outputting to `/code/main/data/v2-trial-epocnumber.csv`.

## Instructions (Emotiv Connection)

*Ensure that you have followed the root-directory `README.md` instructions beforehand...*

1. After hydrating and connecting your EMOTIV headset, run `emotiv-connect.py`. It will connect to the headset and output the band powers to the file `rawEEGData.txt`. You can also monitor `rawEEGData.txt` in a text editor like VSCode that tracks changes to files in real-time.

2. Open a new terminal tab/window and run `process-eeg.py` concurrently. This will receive the processed EEG data from the UDP server and will use Deep Reinforcement Learning to further process the data.

3. The system is now outputting data to the audio modulation system. Open your Digital Audio Workstation and follow the instructions in `/code/audio_modulation/Linux/README.md` to use the audio modulation tools.

The feedback system should now be in full swing, with the data outputting to `/code/main/data/v2-trial-Day Month Day Time Year.csv` (e.g. `v2-trial-Thu May 21 22:38:15 2020.csv`).
