
import threading
from inputs import get_gamepad

LEFT = "BTN_WEST"
MIDDLE = "BTN_C"
RIGHT = "BTN_Z"
DOUBLE = "BTN_NORTH"
SCROLL = "BTN_SOUTH"
FINE = "BTN_EAST"

PRESS = "_PRESS"
RELEASE = "_RELEASE"

class PedalManager:
	def __init__(self):
		self.handlers = {}
		threading.Thread(target = self.poller, daemon = True).start()

	def register(self, event, handler):
		self.handlers[event] = handler

	def poller(self):
		while True:
			events = get_gamepad()
			for event in events:
				#print(event)
				if event.ev_type == "Key":
					ev = event.code + (PRESS if event.state == 1 else RELEASE)
					if ev in self.handlers:
						self.handlers[ev]()
