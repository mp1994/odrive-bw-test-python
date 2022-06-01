#!/usr/bin/python3

import odrive; from odrive.enums import *; 
import time; import serial; import os; from struct import unpack
import numpy as np;  import matplotlib.pyplot as plt


class ODrive():
    # Constructore
    def __init__(self, serial_port='/dev/ttyACM0', timeout=0.0005, verbose=True, benchmark=True):
        # Timeout (default 0.5 ms) > limits the maximum loop frequency (i.e., serial reads cannot be faster than timeout)
        self.fd = serial.Serial(serial_port, timeout=timeout)
        if not self.fd.is_open:
            print("ERROR unable to open USB connection.")
            exit(1)
        self.verbose = verbose
        self.benchmark = benchmark
        self.fd.write_timeout = 0.25e-3
        self.count_timeouts = 0

    # Destructor: useful to flush and close the serial connection with ODrive
    def __del__(self):
        self.fd.flush()
        self.fd.close()

    # --- Some useful functions
    def connect_odrive(self, serial_port='/dev/ttyACM0', timeout=0.0005):
        if not self.fd.is_open:
            self.fd = serial.Serial(serial_port, timeout=timeout)
        self.fd.flush()
        return self.fd.is_open

    def request_data(self, msg):
        if self.benchmark:
            t = time.perf_counter()
        self.fd.write(msg)
        rx = self.fd.read(100)
        if self.benchmark:
            t = time.perf_counter() - t
        self.fd.flush()
        data = rx.decode()
        if self.verbose:
            print(data.strip(), end=' ---')
            if self.benchmark:
                print("Exec time: {:.4f} ms".format(t*1000))
            else:
                print()
            return data
        return rx

    def write(self, msg):
        if not type(msg) == bytes:
            msg = msg.encode()
        if msg[-1] != b'\r':
            msg = msg + b'\r'
        N = len(msg)
        try:
            count = self.fd.write(msg)
            assert(count == N)
            return count
        except serial.SerialTimeoutException:
            self.count_timeouts += 1
        self.fd.flush()

    def read(self, n=100):
        rx = self.fd.read(n)
        data = []
        if self.verbose:
            data = rx.decode().strip()
            print(data)
        return data if self.verbose else rx

# ----------------------------------    

if __name__ == '__main__':

    # -----------------------------------------
    num_loops = 0

    def standard_loop(odrv0, stat=True, plot=False):
        count = 0
        odrv0.benchmark = False # set to false for "external" benchmarking in the loop
        odrv0.verbose = False
        T = []
        while count < 10000:
            t = time.perf_counter()
            odrv0.write(b'c 0 0\r')
            odrv0.request_data(b'f 0\r')
            T.append(time.perf_counter()-t)
            count += 1
            time.sleep(max(1.0/500 - t, 0))
        # Stats and plot
        T = np.array(T)
        if stat:
            print("[STANDARD LOOP] ", end='')
            print("Min Avg Max - {:.4f} {:.4f} {:.4f} [ms] ".format(T.min()*1000, T.mean()*1000, T.max()*1000))
        if plot:
            f, ax = plt.subplots(2,1)
            ax[0].hist(T)
            ax[1].scatter(np.arange(len(T)), T)
            plt.show()

    def custom_loop(odrv0, stat=True, plot=True):
        count = 0
        odrv0.benchmark = False # set to false for "external" benchmarking in the loop
        odrv0.verbose = False
        T = []
        global num_loops; num_loops = 1000*60*5
        while count < num_loops:
            t = time.perf_counter()
            # Send torque_setpoint = 0 to axis0 and read feedback
            odrv0.write(b'a 0 0\r') 
            odrv0.read(100)
            T.append(time.perf_counter()-t)
            count += 1
            time.sleep(max(1.0/1000 - t, 0))
        # Stats and plot
        T = np.array(T)
        if stat:
            print("[CUSTOM LOOP]   ", end='')
            print("Min Avg Max - {:.4f} {:.4f} {:.4f} [ms] ".format(T.min()*1000, T.mean()*1000, T.max()*1000))
            count_less_than_1ms = len(np.where(T <= 1e-3)[0])
            print("Loop count <= 1ms = {} ({:.2f} %)".format(count_less_than_1ms, 100*count_less_than_1ms/num_loops))
        if plot:
            f, ax = plt.subplots(2,1)
            ax[0].hist(T)
            ax[1].scatter(np.arange(len(T)), T)
            plt.show()

    # -----------------------------------------

    try:
        # Get highest priority value
        param = os.sched_param(os.sched_get_priority_max(os.SCHED_FIFO))    
        # Set SCHED_FIFO with highest priority
        os.sched_setscheduler(0, os.SCHED_FIFO, param)                      
    except PermissionError:
        print(" \033[1;35m[WARNING]\033[0m Run this as sudo to set SCHED_FIFO (PRI=rt)")


    # Open serial connection to USB CDC endpoint (ASCII protocol)
    odrv0 = ODrive('/dev/ttyACM0')
    # Test: read vbus voltage with checksum
    odrv0.request_data(b"r vbus_voltage *93\r")
    # Test: request feedback from axis0
    odrv0.request_data(b'f 0\r')
    time.sleep(1)

    # Input mode passthrough
    odrv0.write(b"w axis0.controller.config.input_mode 1"); time.sleep(0.5)
    # Control mode torque control
    odrv0.write(b"w axis0.controller.config.control_mode 1"); time.sleep(0.5)
    # Closed loop control
    odrv0.write(b"w axis0.requested_state 8\r") # AXIS_STATE_CLOSED_LOOP_CONTROL = 8
    time.sleep(2)

    # Custom loop
    custom_loop(odrv0)
    print("Write timoeuts occurred: {} ({:.2f} %)".format(odrv0.count_timeouts, 100*odrv0.count_timeouts/num_loops))
    odrv0.count_timeouts = 0

    time.sleep(1)

    # Standard loop
    # standard_loop(odrv0)
    # print("Write timoeuts occurred: {}".format(odrv0.count_timeouts))


    odrv0.write(b"w axis0.requested_state 1\r") # AXIS_STATE_IDLE = 1
