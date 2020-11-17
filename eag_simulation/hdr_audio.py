import math

import matplotlib.pyplot as plt
import numpy as np
import pyaudio
from matplotlib import animation

# constants
# Make sure CHUNK is divisible by wraps
CHUNK = 8000
WRAPS = 1
FORMAT = pyaudio.paInt16  # audio format (bytes per sample?)
CHANNELS = 1  # single channel for microphone
RATE = 44100  # samples per second
COLS = 1
ROWS = 1
CERT_COMPRESSION = 8
Y_LIM_SATURATION = 17
SATURATION_LVL = 12000  # digitally defined saturation level
width = int(SATURATION_LVL / 2)
HALF_SATURATION = SATURATION_LVL // 2  # might need a better name
GEOMETRIC = 8
GEOMETRIC2 = GEOMETRIC ** 2
EPSILON = 0.1
res_decrease_factor = GEOMETRIC ** 2
TITLE = ["LOW (1X)", "MED (2X)", "HGH (4X)", "HDR COMP"]
samp_rate = 44100
send_data = np.zeros(CHUNK)
soundSamplesRe = np.zeros(CHUNK)
soundSamplesReSend = np.zeros(CHUNK)
soundSamplesIm = np.zeros(CHUNK)
soundSamplesImSend = np.zeros(CHUNK)
prevInd = 0
currInd = CHUNK
hdrout = np.zeros(CHUNK)

# Set up the output audio
soundFreq = 1225
t = np.linspace(0, 40000 / soundFreq, 40000 * samp_rate // soundFreq)

soundArrRe = (2 ** 4) * (np.sin(2 * np.pi * soundFreq * t))
soundArrReSend = (2 ** 12) * (np.sin(2 * np.pi * soundFreq * t))
soundSize = len(soundArrRe)
soundArrIm = (2 ** 4) * (np.cos(2 * np.pi * soundFreq * t))
soundArrImSend = (2 ** 12) * (np.cos(2 * np.pi * soundFreq * t))


def callback(in_data, frame_count, time_info, status):
    # global prevInd
    # global currInd
    # global soundSize
    # global soundSamplesRe
    # global soundSamplesReSend
    # global soundArrReSend
    # global soundArrRe
    # global soundSamplesIm
    # global soundSamplesImSend
    # global soundArrImSend
    # global soundArrIm
    # indices = np.remainder(range(prevInd, currInd), soundSize)
    # soundSamplesReSend = np.take(soundArrReSend, indices, mode='wrap')
    # soundSamplesRe = np.take(soundArrRe, indices, mode='wrap')
    # soundSamplesImSend = np.take(soundArrImSend, indices, mode='wrap')
    # soundSamplesIm = np.take(soundArrIm, indices, mode='wrap')
    # prevInd = prevInd + CHUNK
    # currInd = currInd + CHUNK
    # if (prevInd >= soundSize):
    #    prevInd = prevInd % (soundSize)
    #    currInd = currInd % (soundSize)
    ##out = np.add(soundSamplesReSend, soundSamplesImSend)
    # out = soundSamplesReSend
    return hdrout.astype(np.int16).tostring(), pyaudio.paContinue


# Create matplotlib figure and axes.
plt.style.use('dark_background')
fig, axes = plt.subplots(ROWS, COLS, figsize=(15, 7), subplot_kw=dict(polar=True))
# pyaudio class instance
p = pyaudio.PyAudio()

# stream object to get data from microphone
stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    # input_device_index=0,  # 9 for Danson's Dell Dock
    rate=RATE,  # 48000 for Danson's Dell Dock
    input=True,
    output=True,
    frames_per_buffer=CHUNK
)

outstream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    # input_device_index=0,  # 9 for Danson's Dell Dock
    rate=RATE,  # 48000 for Danson's Dell Dock
    input=False,
    output=True,
    stream_callback=callback,
    frames_per_buffer=CHUNK
)

# Certainty functions
# Make it a trapizoid
# width = 40
offset = 0

trap_top_start = int((SATURATION_LVL / 2) + offset - (width / 2))
trap_top_end = int((SATURATION_LVL / 2) + offset + (width / 2))
certainty_list = [None] * SATURATION_LVL

for i in range(int(trap_top_start)):
    certainty_list[i] = i

for i in range(int(trap_top_end - trap_top_start)):
    certainty_list[i + trap_top_start] = trap_top_start
for i in range(int(SATURATION_LVL - trap_top_end)):
    certainty_list[i + trap_top_end] = SATURATION_LVL - trap_top_end - i
# certainty_list[0] = 0
certainty_list[len(certainty_list) - 1] = 0
print(certainty_list[len(certainty_list) - 1])

certainty = np.asarray(certainty_list)
certainty = np.divide(certainty, max(certainty_list) * CERT_COMPRESSION)


def set_fake_sat(data):
    masked_array = np.ma.masked_less(data, np.multiply(HALF_SATURATION, -1))
    data[masked_array.mask] = np.multiply(-1, HALF_SATURATION)
    masked_array = np.ma.masked_greater_equal(data, HALF_SATURATION)
    data[masked_array.mask] = HALF_SATURATION - 1
    return data


