# Timer-based Loop Function in Python

This repository contains several test scripts for loop functions:

 - `timer-loop.py` loops at a user-defined frequency (default: 100 Hz) using `threading.Timer()`
 - `signal-loop.py` loops at a user-defined frequency (default: 100 Hz) using `signal.setitimer()` and a `signal.SIGALRM` handler function

 The two methods are also tested to send control commands and read the position feedback with a brushless DC motor controller (i.e., the ODrive v3.6 by ODriveRobotics).

 ### Benchmark

 `threading.Timer()` was found to be less accurate (i.e., running at a lower frequency compared to what set by the user) w.r.t. `signal.setitimer()`, both on a general purpose Linux kernel and on a Preempt-patched Linux Kernel. In fact, the Preempt RT patch does not seem to make any difference, even when setting the NICE value of the process to -20 with `os.nice(-20)`.

 ##### `threading.Timer()` results
| **Target Frequency [Hz]** | **Delta Time [s]** | **Actual Frequency [Hz]** | **Error [%]** |
|---------------------------|:------------------:|:-------------------------:|:-------------:|
|             1             |      1.001179      |           0.9988          |      0.12     |
|             10            |      0.100716      |           9.9289          |      0.71     |
|            100            |      0.010226      |          97.7870          |      2.22     |
|            150            |       0007223      |          138.4480         |      7.67     |
 ##### `signal.setitimer()` results
| **Target Frequency [Hz]** | **Delta Time [s]** | **Actual Frequency [Hz]** | **Error [%]** |
|---------------------------|:------------------:|:-------------------------:|:-------------:|
|             1             |      1.000167      |           0.9998          |      0.02     |
|             10            |      0.100105      |           9.9895          |      0.10     |
|            100            |      0.010025      |          99.7482          |      0.25     |
|            150            |      0.006691      |          149.4595         |      0.36     |
|            1000           |      0.001004      |          996.1075         |      0.39     |
