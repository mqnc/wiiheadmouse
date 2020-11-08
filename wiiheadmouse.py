
# https://github.com/tswast/pywiiuse/blob/master/wiiuse/__init__.py
pywiiuseCode = """
'''Python interface to the wiiuse library for the wii remote

Just a simple wrapper, no attempt to make the api pythonic. I tried to hide ctypes where
necessary.

This software is free for any use. If you or your lawyer are stupid enough to believe I have any
liability for it, then don't use it; otherwise, be my guest.

Gary Bishop, January 2008
'''

import os
import sys
import ctypes
from ctypes import (c_char_p, c_int, c_int16, c_uint16, c_byte, c_uint, c_uint8, c_float,
    c_void_p, c_char, c_short, c_ushort)
from ctypes import CFUNCTYPE, Structure, POINTER, Union, byref

# duplicate the wiiuse data structures

class ang3s(Structure):
    _fields_ = [('roll', c_int16),
                ('pitch', c_int16),
                ('yaw', c_int16)
                ]

class ang3f(Structure):
    _fields_ = [('roll', c_float),
                ('pitch', c_float),
                ('yaw', c_float)
                ]

class vec2b(Structure):
    _fields_ = [('x', c_byte),
                ('y', c_byte),
                ]

class vec3b(Structure):
    _fields_ = [('x', c_byte),
                ('y', c_byte),
                ('z', c_byte),
                ]

class vec3f(Structure):
    _fields_ = [('x', c_float),
                ('y', c_float),
                ('z', c_float),
                ]

class orient(Structure):
    _fields_ = [('roll', c_float),
                ('pitch', c_float),
                ('yaw', c_float),
                ('a_roll', c_float),
                ('a_pitch', c_float),
                ]

class accel(Structure):
    _fields_ = [('cal_zero', vec3b),
                ('cal_g', vec3b),
                ('st_roll', c_float),
                ('st_pitch', c_float),
                ('st_alpha', c_float),
                ]

class ir_dot(Structure):
    _fields_ = [('visible', c_byte),
                ('x', c_uint),
                ('y', c_uint),
                ('rx', c_int16),
                ('ry', c_int16),
                ('order', c_byte),
                ('size', c_byte),
                ]

class ir(Structure):
    _fields_ = [('dot', ir_dot*4),
                ('num_dots', c_byte),
                ('aspect', c_int),
                ('pos', c_int),
                ('vres', c_uint*2),
                ('offset', c_int*2),
                ('state', c_int),
                ('ax', c_int),
                ('ay', c_int),
                ('x', c_int),
                ('y', c_int),
                ('distance', c_float),
                ('z', c_float),
                ]

class joystick(Structure):
    _fields_ = [('max', vec2b),
                ('min', vec2b),
                ('center', vec2b),
                ('ang', c_float),
                ('mag', c_float),
                ]

class nunchuk(Structure):
    _fields_ = [('accel_calib', accel),
                ('js', joystick),
                ('flags', POINTER(c_int)),
                ('btns', c_byte),
                ('btns_held', c_byte),
                ('btns_released', c_byte),
                ('orient_threshold', c_float),
                ('accel_threshold', c_int),
                ('accel', vec3b),
                ('orient', orient),
                ('gforce', vec3f),
                ]

class classic_ctrl(Structure):
    _fields_ = [('btns', c_int16),
                ('btns_held', c_int16),
                ('btns_released', c_int16),
                ('r_shoulder', c_float),
                ('l_shoulder', c_float),
                ('ljs', joystick),
                ('rjs', joystick),
                ]

class guitar_hero_3(Structure):
    _fields_ = [('btns', c_int16),
                ('btns_held', c_int16),
                ('btns_released', c_int16),
                ('whammy_bar', c_float),
                ('js', joystick),
                ]
class motion_plus(Structure):
    _fields_ = [('ext', c_byte),
                ('raw_gyro', ang3s),
                ('cal_gyro', ang3s),
                ('angle_rate_gyro', ang3f),
                ('orient', orient),
                ('acc_mode', c_byte),
                ('raw_gyro_threshold', c_int),
                ('nunchuk', POINTER(nunchuk)),
                ('classic_ctrl', POINTER(classic_ctrl))
                ]
class wii_board(Structure):
    _fields_ = [('tl', c_float),
                ('tr', c_float),
                ('bl', c_float),
                ('br', c_float),
                ('rtl', c_ushort),
                ('rtr', c_ushort),
                ('rbl', c_ushort),
                ('rbr', c_ushort),
                ('ctl', c_ushort*3),
                ('ctr', c_ushort*3),
                ('cbl', c_ushort*3),
                ('cbr', c_ushort*3),
                ('update_calib', c_uint8)
                ]
class expansion_union(Union):
    _fields_ = [('nunchuk', nunchuk),
                ('classic', classic_ctrl),
                ('gh3', guitar_hero_3),
                ('wb', wii_board),
                ]

class expansion(Structure):
    _fields_ = [('type', c_int),
                ('motion_plus', motion_plus),
                ('u', expansion_union),
                ]

class wiimote_state(Structure):
    _fields_ = [('exp_ljs_ang', c_float),
                ('exp_rjs_ang', c_float),
                ('exp_ljs_mag', c_float),
                ('exp_rjs_mag', c_float),
                ('exp_btns', c_uint16),
                ('exp_orient', orient),
                ('exp_accel', vec3b),
                ('exp_r_shoulder', c_float),
                ('exp_l_shoulder', c_float),
				('drx', c_short),
				('dry', c_short),
				('drz', c_short),
				('exp_wb_rtr', c_uint16),
				('exp_wb_rtl', c_uint16),
				('exp_wb_rbr', c_uint16),
				('exp_wb_rbl', c_uint16),
                ('ir_ax', c_int),
                ('ir_ay', c_int),
                ('ir_distance', c_float),
                ('orient', orient),
                ('btns', c_uint16),
                ('accel', vec3b),
                ]

if os.name == 'nt':
    JunkSkip = [('dev_handle', c_void_p),
                ('hid_overlap', c_void_p*5), # skipping over this data structure
                ('stack', c_int),
                ('timeout',c_int),#added
				('normal_timeout',c_byte),#added
				('exp_timeout',c_byte)#added
                ]
elif sys.platform == 'darwin':
    JunkSkip = [('objc_wm', c_void_p)]
else:
    JunkSkip = [('bdaddr', c_void_p),
                ('bdaddr_str', c_char*18),
                ('out_sock', c_int),
                ('in_sock', c_int),
                ]

class wiimote(Structure):
    _fields_ = [('unid', c_int),
                ] + JunkSkip + [
                ('state', c_int),
                ('leds', c_byte),
                ('battery_level', c_float),
                ('flags', c_int),
                ('handshake_state', c_byte),
                ('expansion_state', c_byte),
                ('data_req', c_void_p),
                ('read_req', c_void_p),
                ('accel_calib', accel),
                ('exp', expansion),
                ('accel', vec3b),
                ('orient', orient),
                ('gforce', vec3f),
                ('ir', ir),
                ('btns', c_ushort),
                ('btns_held', c_ushort),
                ('btns_released', c_ushort),
                ('orient_threshold', c_float),
                ('accel_threshold', c_int),
                ('lstate', wiimote_state),
                ('event', c_int),
                ('motion_plus_id', c_byte*6)
                ]

wiimote_p = POINTER(wiimote)
wiimote_pp = POINTER(wiimote_p)

event_cb_t = CFUNCTYPE(None, wiimote_p)
read_cb_t = CFUNCTYPE(None, wiimote_p, POINTER(c_byte), c_ushort)
ctrl_status_cb_t = CFUNCTYPE(None, wiimote_p, c_int, c_int, c_int, POINTER(c_int), c_float)
dis_cb_t = CFUNCTYPE(None, wiimote_p)

# clearly a few more to do but I haven't needed them yet
class api(Structure):
    _fields_ = [('version', c_char_p),
                ('api_version', c_int),
                ('init', CFUNCTYPE(wiimote_pp, c_int, POINTER(c_int), event_cb_t,
                                   ctrl_status_cb_t, dis_cb_t)),
                ('disconnected', c_void_p),
                ('rumble', CFUNCTYPE(None, wiimote_p, c_int)),
                ('toggle_rumble', CFUNCTYPE(None, wiimote_p)),
                ('set_leds', CFUNCTYPE(None, wiimote_p, c_int)),
                ('motion_sensing', CFUNCTYPE(None, wiimote_p, c_int)),
                ('read_data', c_void_p),
                ('write_data', c_void_p),
                ('status', CFUNCTYPE(None, wiimote_p)),
                ('get_by_id', c_void_p),
                ('set_flags', CFUNCTYPE(c_int, wiimote_p, c_int, c_int)),
                ('set_smooth_alpha', CFUNCTYPE(c_float, wiimote_p, c_float)),
                ('set_ir', CFUNCTYPE(None, wiimote_p, c_int)),
                ('set_ir_vres', CFUNCTYPE(None, wiimote_p, c_uint, c_uint)),
                ('set_ir_position', CFUNCTYPE(None, wiimote_p, c_int)),
                ('set_aspect_ratio', CFUNCTYPE(None, wiimote_p, c_int)),
                ('set_bluetooth_stack', c_void_p),
                ('set_orient_threshold', CFUNCTYPE(None, wiimote_p, c_float)),
                ('find', CFUNCTYPE(c_int, wiimote_pp, c_int, c_int)),
                ('connect', CFUNCTYPE(c_int, wiimote_pp, c_int)),
                ('disconnect', CFUNCTYPE(None, wiimote_p)),
                ('poll', CFUNCTYPE(None, wiimote_pp, c_int)),
                ]

def is_pressed(dev, button):
    return dev.btns & button

def is_held(dev, button):
    return dev.btns_held & button

def is_released(dev, button):
    return dev.btns_released & button

def is_just_pressed(dev, button):
    return is_pressed(dev, button) and not is_held(dev, button)

def using_acc(wm):
    return wm.state & 0x020

def using_exp(wm):
    return wm.state & 0x040

def using_ir(wm):
    return wm.state & 0x080

def using_speaker(wm):
    return wm.state & 0x100

LED_NONE = 0
LED_1 = 0x10
LED_2 = 0x20
LED_3 = 0x40
LED_4 = 0x80

LED = [LED_1, LED_2, LED_3, LED_4]

EXP_NONE = 0
EXP_NUNCHUK = 1
EXP_CLASSIC = 2

SMOOTHING = 0x01
CONTINUOUS = 0x02
ORIENT_THRESH = 0x04
INIT_FLAGS = SMOOTHING | ORIENT_THRESH

IR_ABOVE = 0
IR_BELOW = 1

ASPECT_4_3 = 0
ASPECT_16_9 = 1

button = { '2':0x0001,
           '1':0x0002,
           'B':0x0004,
           'A':0x0008,
           '-':0x0010,
           'Home':0x0080,
           'Left':0x0100,
           'Right':0x0200,
           'Down':0x0400,
           'Up':0x0800,
           '+':0x1000,
           }

nunchuk_button = { 'Z':0x01,
                   'C':0x02,
                   }

# functions from the wiiuse api
find = None
connect = None
set_leds = None
rumble = None
status = None
poll = None
disconnect = None
motion_sensing = None
set_ir = None
toggle_rumble = None
set_ir_vres = None
set_ir_position = None
set_aspect_ratio = None
set_orient_threshold = None
set_flags = None

# wrap the init function so the user doesn't have to fool with ctypes for the callbacks
def init(nwiimotes):
    '''Initialize the module'''
    # find the dll
    if os.name == 'nt':
        dll = ctypes.cdll.wiiuse
    elif sys.platform == 'darwin':
        dll = ctypes.cdll.LoadLibrary('libwiiuse.dylib')
    else:
        dll = ctypes.cdll.LoadLibrary('libwiiuse.so')

    # pointer to the api object he will return
    # wiiuse_api = POINTER(api)()
    # fill in the pointer
    # dll.wiiuse_main(byref(wiiuse_api))
    # get the object so we don't have to fool with the pointer
    # wapi = wiiuse_api[0]

    # initialize our other function pointers
    global find, connect, set_leds, rumble, status, poll, disconnect, motion_sensing
    global set_ir, toggle_rumble, set_ir_vres, set_ir_position, set_aspect_ratio
    global set_orient_threshold, set_flags
    find = dll.wiiuse_find
    connect = dll.wiiuse_connect
    set_leds = dll.wiiuse_set_leds
    rumble = dll.wiiuse_rumble
    status = dll.wiiuse_status
    poll = dll.wiiuse_poll
    disconnect = dll.wiiuse_disconnect
    motion_sensing = dll.wiiuse_motion_sensing
    set_ir = dll.wiiuse_set_ir
    toggle_rumble = dll.wiiuse_toggle_rumble
    set_ir_vres = dll.wiiuse_set_ir_vres
    set_ir_position = dll.wiiuse_set_ir_position
    set_aspect_ratio = dll.wiiuse_set_aspect_ratio
    set_orient_threshold = dll.wiiuse_set_orient_threshold
    set_flags = dll.wiiuse_set_flags

    # finally initialize wiiuse
    dll.wiiuse_init.restype = wiimote_pp
    wiimotes = dll.wiiuse_init(nwiimotes)

    return wiimotes
"""


