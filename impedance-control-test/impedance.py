#!/usr/bin/python3
import odrive; from odrive.utils import dump_errors, start_liveplotter; from odrive.enums import *
from time import sleep; import signal

old_vel_value = 0
actual_pos = 0
actual_vel = 0
filtered_velocity = 0
current_measured = 0

def read_parameter():
    global actual_pos 
    global actual_vel
    global current_measured
    global filtered_velocity
    actual_pos = odrv0.axis0.encoder.pos_estimate 
    actual_vel = odrv0.axis0.encoder.vel_estimate
    current_measured = odrv0.axis0.motor.current_control.Iq_measured


def impedance(Kdgain, Kvgain, verbose=False):
    alfa = 0.005
    global old_vel_value
    global actual_pos
    global actual_vel
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
    odrv0.axis0.controller.input_torque = torque_command
def int_handler(sig, f):
    global Run; Run = False

def idle():
    odrv0.axis0.controller.input_torque = 0
    odrv0.axis0.requested_state = AXIS_STATE_IDLE


if __name__ == '__main__':

    odrv0 = odrive.find_any()
    print("Connected to ODrive")
    print("VBUS voltage = {:.2f} V".format(odrv0.vbus_voltage))

    signal.signal(signal.SIGINT, int_handler)

    # Set torque control
    odrv0.axis0.controller.config.control_mode = CONTROL_MODE_TORQUE_CONTROL
    # odrv0.axis0.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
    # odrv0.axis0.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL

    # Go to closed loop control
    odrv0.axis0.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
    # Set input mode: input:mode_pos_filtered no good for velocity e torque control
    odrv0.axis0.controller.config.input_mode = INPUT_MODE_PASSTHROUGH


    vel_limit = 15.0 # turn/s
    Kdgain = 3  # Nm/rad
    Kvgain = 0.06 # Nm/rad^2
    rate = 150  # Hz
    dt = 1.0/rate

    odrv0.axis0.controller.config.vel_limit = vel_limit
    canc_token = start_liveplotter(lambda:[actual_pos, filtered_velocity, current_measured])

    count = 0

    Run = True
    while Run:
        read_parameter()
        impedance(Kdgain,Kvgain, verbose=True)
        # odrv0.axis0.controller.input_vel = 0.02
        # odrv0.axis0.controller.input_pos= 0.0

        sleep(dt)
        count += 1
        # Stop after 30 sec
        if count == rate*60:
            idle()

    # Go to idle (if stopped by Ctrl-C)
    idle()



    

