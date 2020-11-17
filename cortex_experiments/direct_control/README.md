# Immediate Implementations

These programs were made as a proof-of-concept for using the Emotiv Epoc+ to control a VST's 
LFO rate for a cutoff filter.

Future versions will have increased modulatarity and can be found in the super folder 
`Ableton Integration`.

### `connect.py`

Script to make connection and invoke function to write to Ableton script. This function will leverage the existing connection systems for creating a session with the Emotiv Epoc+ Cortex API. It will send all data packets to some arbitrary function in `signalLib.py` for further analysis and transfer.

### `signalLib.py`

Library of functions to analyze incoming data AND send them to the Ableton Live 10 VST's (currently that is via a text file). The following are signal processing functions that must be created:

* [DONE] Jaw clench classifier (faux regressor): 
	* Continuously calculate the standard deviation of the signal over the course of the `N` milliseconds.
	* If the STDEV goes above a threshold value `c`, return a `255`. Otherwise, return a `0`.
	* Extension: interpolate over `s` seconds to the final value of `255`.
* [IPR] Calmness regressor:
	* Research connection between `alpha`, `beta`, and `theta` bands and meditative state. 
	* Create an algorith that will process them into a `0-255` value. 
	* Extension: Add a machine learning aspect to the project.