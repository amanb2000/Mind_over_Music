# Code: Mind over Music

The programs here work together to form the Mind over Music system.

## Folder Structure

* `audio_modulation`: Contains custom Audio Modulation programs. 

* `ESP32`: Bluetooth/UDP program that connects to the Muse 2 headset and relays the packet information to the UDP server in `main/udpserver.py`. This is a simple **Platform.io** project, so simply flash your ESP32 with the software and monitor it through the serial monitor to ensure it is connecting properly. Make sure you update the SSID, WiFi password, and UDP address. The UDP address should be 

* `main`: Python scripts to read EEG data, process via Deep Reinforcement Learning, and output results to the audio modulation system. See `main/README.md` for setup and use instructions.

-----------

## Implementation Notes

### VST File Location

For the current version of the Mind over Music VST, the path is hard coded as follows:

Windows OS: C:/ProgramData/MOM/eegData.txt

Unix: /Applications/MOM/eegData.txt

On a Unix system, that means that, when you his `pwd` in the given folder, it should actually
say the aforementioned path. It should not be relative to your root directory.
