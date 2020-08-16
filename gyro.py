#!/usr/bin/python
import smbus
import math
import time
import curses

# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

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


address = 0x68
bus = smbus.SMBus(1) 
bus.write_byte_data(address, power_mgmt_1, 0)

def show_data(window):
    try:
        # set params
        w_scale = 131.0
        a_scale = 16384.0

        # initialize angle and angular velocities
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


        while True:

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

            # print results
            window.addstr("\n\tGyroscope\n")
            window.addstr("\t---------\n")
            window.addstr("\tw_x:  %5d\t scaled: %5f (deg/s)\n" % (w_x, w_x_scaled))
            window.addstr("\tw_y:  %5d\t scaled: %5f (deg/s)\n" % (w_y, w_y_scaled))
            window.addstr("\tw_z:  %5d\t scaled: %5f (deg/s)\n\n" % (w_z, w_z_scaled))
            window.addstr("\tO_x:  %5f (deg)\n" % O_x)
            window.addstr("\tO_y:  %5f (deg)\n" % O_y)
            window.addstr("\tO_z:  %5f (deg)\n" % O_z)
            window.addstr("\tO_dt: %5f\n" % O_dt)



            window.addstr("\n\n\tAcceleration\n")
            window.addstr("\t------------\n")

            a_x = read_word_2c(0x3b)
            a_y = read_word_2c(0x3d)
            a_z = read_word_2c(0x3f)

            a_x_scaled = a_x / a_scale
            a_y_scaled = a_y / a_scale
            a_z_scaled = a_z / a_scale

            window.addstr("\ta_x: %5d\t scaled: %5f (g)\n" % (a_x, a_x_scaled))
            window.addstr("\ta_y: %5d\t scaled: %5f (g)\n" % (a_y, a_y_scaled))
            window.addstr("\ta_z: %5d\t scaled: %5f (g)\n\n" % (a_z, a_z_scaled))


            window.refresh()
            window.clear()

    except KeyboardInterrupt:
        exit(0)

curses.wrapper(show_data)
