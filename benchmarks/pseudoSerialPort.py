#!/usr/bin/env python3

import os, pty, serial
import time, sys

if __name__=='__main__':

    master,slave = pty.openpty()  # open the pseudoterminal
    s_name = os.ttyname(slave)    # translate the slave fd to a filename
    print("Connect to: \033[1;33m{}\033[0m".format(s_name))

    s = input("Press any key to start...")
    print("\033[1;32m [INFO]\033[0m Simulating the serial port...")

    counter = 0
    TxBuffer = bytearray(50)
    RxBuffer = bytearray(50)
    TxBuffer[0]  = 0xA0
    TxBuffer[-1] = 0xC0


    
    while 1:
        os.read(master, RxBuffer)        
        counter = counter+1
        TxBuffer[1:5] = counter.to_bytes(4, sys.byteorder)
        os.write(master, TxBuffer)
        time.sleep(0.02) # approx 50 Hz
