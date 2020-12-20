
import socket
from talon import Module

UDP_IP = "127.0.0.1"
UDP_PORT = 7711

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

mod = Module()

@mod.action_class
class Actions:

	def wii_connect():
		"""connect to the WiiHeadMouse"""
		sock.sendto(b"CONNECT", (UDP_IP, UDP_PORT))

	def wii_disconnect():
		"""disconnect from the WiiHeadMouse"""
		sock.sendto(b"DISCONNECT", (UDP_IP, UDP_PORT))

	def wii_calibrate():
		"""calibrate the WiiHeadMouse"""
		sock.sendto(b"CALIBRATE", (UDP_IP, UDP_PORT))

	def wii_recenter():
		"""recenter the WiiHeadMouse"""
		sock.sendto(b"RECENTER", (UDP_IP, UDP_PORT))

	def wii_start_fine():
		"""fine motion"""
		sock.sendto(b"START_FINE", (UDP_IP, UDP_PORT))

	def wii_stop_fine():
		"""stop fine motion"""
		sock.sendto(b"STOP_FINE", (UDP_IP, UDP_PORT))

	def wii_mouse():
		"""mouse mode"""
		sock.sendto(b"MOUSE", (UDP_IP, UDP_PORT))

	def wii_scroll():
		"""scroll mode"""
		sock.sendto(b"SCROLL", (UDP_IP, UDP_PORT))

	def wii_sleep():
		"""sleep mode"""
		sock.sendto(b"SLEEP", (UDP_IP, UDP_PORT))

	def wii_stutter():
		"""don't move for a moment"""
		sock.sendto(b"STUTTER", (UDP_IP, UDP_PORT))
