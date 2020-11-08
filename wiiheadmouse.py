
SCROLL_MULTIPLIER = 1

import sys
import time
import os
import threading
import math

# import wiiuse from a file
path = os.path.join(
	os.path.dirname(os.path.abspath(__file__)),
	'pywiiuse.py_'
)
with open(path) as file:
	code = file.read()
from types import ModuleType
wiiuse = ModuleType('wiiuse')
sys.modules['wiiuse'] = wiiuse
exec(code, wiiuse.__dict__)

try:
	from talon import Module, ctrl, screen
	usingTalon = True
	moveMouse = ctrl.mouse_move
	def scrollMouse(y):
		ctrl.mouse_scroll(y, 0)
	W = screen.main_screen().rect.width
	H = screen.main_screen().rect.height
except:
	from pynput.mouse import Controller
	usingTalon = False
	mouse = Controller()
	def moveMouse(x, y):
		mouse.position = (x, y)
	def scrollMouse(y):
		mouse.scroll(0, y)
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
	SCROLLING = 3
	CALIBRATING = 4
	QUIT = 5

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
			if self.mode == self.DISCONNECTED:
				time.sleep(0.1)
				continue

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

	def controlMouse(self):
		while not self.mode == self.QUIT:
			if self.mode == self.MOUSING:
				moveMouse(
					lerp(
						self.caliPt1[0], self.caliPt2[0],
						50, W-50,
						self.cursorSmooth[0]
					) - self.offset[0],
					lerp(
						self.caliPt1[1], self.caliPt2[1],
						50, W-50,
						self.cursorSmooth[1]
					) - self.offset[1]
				)
				time.sleep(0.016)
			elif self.mode == self.SCROLLING:
				d = self.cursorSmooth[1] - self.scrollStart[1]
				dir = 1 if d >= 0 else -1
				if abs(d) > 50:
					speed = ((abs(d) - 50)/20)**1.7 * SCROLL_MULTIPLIER
					interval = 1/speed
					step = 1
					while interval < 0.1:
						step += 1
						interval = step/speed
					if interval > 0.5:
						interval = 0.5
					scrollMouse(dir * step)
					time.sleep(interval)
				else:
					time.sleep(0.1)
			else:
				time.sleep(0.1)

	def startScrolling(self):
		if self.mode == self.MOUSING:
			self.mode = self.SCROLLING
			self.scrollStart = self.cursorSmooth
		else:
			print("can only scroll in mouse mode")

	def stopScrolling(self):
		if self.mode == self.SCROLLING:
			self.mode = self.MOUSING
		else:
			print("wasn't scrolling")

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

	def recenter(self):
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
		self.scrollStart = self.cursorMsr
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
	mod = Module()

	@mod.action_class
	class Actions:

		def wii_connect():
			"""connect to the WiiHeadMouse"""
			threading.Thread(target = wm.connect, daemon = True).start()

		def wii_disconnect():
			"""disconnect from the WiiHeadMouse"""
			wm.disconnect()

		def wii_calibrate():
			"""calibrate the WiiHeadMouse"""
			threading.Thread(target = wm.calibrate, daemon = True).start()

		def wii_recenter():
			"""recenter the WiiHeadMouse"""
			threading.Thread(target = wm.recenter, daemon = True).start()

		def wii_start_scrolling():
			"""start scrolling"""
			wm.startScrolling()

		def wii_stop_scrolling():
			"""stop scrolling"""
			wm.stopScrolling()

else:
	wm.connect()
	wm.calibrate()
	while True:
		time.sleep(1)
