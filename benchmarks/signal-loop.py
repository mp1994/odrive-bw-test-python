#!/usr/bin/env python3
import signal, time, os, sys

global t0 # Starting time
T = []    # List of time steps

freq = int(sys.argv[1])  # Hz
if freq is None:
    freq = 100 # Hz
dt = 1.0/freq
tSleep = 0.005/freq
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
    T.append(time.time()-t0)
    global N
    if len(T) == N:
        global Running
        Running = False

print(" [INFO]    Running at {} Hz for {} s. Stop early with ^C".format(freq, N/freq))

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
signal.setitimer(signal.ITIMER_REAL, 0)
time.sleep(1)

import numpy as np
import matplotlib.pyplot as plt

T = np.array(T)
T = np.diff(T)

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

if fifo:
    np.save("T_signal_fifo", T)
else:
    np.save("T_signal", T)