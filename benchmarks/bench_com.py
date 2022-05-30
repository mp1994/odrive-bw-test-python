#!/usr/bin/env python3

import time
import math
import odrive
import odrive.enums
import sys

ODRIVE0 = None
ODRIVE0_HULL_SENSOR_COUNTS_PER_POLE_PAIR = 6
ODRIVE0_MOTOR_LEFT_COUNTS_PER_REV = 2**14 # Read from config on odrive
ODRIVE0_MOTOR_RIGHT_COUNTS_PER_REV = 2**14 # Read from config on odrive
ODRIVE0_MOTOR_LEFT_KV = 330
ODRIVE0_MOTOR_RIGHT_KV = ODRIVE0_MOTOR_LEFT_KV

RADIANS_PER_REV = 2.0 * math.pi
# Source: https://en.wikipedia.org/wiki/Motor_constants#Motor_Torque_constant
AMPS_KV_NM_CONVERSION = (3.0/2.0) / (math.sqrt(3) * (1.0/60.0) * 2.0*math.pi)


#### ODrive functions ##########################################################


def init_odrive():
    print("[DEBUG] finding an odrive...", file=sys.stderr, flush=True)
    odrive0 = odrive.find_any()
    return odrive0

def set_odrive_vel(target_rads_per_sec_left, target_rads_per_sec_right):
    global ODRIVE0_MOTOR_LEFT_COUNTS_PER_REV
    global ODRIVE0_MOTOR_RIGHT_COUNTS_PER_REV
    if target_rads_per_sec_left is not None:
        target_revs_per_sec_left = target_rads_per_sec_left / RADIANS_PER_REV
        target_counts_per_sec_left = target_revs_per_sec_left * \
            ODRIVE0_MOTOR_LEFT_COUNTS_PER_REV
        ODRIVE0.axis0.controller.vel_setpoint = target_counts_per_sec_left
    if target_rads_per_sec_right is not None:
        target_revs_per_sec_right = target_rads_per_sec_right / RADIANS_PER_REV
        target_counts_per_sec_right = target_revs_per_sec_right * \
          ODRIVE0_MOTOR_RIGHT_COUNTS_PER_REV
        ODRIVE0.axis1.controller.vel_setpoint = target_counts_per_sec_right

def read_odrive_rads_per_sec():
    global ODRIVE0_MOTOR_LEFT_COUNTS_PER_REV
    global ODRIVE0_MOTOR_RIGHT_COUNTS_PER_REV
    counts_per_sec_left = ODRIVE0.axis0.encoder.vel_estimate
    counts_per_sec_right = ODRIVE0.axis1.encoder.vel_estimate
    rads_per_sec_left = 0
    if counts_per_sec_left != 0:
        revs_per_sec_left = counts_per_sec_left / ODRIVE0_MOTOR_LEFT_COUNTS_PER_REV
        rads_per_sec_left = RADIANS_PER_REV * revs_per_sec_left
    rads_per_sec_right = 0
    if counts_per_sec_right != 0:
      revs_per_sec_right = counts_per_sec_right / ODRIVE0_MOTOR_RIGHT_COUNTS_PER_REV
      rads_per_sec_right = RADIANS_PER_REV * revs_per_sec_right
    return {"lVelActual": rads_per_sec_left, "rVelActual": rads_per_sec_right}

def read_odrive_amps_and_Nm():
    global AMPS_KV_NM_CONVERSION
    global ODRIVE0_MOTOR_LEFT_KV
    global ODRIVE0_MOTOR_RIGHT_KV
    current_left = ODRIVE0.axis0.motor.current_control.Iq_setpoint
    current_right = ODRIVE0.axis1.motor.current_control.Iq_setpoint
    torque_left = AMPS_KV_NM_CONVERSION * current_left / ODRIVE0_MOTOR_LEFT_KV
    torque_right = AMPS_KV_NM_CONVERSION * current_right / ODRIVE0_MOTOR_RIGHT_KV
    return {
        "lCurrent": current_left,
        "rCurrent": current_right,
        "lTorque": torque_left,
        "rTorque": torque_right
    }

def read_odrive_pos():
    pos_left = ODRIVE0.axis0.encoder.pos_estimate * (RADIANS_PER_REV / ODRIVE0_MOTOR_LEFT_COUNTS_PER_REV)
    pos_right = ODRIVE0.axis1.encoder.pos_estimate * (RADIANS_PER_REV / ODRIVE0_MOTOR_RIGHT_COUNTS_PER_REV)
    return {
        "lPos": pos_left,
        "rPos": pos_right
    }


def idle_odrive():
    print("odrive to idle", file=sys.stderr, flush=True)
    ODRIVE0.axis0.requested_state = odrive.enums.AXIS_STATE_IDLE
    ODRIVE0.axis1.requested_state = odrive.enums.AXIS_STATE_IDLE

def activate_odrive():
    print("odrive to active", file=sys.stderr, flush=True)
    ODRIVE0.axis0.requested_state = odrive.enums.AXIS_STATE_CLOSED_LOOP_CONTROL
    ODRIVE0.axis1.requested_state = odrive.enums.AXIS_STATE_CLOSED_LOOP_CONTROL



#### Test ######################################################################

def odrive_speed_test():
    loop_iters = 1000
    t0 = time.time()
    for i in range(loop_iters):
        set_odrive_vel(0, 0)
    t1 = time.time()
    print(loop_iters*2, "writes of vel_setpoint", (t1-t0)/(loop_iters*2)*1000, "mS each", file=sys.stderr)
    for i in range(loop_iters):
        read_odrive_rads_per_sec()
        read_odrive_amps_and_Nm()
        read_odrive_pos()
    t2 = time.time()
    print(loop_iters*6, "reads of vel_estimate, pos_estimate, and Iq_setpoint", (t2-t1)/(loop_iters*6)*1000, "mS each", file=sys.stderr)
    print("Loop iteration time (2 writes, 6 reads): ",(t2-t1)/(loop_iters)*1000, "mS per loop", file=sys.stderr)
    print("Loop frequency: ",1000/(t2-t1), "Hz", file=sys.stderr)



#### Main ######################################################################


def main():
    global ODRIVE0
    init_t0 = time.time()
    ODRIVE0 = init_odrive()
    print("Initializing odrive", (time.time() - init_t0)*1000, "mS")
    # activate_odrive()
    odrive_speed_test()
    idle_odrive()
    time.sleep(1) # make sure command flushes over usb


if __name__ == '__main__':
    main()
