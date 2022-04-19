#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches

freq = 100

T = np.load("T_signal.npy")
T_fifo = np.load("T_signal_fifo.npy")

f, ax = plt.subplots(dpi=100)

ax.hist(T,      bins=100, color='b', zorder=1)
ax.hist(T_fifo, bins=100, color='r', zorder=2)
ax.vlines(1000/freq, ymin=0, ymax=ax.get_ylim()[-1], color='#707070', linestyles='dotted')
ax.vlines(T.max(), ymin=0, ymax=ax.get_ylim()[-1]/30, color='b')
ax.vlines(T_fifo.max(), ymin=0, ymax=ax.get_ylim()[-1]/30, color='r')

p = [patches.Patch(color='b'), patches.Patch(color='r')]
ax.legend(p, ["SCHED_OTHER", "SCHED_FIFO"])

ax.set_xlabel("Loop time (dt) [ms]")
ax.set_ylabel("Counts")
ax.set_title("Frequency = {} Hz".format(freq))

plt.show()