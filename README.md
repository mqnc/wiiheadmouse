# WiiHeadMouse
This is WiiHeadMouse, a module for using the WiiMote as a mouse in Talon Voice or stand alone.

## Status
This is a prototype which can only do mouse motion and scrolling, no clicking. It also doesn't handle any errors yet.

BE PREPARED THAT TALON MIGHT CRASH OR YOUR MOUSE GETS STUCK AND YOU HAVE TO KILL THE PROGRAM USING ONLY YOUR KEYBOARD!

That being said, I am already using it and it works fine for me.

## Hardware Installation
You need a WiiMote connected to your head (I use a bike helmet) and an infrared LED or the sensor bar above or under your screen.

## Software Installation
Install wiiuse from here: https://github.com/wiiuse/wiiuse

If you want to use WiiHeadMouse with Talon Voice, just clone this repository into the Talon user folder and you're good to go.

Otherwise you need to install pynput.

## Talon Usage

**"wii connect"** - connect to the WiiMote (press buttons 1 and 2 on the WiiMote) Once connected, the mouse cursor will magically follow your head (not your eyes).

**"wii disconnect"** - disconnect; be aware that reconnecting somehow doesn't work yet, you need to restart talon if you want to connect again.

**"wii calibrate"** - perform a calibration: Just follow the cursor with your face facing direction. The dimensions of your screen will be estimated and the cursor will be centered.

**"wii recenter"** - and then staring in the middle of the screen recenters the cursor without measuring the screen again.

**"wii scroll"** - start scrolling mode: Move your head up and down to stroll up and down. This was tuned for Ubuntu, you might want to adjust SCROLL_MULTIPLIER in wiiheadmouse.py. 

## Stand Alone Usage
Just execute wiiheadmouse.py. A calibration will be performed (follow the cursor with your face facing direction) and then you can control the cursor with your head.
