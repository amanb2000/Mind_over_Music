# Mind over Music

*Authors: Aman Bhargava, Kyle O'Shaughnessy, Steve Mann*

[Click Here for IEEE Sensors 2020 Video Presentation](https://www.youtube.com/watch?v=PuzvJ03wy3A&feature=youtu.be&ab_channel=Aman%27sProjects)

Since the advent of EEG brain scanning technology, cognitive response modeling and brain state optimization has been a topic of great interest. 

Here, we propose a novel Humanistically Intelligent (HI) system where brain waves are interpreted by a real-time deep reinforcement learning agent that controls an audio modulation system in order for the user to achieve an arbitrary target brain state. 

In our tests comparing the proposed system to a conventional neurofeedback system, we found that the proposed system consistently led to a more meditative brain state with p = 0.06.

This work was presented at IEEE Sensors 2020 ([link](https://archive.org/details/pid-6601141)):

<a id="1">[1]</a> 
A. Bhargava, K. O'Shaughnessy, and S. Mann,  
"A Novel Approach to EEG Neurofeedback via Reinforcement Learning", 
*Proc. IEEE Sensors, 2020*.


**Note that certain key pieces of proprietary InteraXon code that enable one to directly connect to a Muse 2 headset via BLE have been removed due to non-disclosure agreement.*

## Requirements

### Software

* `python 3`
* `numpy`
* `pytorch`
* `matplotlib`
* `pandas`
* A `DAW` (digital audio workstation), see below.

### Hardware

* One of:
  * Muse 2 EEG Headset and ESP32 microprocessor.
  * Any Emotiv EEG Headset.
* Audio output system.
* A quiet space and 10 minutes of time to meditate.

## Goals

We aim to create a **modular** system that is able to (1) connect to any headset (Muse OR Emotiv, as OS-agnostically as possible) (2) Process the raw band powers via Deep Reinforcement Learning into a vector format and (3) communicate the processed signals to Kyle's audio modulation system.

## Instructions

1. Install and set up Audio Modulation programs. See `code/audio_modulation/Linux/README.md` for detailed installation and use instructions.

2. **If using Muse 2 headset**: Configure the ESP32 Platform.io project with the following information (file located in `/code/ESP32/src/main.cpp`):
    * Your WiFi SSID (Line 42).
    * Your WiFi password (Line 43).
    * Your UDP address (Line 45) -- the IP Address of the computer you are running the main system on.
    * **Once done**: Upload the code onto your ESP32 and monitor its connection progress via the Serial monitor in VSCode.

3. See `/code/main/README.md` for instructions on running the Deep Reinforcement Learning and coordination system.

4. Run `/eag-simulation/hdr_audio.py` for a high dynamic range RGB SWIMulator visualization of the audio. For best results, use a low-gain audio interface in a quiet room. 
