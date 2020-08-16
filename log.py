#!/usr/bin/python
import smbus
import math
import time
import os
import curses

# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
gyro_config = 0x1b
accel_config = 0x1c

def read_byte(reg):
	return bus.read_byte_data(address, reg)

def read_word(reg):
	h = bus.read_byte_data(address, reg)
	l = bus.read_byte_data(address, reg+1)
	value = (h << 8) + l
	return value

def read_word_2c(reg):
	val = read_word(reg)
	if (val >= 0x8000):
		return -((65535 - val) + 1)
	else:
		return val

w_scale = 16.38
a_scale = 2048

address = 0x68
bus = smbus.SMBus(1) 
bus.write_byte_data(address, power_mgmt_1, 0)
bus.write_byte_data(address, gyro_config, 24)
bus.write_byte_data(address, accel_config, 24)

# initialize angle and angular velocities
time.sleep(1) # wait so w initializes correctly
w_x0 = read_word_2c(0x43)
w_y0 = read_word_2c(0x45)
w_z0 = read_word_2c(0x47)
O_x = 0.0
O_y = 0.0
O_z = 0.0
O_t1 = time.time()

a_x0 = read_word_2c(0x3b)
a_y0 = read_word_2c(0x3d)
a_z0 = read_word_2c(0x3f)

start_time = time.time()

# get elapsed time
O_t2 = time.time()
O_dt = O_t2 - O_t1
O_t1 = O_t2

# get new angular velocities
w_x = read_word_2c(0x43)
w_y = read_word_2c(0x45)
w_z = read_word_2c(0x47)

# scale them
w_x_scaled = (w_x-w_x0) / w_scale
w_y_scaled = (w_y-w_y0) / w_scale
w_z_scaled = (w_z-w_z0) / w_scale

# update current angles
O_x += w_x_scaled * O_dt
O_y += w_y_scaled * O_dt
O_z += w_z_scaled * O_dt

a_x = read_word_2c(0x3b)
a_y = read_word_2c(0x3d)
a_z = read_word_2c(0x3f)

a_x_scaled = a_x / a_scale
a_y_scaled = a_y / a_scale
a_z_scaled = a_z / a_scale

logfile.write("%5d, %5d, %5d, %5d, %5d, %5d, %6f\n" % (w_x, w_y, w_z, a_x, a_y, a_z, O_dt))
logfile.flush()
os.fsync(logfile.fileno())
