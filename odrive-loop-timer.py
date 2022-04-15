#!/usr/bin/env python3

import odrive
import threading
import time
import os
from odrive.enums import *

control_freq = 100      # Hz
dt = 1.0/control_freq   # s

global odrv0

def loopFunction():
    global t0
    # Read odrive's encoder on axis0
    enc = odrv0.axis0.encoder.shadow_count
    # Dummy position command
    # odrv0.axis0.controller.input_pos = odrv0.axis0.controller.pos_setpoint
    t = time.time() - t0
    print("{:>.8f}".format(t))
        

def startTimer():
    t = threading.Timer(dt, startTimer)
    t.start()
    loopFunction()

if __name__ == '__main__':
    # Connect to Odrive
    odrv0 = odrive.find_any()
    print("// Connected to Odrive {} as odrv0".format(odrv0.serial_number))

    print("time")

    odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    
    # This requires sudo to run
    try:
        os.nice(-20)
    except PermissionError:
        pass

    t0 = time.time()
    startTimer()