import sys
import time
import os
import threading
import math

# import wiiuse from a string
from types import ModuleType
wiiuse = ModuleType('wiiuse')
sys.modules['wiiuse'] = wiiuse
exec(pywiiuseCode, wiiuse.__dict__)

try:
	from talon import ctrl, screen
	usingTalon = True
	moveMouse = ctrl.mouse_move
	W = screen.main_screen().rect.width
	H = screen.main_screen().rect.height
except:
	from pynput.mouse import Controller
	usingTalon = False
	mouse = Controller()
	def moveMouse(x, y):
		mouse.position = (x, y)
	moveMouse(30000, 30000)
	W, H = mouse.position

moveMouse(W/2, H/2)


def lerp(x0, x1, y0, y1, x):
	return (x-x0)/(x1-x0) * (y1-y0) + y0


def line(x0, y0, x1, y1):
	q = 0
	while q < 1:
		moveMouse((1-q)*x0 + q*x1, (1-q)*y0 + q*y1)
		q += 0.03
		time.sleep(0.02)

def wiggle(x, y):
	phi = 0
	while phi < 30:
		moveMouse(x + 30*math.cos(phi), y + 30*math.sin(phi))
		phi += 0.3
		time.sleep(0.02)



class WiiMouse:

	DISCONNECTED = 0
	INACTIVE = 1
	MOUSING = 2
	CALIBRATING = 3
	QUIT = 4

	def connect(self):
		while self.mode == self.DISCONNECTED:
			print('Attempting to connect to WiiMote...')
			if os.name != 'nt': print('Press (1) & (2)')

			found = wiiuse.find(self.wiimotes, 1, 5)
			if not found:
				print('no WiiMote found')
				continue

			connected = wiiuse.connect(self.wiimotes, 1)
			if connected:
				print('Connected to %i WiiMotes (of %i found).' % (connected, found))
			else:
				print('failed to connect to any WiiMote.')
				continue

			wiiuse.status(self.wiimotes[0])
			time.sleep(0.1)
			wiiuse.set_ir(self.wiimotes[0], 1)
			time.sleep(0.1)

			self.mode = self.MOUSING

	def disconnect(self):
		self.mode = self.DISCONNECTED
		wiiuse.disconnect(self.wiimotes[0])

	def quit(self):
		print("quitting...")
		self.disconnect()
		self.mode = self.QUIT

	def watchdog(self):
		try:
			while not self.mode == self.QUIT:
				time.sleep(0.1)
		finally:
			self.quit()

	def poller(self):
		while self.mode != self.QUIT:
			if self.mode == self.DISCONNECTED:
				time.sleep(0.01)
				continue

			r = wiiuse.poll(self.wiimotes, 1)
			if r != 0:
				wm = self.wiimotes[0][0]
				if self.mode == self.MOUSING or self.mode == self.CALIBRATING:
					x, y = 0, 0
					n = 0
					for i in range(4):
						if wm.ir.dot[i].visible:
							x += wm.ir.dot[i].x
							y += wm.ir.dot[i].y
							n += 1

					if n > 0:
						self.seeIR = True
						self.cursorMsr = (x/n, y/n)
					else:
						self.seeIR = False

	def smoothen(self):
		while not self.mode == self.QUIT:
			if self.mode == self.MOUSING:
				d = math.sqrt(
					(self.cursorMsr[0] - self.cursorSmooth[0])**2 +
					(self.cursorMsr[1] - self.cursorSmooth[1])**2
				)

				# or smoothing when the cursor doesn't move as much
				drag = 0.997 / ((d/80)**2 + 1)

				self.cursorSmooth = (
					drag*self.cursorSmooth[0] + (1-drag)*self.cursorMsr[0],
					drag*self.cursorSmooth[1] + (1-drag)*self.cursorMsr[1]
				)
				time.sleep(0.004)
			else:
				time.sleep(0.1)

	def controlMouse(self):
		while not self.mode == self.QUIT:
			if self.mode == self.MOUSING:
				moveMouse(
					lerp(
						self.caliPt1[0],
						self.caliPt2[0],
						50,
						W-50,
						self.cursorSmooth[0]
					) - self.offset[0],
					lerp(
						self.caliPt1[1],
						self.caliPt2[1],
						50,
						W-50,
						self.cursorSmooth[1]
					) - self.offset[1]
				)
				time.sleep(0.016)
			else:
				time.sleep(0.1)


	def calibrate(self):
		if self.mode != self.MOUSING:
			print("can only calibrate in mouse mode")
			return

		self.mode = self.CALIBRATING

		line(W/2, H/2, 50, 50)
		wiggle(50, 50)
		self.caliPt1 = self.cursorMsr
		line(50, 50, W-50, H-50)
		wiggle(W-50, H-50)
		self.caliPt2 = self.cursorMsr
		line(W-50, H-50, W/2, H/2)
		wiggle(W/2, H/2)
		x = lerp(self.caliPt1[0], self.caliPt2[0], 50, W-50, self.cursorMsr[0])
		y = lerp(self.caliPt1[1], self.caliPt2[1], 50, W-50, self.cursorMsr[1])
		self.offset = (x-W/2, y-H/2)

		self.mode = self.MOUSING

	def recenter():
		if self.mode != self.MOUSING:
			print("can only recenter in mouse mode")
			return

		self.mode = self.CALIBRATING

		wiggle(W/2, H/2)
		x = lerp(self.caliPt1[0], self.caliPt2[0], 50, W-50, self.cursorMsr[0])
		y = lerp(self.caliPt1[1], self.caliPt2[1], 50, W-50, self.cursorMsr[1])
		self.offset = (x-W/2, y-H/2)

		self.mode = self.MOUSING

	def __init__(self):
		self.mode = self.DISCONNECTED
		self.wiimotes = wiiuse.init(1)
		self.cursorMsr = (1024/2, 768/2)
		self.cursorSmooth = self.cursorMsr
		self.caliPt1 = (100, 100)
		self.caliPt2 = (1024-100, 768-100)
		self.offset = (0, 0)
		self.seeIR = False

		threading.Thread(target = self.watchdog, daemon = True).start()
		threading.Thread(target = self.poller, daemon = True).start()
		threading.Thread(target = self.smoothen, daemon = True).start()
		threading.Thread(target = self.controlMouse, daemon = True).start()

wm = WiiMouse()

if usingTalon:
	def initMouse():
		wm.connect()
		wm.calibrate()
	threading.Thread(target = initMouse, daemon = True).start()
else:
	wm.connect()
	wm.calibrate()
	while True:
		time.sleep(1)
