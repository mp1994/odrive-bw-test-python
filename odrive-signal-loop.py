#!/usr/bin/env python3
import signal, time, os, sys
import odrive; from odrive.enums import *

global t0 # Starting time
T = []    # List of time steps
enc = []
torque = []

freq = int(sys.argv[1]) if len(sys.argv) == 2 else 500  # Hz
dt = 1.0/freq
tSleep = 0.25e-6
N = 60*freq

fifo = False
try:
    # Get highest priority value
    param = os.sched_param(os.sched_get_priority_max(os.SCHED_FIFO))    
    # Set SCHED_FIFO with highest priority
    os.sched_setscheduler(0, os.SCHED_FIFO, param)                      
    fifo = True
except PermissionError:
    print(" \033[1;35m[WARNING]\033[0m Run this as sudo to set SCHED_FIFO (PRI=rt)")

# Ctrl-C handler
def intHandler(sig, f):
    global Running
    Running = False

# Handle SIGALRM signals: restart the timer and perform loop activities
def timeoutHandler(sig, f):
    global dt
    signal.setitimer(signal.ITIMER_REAL, dt)
    global t0
    # Read odrv0 encoder
    global odrv0
    e = odrv0.axis0.encoder.pos_estimate
    enc.append(e)
    # t = odrv0.get_adc_voltage(3)
    # torque.append(t)
    T.append(time.perf_counter()-t0)
    global N
    if len(T) == N:
        global Running
        Running = False

print(" [INFO]    Running at {} Hz for {} s. Stop early with ^C".format(freq, N/freq))

odrv0 = odrive.find_any()
print("Connected to ODrive - {:.2f} V".format(odrv0.vbus_voltage))

# Attach intHandler to SIGINT signal
signal.signal(signal.SIGINT, intHandler)
# Attach timeoutHandler to SIGALRM signal: loop function
signal.signal(signal.SIGALRM, timeoutHandler)
# Start the timer for the first time
signal.setitimer(signal.ITIMER_REAL, dt)

Running = True
t0 = time.perf_counter()
while Running: 
    time.sleep(tSleep)

# Stopped: print average dt and freq
signal.setitimer(signal.ITIMER_REAL, 0)
time.sleep(1)

import numpy as np
import matplotlib.pyplot as plt

T = np.array(T)
T = np.diff(T)

enc = np.array(enc)

ta = T.mean()
fa = 1/ta
td = T.std()

print("\nAverage dt: {:.6f} ms +/- {:.4f} us | Average freq: {:4.4f} Hz".format(ta*1e3, td*1e6, fa))
print("Min: {:.6f} ms - Max: {:.6f} ms".format(min(T)*1000, max(T)*1000))

T = T * 1000
plt.hist(T, bins=250)
plt.xlabel("dt [ms]")
ax = plt.gca()
plt.text(0.5, 0.85, "Average frequency: {:4.4f} Hz".format(fa), fontsize=10, transform=ax.transAxes)
plt.vlines(1000/freq, 0, np.floor(ax.get_ylim()[-1]), colors='#808080', linestyles='dashed')
plt.show()

plt.plot(torque)
plt.plot(enc)
plt.show()

if fifo:
    np.save("T_signal_fifo", T)
else:
    np.save("T_signal", T)