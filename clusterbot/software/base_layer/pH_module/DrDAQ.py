# ---------------------------------------------------------------- #
# ------ pH MEASUREMENT USING DR-DAQ ON RASPBERRY PI SERVER ------ #
# ---------------------------------------------------------------- #

# Abhishek Sharma
# Cronin Lab
# University of Glasgow
# abhishek.sharma@glasgow.ac.uk

"""
                  --- Description ---

     This file runs on RaspberryPi server to which DrDAQ is connected. The program runs 
     in background and waits for input from the client. Once contacted, it starts pH
     measurements and sends back average pH value. To start the program :

     python pH_DrDAQ_server.py &


     For some reasons, DrDAQ doesnot work on UBUNTU 16.04 LTS. So, I use Raspberry Pi 
     to get the pH values.
"""

import sys
import time
import ctypes
import socket
import numpy as np 

LIBNAME = '/opt/picoscope/lib/libusbdrdaq.so'

recording_block = ctypes.c_int16(200000)
no_of_samples = ctypes.c_int16(20000)
channel = ctypes.c_int16(5)
no_of_active_channels=ctypes.c_int16(1)
measurement_results = (ctypes.c_short * 20000)()

VERBOSE = 0

class drDAQ():

    def __init__(self):
        self.handle = None
        self.lib = ctypes.cdll.LoadLibrary(LIBNAME)
        self.handle = self.open_unit()
        self.set_DAQ_interval()
        self.enable_rgb()

    def open_unit(self):
        if VERBOSE:
            print ('Connecting to DrDAQ')

        try:
            self.handle = ctypes.c_int16()
            drDAQStatus = self.lib.UsbDrDaqOpenUnit(ctypes.byref(self.handle))

        except OSError:
            print ('No PICOSCOPE library found')

        if VERBOSE:
            print ('Pico_Status: '+ str(drDAQStatus))
            print ('Handle is '+str(self.handle.value))
        return self.handle

    def close_unit(self):
        if VERBOSE:
            print ('Closing connection to DrDAQ')
        try:
            res= self.lib.UsbDrDaqCloseUnit(self.handle)
            if VERBOSE:
                print ('Pico_Status: '+str(res))
    
        except OSError:
                print ('Closing failed')

    def set_DAQ_interval(self):
        if VERBOSE:
            print ('Setting Sampling Rate')
        res = self.lib.UsbDrDaqSetInterval(self.handle,ctypes.byref(recording_block),no_of_samples,ctypes.byref(channel),no_of_active_channels)
        if VERBOSE:
            print ('Status of interval setting' + str(res))

    def run_single_shot(self):
        res= self.lib.UsbDrDaqRun(self.handle,no_of_samples,ctypes.c_int16(1))
        if VERBOSE:
            print ('\nInitialising single shot measurement')
            print ('Status of single shot run: ' + str(res))

    def sampling_done(self):
        done = ctypes.c_bool(0)
        res = self.lib.UsbDrDaqReady(self.handle,ctypes.byref(done))
        if VERBOSE:
            print ('\nChecking if sampling is done')
            print ('Pico_Status: ' + str(res))
            print ('Sampling done is: ' + str(done))
        
    def stop_sampling(self):
        res= self.lib.UsbDrDaqStop(self.handle)
        if VERBOSE:
            print ('\nStopping Sampling') 
            print ('Pico_Status: ' + str(res)) 

    def get_sampled_values(self):
        noOfValues = no_of_samples
        Overflow = ctypes.c_int16(0)
        res = self.lib.UsbDrDaqGetValues(self.handle,ctypes.byref(measurement_results),ctypes.byref(noOfValues),ctypes.byref(Overflow),None)
        if VERBOSE:
            print ('\nPicoStatus sampling: ' + str(res))
            print ('Number of Samples measured: ' + str(noOfValues))
            print ('Channel with Overflow: ' + str(Overflow))
        if res == 0:
            samples = np.ctypeslib.as_array(measurement_results)
            print(str(samples))
            
            return samples

    def set_rgb(self, r, g, b):
        self.lib.UsbDrDaqSetRGBLED(self.handle, ctypes.c_ushort(r), ctypes.c_ushort(g), ctypes.c_ushort(b))

    def enable_rgb(self):
        self.lib.UsbDrDaqEnableRGBLED(self.handle, ctypes.c_short(1))
