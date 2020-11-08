# WiiHeadMouse
This is WiiHeadMouse, a module for using the WiiMote as a mouse in Talon Voice or stand alone.

## Status
This is an initial prototype which can only do mouse motion, no clicking or scrolling yet. It also doesn't handle any errors yet.

BE PREPARED THAT TALON MIGHT CRASH OR YOUR MOUSE GETS STUCK AND YOU HAVE TO KILL THE PROGRAM USING ONLY YOUR KEYBOARD!

That being said, I am already using it and it works fine.

## Hardware Installation
You need a WiiMote connected to your head (I use a bike helmet) and an infrared LED or the sensor bar above or under your screen.

## Software Installation
You need to install wiiuse from here: https://github.com/wiiuse/wiiuse

If you want to use WiiHeadMouse with Talon Voice, just clone this repository into the Talon user folder and you're good to go.

Otherwise you need to install pynput and then execute wiiheadmouse.py.

## Usage
When the program is started, you need to connect your WiiMote by pressing buttons 1 and 2 on it.

Once connected, an initial calibration will be performed. Just follow the cursor with your face facing direction.

Afterwards the mouse cursor will magically follow your head (not your eyes).
