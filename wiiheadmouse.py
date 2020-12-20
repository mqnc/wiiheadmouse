

UDP_IP = "127.0.0.1"
UDP_PORT = 7711
SCROLL_FACTOR = -0.4
SCROLL_MODE = 'touchpad' # joystick or touchpad

import sys
import time
import os
import threading
import math
import socket
import traceback

from pynput.mouse import Controller, Button
import pywiiuse as wiiuse

mouse = Controller()
def moveMouse(x, y):
	mouse.position = (x, y)
def scrollMouse(y):
	mouse.scroll(0, y)
moveMouse(30000, 30000)
W, H = mouse.position
def leftPress():
	mouse.press(Button.left)
def leftRelease():
	mouse.release(Button.left)
def rightPress():
	mouse.press(Button.right)
def rightRelease():
	mouse.release(Button.right)
def middlePress():
	mouse.press(Button.middle)
def middleRelease():
	mouse.release(Button.middle)

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
	FINE_MOUSING = 3
	SCROLLING = 4
	CALIBRATING = 5
	QUIT = 6

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
		#wiiuse.cleanup(self.wiimotes, 1)

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
					self.lastIR = time.time()
					self.cursorMsr = (x/n, y/n)

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

	def project(self, xy):
		return (
			lerp(
				self.caliPt1[0], self.caliPt2[0],
				50, W-50,
				xy[0]
			) - self.offset[0],
			lerp(
				self.caliPt1[1], self.caliPt2[1],
				50, W-50,
				xy[1]
			) - self.offset[1]
		)

	def controlMouse(self):
		while not self.mode == self.QUIT:
			if time.time() > self.lastIR + 0.1:
				time.sleep(0.1)
				continue

			if self.mode == self.MOUSING or self.mode == self.FINE_MOUSING:
				targetX, targetY = self.project(self.cursorSmooth)

				if self.mode == self.FINE_MOUSING:
					targetX = self.focus[0] + 0.2 * (targetX - self.focus[0])
					targetY = self.focus[1] + 0.2 * (targetY - self.focus[1])
				moveMouse(targetX, targetY)

				time.sleep(0.016)
			elif self.mode == self.SCROLLING:
				if SCROLL_MODE == 'joystick':
					d = self.cursorSmooth[1] - self.scrollStart[1]
					dir = 1 if d >= 0 else -1
					if abs(d) > 50:
						speed = ((abs(d) - 50)/20)**1.7 * SCROLL_FACTOR
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
				elif SCROLL_MODE == 'touchpad':
					d = self.cursorSmooth[1] - self.scrollStart[1]
					desiredPosition = round(d * SCROLL_FACTOR)
					scrollMouse(desiredPosition - self.scrollPosition)
					self.scrollPosition = desiredPosition
					time.sleep(0.1)
				else:
					time.sleep(0.1)
			else:
				time.sleep(0.1)

	def stutter(self):
		before = self.mode
		self.mode = self.INACTIVE
		time.sleep(0.2)
		if self.mode == self.INACTIVE:
			self.mode = before

	def startFine(self):
		if self.mode == self.MOUSING:
			self.mode = self.FINE_MOUSING
			self.focus = self.project(self.cursorSmooth)
		else:
			print("can only fine mouse in mouse mode")

	def stopFine(self):
		if self.mode == self.FINE_MOUSING:
			self.mode = self.MOUSING
		else:
			print("wasn't fine mousing")

	def mouse(self):
		if self.mode == self.SCROLLING or self.mode == self.INACTIVE:
			self.mode = self.MOUSING
		else:
			print("not in scroll mode or sleep mode")

	def scroll(self):
		if self.mode == self.MOUSING or self.mode == self.INACTIVE:
			self.mode = self.SCROLLING
			self.scrollStart = self.cursorSmooth
			self.scrollPosition = 0
		else:
			print("not in mouse mode or sleep mode")

	def sleep(self):
		if self.mode == self.MOUSING or self.mode == self.SCROLLING:
			self.mode = self.INACTIVE
		else:
			print("not in mouse mode or scroll mode")

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
		self.cursorSmooth = (1024/2, 768/2)
		self.scrollStart = (1024/2, 768/2)
		self.focus = (1024/2, 768/2)
		self.scrollPosition = 0
		self.caliPt1 = (100, 100)
		self.caliPt2 = (1024-100, 768-100)
		self.offset = (0, 0)
		self.lastIR = 0

		threading.Thread(target = self.watchdog, daemon = True).start()
		threading.Thread(target = self.poller, daemon = True).start()
		threading.Thread(target = self.smoothen, daemon = True).start()
		threading.Thread(target = self.controlMouse, daemon = True).start()

moveMouse(W/2, H/2)
wm = WiiMouse()
wm.connect()

api = {
	"CONNECT": wm.connect,
	"DISCONNECT": wm.disconnect,
	"CALIBRATE": wm.calibrate,
	"RECENTER": wm.recenter,
	"START_FINE": wm.startFine,
	"STOP_FINE": wm.stopFine,
	"MOUSE": wm.mouse,
	"SCROLL": wm.scroll,
	"SLEEP": wm.sleep,
	"STUTTER": wm.stutter,
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

def stutterLeftPress():
	wm.stutter()
	leftPress()
def stutterRightPress():
	wm.stutter()
	rightPress()
def stutterMiddlePress():
	wm.stutter()
	middlePress()
def doubleClick():
	wm.stutter()
	leftPress()
	time.sleep(0.01)
	leftRelease()
	time.sleep(0.01)
	leftPress()
	time.sleep(0.01)
	leftRelease()

try:
	import footpedals as fp
	ped = fp.PedalManager()
	ped.register(fp.LEFT + fp.PRESS, stutterLeftPress)
	ped.register(fp.LEFT + fp.RELEASE, leftRelease)
	ped.register(fp.RIGHT + fp.PRESS, stutterRightPress)
	ped.register(fp.RIGHT + fp.RELEASE, rightRelease)
	ped.register(fp.MIDDLE + fp.PRESS, stutterMiddlePress)
	ped.register(fp.MIDDLE + fp.RELEASE, middleRelease)
	ped.register(fp.FINE + fp.PRESS, wm.startFine)
	ped.register(fp.FINE + fp.RELEASE, wm.stopFine)
	ped.register(fp.SCROLL + fp.PRESS, wm.scroll)
	ped.register(fp.SCROLL + fp.RELEASE, wm.mouse)
	ped.register(fp.DOUBLE + fp.PRESS, doubleClick)
except:
	traceback.print_exc()

while True:
	data, addr = sock.recvfrom(1024)
	msg = data.decode("ascii")
	if msg in api:
		api[msg]()
