# Mind Over Music Audio Plugin - Linux Package
*VST Audio DSP Software Plugin Mind over Music project*

The goal for this project is to create a feedback loop where EEG signals influence a musical instrument that in turn influences a simulated [SWIM](http://wearcam.org/swim/) (SWIMulator). This feedback loop can be adjusted to optimize flow state, concentration, mindfulness, or any other psychological characteristic we can extract from the muse headset.

This Audio effect plugin included in this package is a software plugin which is designed to interface with a 
Digital Audio Workspace (DAW) to apply DSP algorithms to the audio recorded or produced by the DAW. 
This particular plugin is designed to use an Low Frequency Oscillator (LFO) to the amplify audio signals. The
frequency of the sinusoidal LFO is controlled by EEG band power written to a text file located at:
/Applications/MOM/eegData.txt

Setup instructions for using the plugin on a Linux computer:

* Ensure that Ubuntu 64 Bit is installed
* Download/Install Bitwig Studio DAW from https://www.bitwig.com/en/download.html (Select demo version)
* Ensure that Linux has ALSA Audio Driver fully setup by running:
     sudo apt-get install alsa-tools alsa-tools-gui alsamixergui patchage jackd2 \
     jackd2-firewire qjackctl a2jmidid gmidimonitor
* Copy eegData.txt from this directory (.../Amuse/Ableton_Integration/Releases/Linux) to /Applications/MOM/
* In Bitwig:
  Add Plug-in Location
  *Open File->Settings->Locations
  *Beside "Plug-In Locations", select "+ Add Location"
  *Add this directory (.../mind-over-music/Ableton_Integration/Releases/Linux)
  
  Import Plugin
  *In Settings window, open "Plug-Ins" tab
  *Select "By plug-in" and check the box to the left of "MIND OVER MUSIC (VST 3)"

  Import Audio Sample for processing
  *Return to the main DAW window of Bitwig
  *In "Browser" window on right, select the "Files" tab on the far right
  *Find this directory (.../Releases/Linux) under  "Computer"
  *Drag singingBowl.wav from that directory into the main DAW window (it should appear as an audio clip)

  Activate Plug-in
  *In the main DAW window, double click the name of the track where the new audio was added
  *Under the Browser ->"Devices" tab, navigate into Linux->eegVst
  *Drag "MIND OVER MUSIC (VST3)" to the "+"  symbol in the bottom section of the main window
  *VST Plugin is now active
