# WiiHeadMouse
This is WiiHeadMouse, a module for using the WiiMote as a mouse in Talon Voice or stand alone.

## Hardware Installation
You need a WiiMote connected to your head (~~I use a bike helmet~~ now I have attached it to the headband of my headphones) and an infrared LED or the sensor bar above or under your screen.

For clicking and stuff, I built myself a board with foot pedals which identifies as a gamepad. This program will attempt to connect to his. But you can also configure Talon to do the clicking for you.

## Software Installation
Install wiiuse from here: https://github.com/wiiuse/wiiuse

Furthermore, you need to pip install pynput. If you want to use a gamepad for clicking, you also need to pip install inputs.

If you want to use WiiHeadMouse with Talon Voice, create a link inside your talon user folder pointing to the talon folder in this project.

## Stand Alone Usage
Just execute wiiheadmouse.py and you can control the cursor with your head. The program will listen on port 7711 for the following UDP messages:

* CONNECT: connect to the WiiMote (press buttons 1 and 2 on the WiiMote) Once connected, the mouse cursor will magically follow your head (not your eyes).
* DISCONNECT: disconnect; be aware that reconnecting somehow doesn't work yet, you need to restart talon if you want to connect again.
* CALIBRATE: perform a calibration: Just follow the cursor with your face facing direction. The dimensions of your screen will be estimated and the cursor will be centered.
* RECENTER: and then staring in the middle of the screen recenters the cursor without measuring the screen again.
* START_FINE: refine the mouse position around its current location
* STOP_FINE: stop fine mode
* MOUSE: use the WiiMote to move the mouse (default)
* SCROLL: start scrolling mode: Move your head up and down to stroll up and down. This was tuned for Ubuntu, you might want to adjust SCROLL_MULTIPLIER in wiiheadmouse.py. You can also change SCROLL_MODE between joystick and touchpad. Joystick means you control the scrolling speed, touchpad means you control the scrolling position.
* SLEEP: don't use the WiiMote but to keep the connection up
* STUTTER: don't move the mouse for a bit, useful for clicking

## Talon Usage
Run wiiheadmouse.py, talon will connect to it through UDP.

Check out talon/wiiclient.talon to see what you can say for in action with the wiiheadmouse.
