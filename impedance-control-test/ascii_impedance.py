#!/usr/bin/env python3

import struct
from asciiodrive import *
import os, signal

odrv0 = []
old_vel_value = 0
filtered_velocity = 0

if __name__ == '__main__':

    def int_handler(sig, f):
        global Run; Run = False
        global odrv0
        odrv0.write(b"w axis0.requested_state 1\r") # AXIS_STATE_IDLE = 1

    signal.signal(signal.SIGINT, int_handler)

    def impedance(actual_pos, actual_vel, Kdgain=1.0, Kvgain=0.02, verbose=False):
        alfa = 0.005
        global old_vel_value
        global filtered_velocity
        filtered_velocity = (1-alfa)*old_vel_value + alfa*actual_vel
        # print("filtered_velocity {} rad/s".format(filtered_velocity))
        old_vel_value = actual_vel
        #impedance target
        torque_command = Kdgain * (0 - actual_pos/20) - Kvgain*filtered_velocity/6.28
        if torque_command > 10:
            torque_command = 10
        elif torque_command < -10:
            torque_command = -10
        if verbose:
            print("torque {} Nm".format(torque_command*20))
        return torque_command

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

    odrv0.benchmark = False # set to false for "external" benchmarking in the loop
    odrv0.verbose = False
    T = []
    Run = True
    actual_pos, actual_vel = 0, 0
    freq = 1000
    while Run:
        t = time.perf_counter()
        # Send torque_setpoint = 0 to axis0 and read feedback
        torque_command = impedance(actual_pos, actual_vel)
        odrv0.write("a 0 {}".format(torque_command)) 
        rx = odrv0.read(100)
        try:
            rx = unpack('fff', rx)
            actual_pos, actual_vel = rx[0], rx[1]
        except struct.error:
            pass
        # print(actual_pos)
        T.append(time.perf_counter()-t)
        time.sleep(max(1.0/freq - t, 0))
    # Stats and plot
    T = np.array(T)
    print("[CUSTOM LOOP]   ", end='')
    print("Min Avg Max - {:.4f} {:.4f} {:.4f} [ms] ".format(T.min()*1000, T.mean()*1000, T.max()*1000))
    count_less_than_dt = len(np.where(T <= 1.0/freq)[0])
    print("Loop count <= 1ms = {} ({:.2f} %)".format(count_less_than_dt, 100*count_less_than_dt/len(T)))

