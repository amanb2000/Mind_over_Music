# eegMuse

## Prerequisites
### Hardware 
1. A Muse2 EEG headset
### Software
1. Anaconda  
[How to install Anaconda](https://linuxize.com/post/how-to-install-anaconda-on-ubuntu-18-04/)
2. Apt Install
```bash
$ sudo apt-get install libglib2.0-dev
```

## Setup
1. Go to the project root directory
2. Type the following commands to activate environment.
```bash
$ conda env create --prefix ./env --file environment.yml
```
3. Type the next commands.
```bash
$ conda activate path/to/conda/env
```
4. Change the Muse `MAC_Address` in the `./config.yml` to the MAC Address of your current Muse. Locate this address using your device's `Search Bluetooth Devices` function.


## Dev Notes
### Update Conda Environment
1. Check if library exists in Anaconda Cloud. Just Google Search `conda install [name/of/python/package]`
2. If present add the package name in `dependency` list of `environment.yml`. If not, add the package name in `pip` list of `environment.yml
3. Run the following command to update the environment. PS. You do not need to be outside the environment (`conda deactivate`) to update.
```bash
$ conda env update --prefix ./env --file environment.yml  --prune
```
