#!/usr/bin/env python3
import signal, time, os

global t0 # Starting time
T = []    # List of time steps

freq = 100 # Hz
dt = 1.0/freq
tSleep = 0.005/freq

try:
    os.nice(-20)
except PermissionError:
    print(" \033[1;35m[WARNING]\033[0m Run this as sudo to set the niceness to -20 (PRI=0)")

# Ctrl-C handler
def intHandler(sig, f):
    global Running
    Running = False

# Handle SIGALRM signals: restart the timer and perform loop activities
def timeoutHandler(sig, f):
    global dt
    signal.setitimer(signal.ITIMER_REAL, dt)
    global t0
    T.append(time.time()-t0)

print(" [INFO]    Running at {} Hz. Stop with ^C".format(freq))

# Attach intHandler to SIGINT signal
signal.signal(signal.SIGINT, intHandler)
# Attach timeoutHandler to SIGALRM signal: loop function
signal.signal(signal.SIGALRM, timeoutHandler)
# Start the timer for the first time
signal.setitimer(signal.ITIMER_REAL, dt)

t0 = time.time()
Running = True
while Running:
    time.sleep(tSleep)

# Stopped: print average dt and freq
time.sleep(1)
import numpy as np
T = np.array(T)
T = np.diff(T)

ta = T.mean()
fa = 1/ta

print("\nAverage dt: {:.8f} | Average freq: {:4.6f}".format(ta, fa))
