#!/usr/bin/env python3

import threading
import time, os

control_freq = 100      # Hz
dt = 1.0/control_freq   # s

def loopFunction():
    global t0
    print(time.time() - t0)

def startTimer():
    t = threading.Timer(dt, startTimer)
    t.start()
    loopFunction()

if __name__ == '__main__':

    print("time") # for CSV header
    
    try:    
        os.nice(-20)
    except PermissionError:
        pass
    
    t0 = time.time()
    startTimer()