def compute_hdr(data):
    low = np.subtract(data[0], HALF_SATURATION)
    med = np.subtract(data[1], HALF_SATURATION)
    high = np.subtract(data[2], HALF_SATURATION)

    lowgain = np.multiply(low, GEOMETRIC2)
    medgain = np.multiply(med, GEOMETRIC)

    low = set_fake_sat(low)
    med = set_fake_sat(med)
    high = set_fake_sat(high)

    hdrin = np.zeros(CHUNK)
    for i in range(CHUNK):
        multlow = certainty[low[i] + HALF_SATURATION]
        multmed = certainty[med[i] + HALF_SATURATION]
        multhigh = certainty[high[i] + HALF_SATURATION]
        hdrin[i] = (lowgain[i] * multlow + medgain[i] * multmed + high[i] * multhigh)
        # print(multlow + multmed + multhigh)
        # hdrin[i] = (low[i] * multlow + med[i] * multmed + high[i] * multhigh) // (multlow + multmed + multhigh)
        # hdrin[i] = (low[i])

    # stream.write(hdrin.astype(np.int16).tostring())
    stream.write(hdrin.astype(np.int16).tostring())
    hdrin = np.add(hdrin, HALF_SATURATION)

    return hdrin


def decrease_resolution(sound):
    for i in range(len(sound)):
        sound[i] = int(sound[i] / res_decrease_factor)
        sound[i] = sound[i] * res_decrease_factor
    return sound


# variable for plotting
x = np.linspace(0, 2 * math.pi, int(CHUNK / WRAPS), dtype=float)
x_wrapper = np.linspace(0, 2 * math.pi, int(CHUNK / WRAPS), dtype=float)
for index in range(WRAPS - 1):
    x = np.append(x, x_wrapper)

lines = []
# Basic formatting for the axes
    #for row in range(ROWS):
row = 0
axes.set_xticks([])
axes.set_yticks([])
axes.set_facecolor('k')
if row == 0:
    axes.set_title(TITLE[3], color='white')
    axes.set_ylim(-1, SATURATION_LVL)
    temp = axes.plot(x, np.random.rand(CHUNK), '-',
                               lw=2, color='red', linewidth=0.5)[0]
    temp1 = axes.plot(x, np.random.rand(CHUNK), '-',
                               lw=2, color='green', linewidth=0.5)[0]
    temp2 = axes.plot(x, np.random.rand(CHUNK), '-',
                               lw=2, color='blue', linewidth=0.5)[0]
    #temp3 = axes.plot(x, np.random.rand(CHUNK), '-',
     #                          lw=2, color='white', linewidth=0.5)[0]
else:
    axes[row][col].set_title("Saturation", color='white')
    axes[row][col].set_ylim(-1, Y_LIM_SATURATION)
    temp = axes[row][col].plot(x, np.random.rand(CHUNK), '-',
                               lw=2, color='r', linewidth=0.5)[0]
lines.append(temp)
lines.append(temp1)
lines.append(temp2)
#lines.append(temp3)


def init():
    """
    Base frame for animation.FuncAnimation.

    Returns:
        list(np.array): Data to animate.
    """
    outstream.start_stream()
    for line in lines:
        line.set_ydata([])
    return lines


def animate(frame_num):
    """
    Main animation method for animation.FuncAnimation.

    Args:
        frame_num (int): Frame number as it is called in animation.FuncAnimation.

    Returns:
        list(np.array): Data to animate.
    """
    # binary data
    data_raw = stream.read(CHUNK, exception_on_overflow=False)
    # create np array and offset by 128
    data = np.frombuffer(data_raw, dtype=np.int16).astype(np.int16)
    # data_poor = decrease_resolution(data)
    data_processed = np.vstack(
        (data, np.multiply(data, GEOMETRIC), np.multiply(data, GEOMETRIC ** 2)))

    data_processed = np.add(data_processed, HALF_SATURATION)
    clip_data_processed = data_processed.copy()

    hdr = compute_hdr(data_processed)
    hdrout = data.copy()
    data_processed = np.vstack((data_processed, hdr))
    clip_data_processed = np.vstack((clip_data_processed, hdr))

    clip_data_processed = clip_data_processed - SATURATION_LVL + 1
    masked_array = np.ma.masked_less_equal(clip_data_processed, 0)
    clip_data_processed[masked_array.mask] = 1
    clip_data_processed = -np.log(clip_data_processed) / np.log(0.5)
    # masked_array = np.ma.masked_less(clip_data_processed, SATURATION_LVL)
    # clip_data_processed[masked_array.mask] = HALF_SATURATION
    # clip_data_processed[np.logical_not(masked_array.mask)] = SATURATION_LVL - 1

    for col_index in range(1):
        #lines[2 * col_index].set_ydata(data_processed[col_index])
        lines[(4*col_index)].set_ydata(data_processed[0])
        lines[(4*col_index)+1].set_ydata(data_processed[1])
        lines[(4*col_index)+2].set_ydata(data_processed[2])
        #lines[(4*col_index)+3].set_ydata(data_processed[3])
        #lines[2 * col_index + 1].set_ydata(clip_data_processed[col_index])

    return lines


anim = animation.FuncAnimation(fig, animate, init_func=init, frames=1000, interval=10, blit=True)
plt.show()

