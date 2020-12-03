
"""
Notebook for streaming data from a microphone in realtime

audio is captured using pyaudio
then converted from binary data to ints using struct
then displayed using matplotlib

if you don't have pyaudio, then run

>>> pip install pyaudio

note: with 2048 samples per chunk, I'm getting 20FPS
"""

import pyaudio
import os
import struct
import numpy as np
import matplotlib.pyplot as plt
import time
from tkinter import TclError
import math

class SWIMulator:

    """ 
    Class to vizualize signal input data in a SWIM style in Python

    dataStream: an audio stream (using pyaudio) from which the vizualisation feeds
    buffSize: The buffer size

    """
    FORMAT = pyaudio.paInt16

    def __init__(self, buffSize=802, channelCount=1, rate=44100, axes=False):
        self.chunk = buffSize * 2
        self.channels = channelCount
        self.rate = rate
        self.crosshair = False

        self.init_plot()

        if axes:
            self.toggle_axes()

    def open_stream(self):
        # pyaudio class instance
        p = pyaudio.PyAudio()

        # stream object to get data from microphone
        self.stream = p.open(
            format=SWIMulator.FORMAT,
            channels=self.channels,
            rate=self.rate,
            input=True,
            output=True,
            frames_per_buffer=self.chunk
        )

        return

    def init_plot(self):
        self.plot, self.axes = plt.subplots(1, figsize=(15, 7), subplot_kw=dict(polar=True))

        # Dummy line info
        xp = np.arange(0, 2*math.pi, 8*math.pi/(self.chunk), dtype=float)
        x = np.append(xp, xp)
        x = np.append(x, x)

        # Arrange line
        self.line, = self.axes.plot(x, np.random.rand(self.chunk), '-', lw=2, color='#330033')

        # Build axes
        self.axes.set_title('')
        self.axes.set_ylim(-1, 259)
        self.axes.set_xticks([]) 
        self.axes.set_yticks([])
        self.axes.set_rticks([])

        # Stylaize
        self.axes.set_facecolor((1,1,1))
        # self.axes.set_axis_bgcolor((0,0,0))
        # self.axes.set_xlim(0, 360)
        # self.plot.setp(ax, xticks=[0, CHUNK, 2 * CHUNK], yticks=[0, 128, 255])

        return

    def toggle_axes(self):
        self.crosshair = not self.crosshair
        if self.crosshair:
            self.axes.grid(True, color='#000000', linestyle='-', linewidth=1)
            self.axes.set_xticks(np.arange(0,2.0*np.pi, np.pi/2.0))
        else:
            self.axes.grid(False)
            self.axes.set_xticks([])

        # ax.set_title('')
        # ax.set_xlabel('samples')
        # ax.set_ylabel('volume')
        # ax.set_ylim(-1, 259)
        
        # ax.set_yticks([])
        
        return

    def start(self):
        # Begin
        plt.show(block=False)

        # Count frames
        frame_count = 0
        start_time = time.time()

        # Loop
        while True: # End this with ctrl+C
            # Begin reading the data
            data = self.stream.read(self.chunk, exception_on_overflow=False)  
            
            # Convert data to integers packed as numpy array, then offset it by 127
            data_int = struct.unpack(str(2 * self.chunk) + 'B', data)
            
            # Create numpy array and offset by 128
            data_np = np.array(data_int, dtype='b')[::2] + 129

            self.line.set_ydata(data_np)
            
            # update figure canvas
            try:
                self.plot.canvas.draw()
                self.plot.canvas.flush_events()
                frame_count += 1
                
            except TclError:
                
                # calculate average frame rate
                frame_rate = frame_count / (time.time() - start_time)
                
                print('Stream stopped')
                print('Average frame rate = {:.0f} FPS'.format(frame_rate))
                break
