#!/usr/bin/python3

'''
    File name: PiHueRoom.py
    Author: Tim Richardson
    Date created: 04/07/2017
    Date last modified: 10/07/2017
    Python Version: 3.4

	Description:
	Control Philips Hue lights using a Pimoroni TouchpHAT - Room version

    Requirements:
    * Raspberry Pi (http://raspberrypi.org/)
    * Philips Hue (http://www2.meethue.com)
    * Pimoroni Touch pHAT (https://shop.pimoroni.com/products/touch-phat)

    The Raspberry Pi must be on the same network as the Hue bridge
    You must set the bridgeip to be the IP address of your bridge
    and edit the room constant 'roomname'

    You can edit/expand the colour 'xy' values and the alerts
'''

# Import libraries
# Install phue and touchphat with pip3
# pip3 install phue
# pip3 install touchphat
from phue import Bridge
import rainbowhat as rh
import time

# ==============================================================================================
# Setup
# ==============================================================================================
rh.rainbow.clear()
rh.rainbow.show()
rh.display.clear()
rh.display.show()
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Stuff you need to change!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# The IP address of the Hue bridge and a list of lights you want to use
bridgeip = '192.168.0.241'  # <<<<<<<<<<<
# The 'group' of lights you want to change - i.e. the Room Name in the Hue app
# roomname = 'Hut 8'  # <<<<<<<<<<<

# -----------------------------------------------------------------------------------------------
# Do some internal setup
# -----------------------------------------------------------------------------------------------
# Connect to the bridge
b = Bridge(bridgeip)

# IMPORTANT: If running for the first time:
#    Uncomment the b.connect() line
#    Press button on bridge
#    Run the code
# This will save your connection details in /home/pi/.python_hue
# Delete that file if you change bridges
# b.connect() # <<<<<<<<<<
# b = Bridge('192.168.0.241')
# {"192.168.0.241": {"username": "LUDZE-wKv6nr5eticaudf3yDskcWn3Eje7jqz89O"}}
# Find the room number from the room name
allrooms = b.get_group()
print('allrooms set')
rooms = {}

for num, room in enumerate(allrooms.keys(), start=1):
    rooms[num] = {'name': allrooms[room]['name'][:4].upper(),
                  'is_on': allrooms[room]['state']['any_on']}

number_rooms = len(allrooms)


if len(allrooms) == 0:
    print('The rooms in your Hue network are not found. Please try again. Exiting.')
    exit()

# set inital room to show 1 and display room
selected_room = 1

# Wait time between sending messages to the bridge - to stop congestion
defaultwaittime = 0.41

is_asleep = False
# = End of Setup ============================================================================

# -------------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------------

# Display room name on board


def display_room_name():
    rh.display.clear()
    rh.display.print_str(rooms.get(selected_room)['name'])
    rh.display.show()
    display_led_indicator()

# display sleep, turn off display and led


def go_to_sleep():
    print('go to sleep called')
    global is_asleep
    is_asleep = True
    rh.display.clear()
    rh.display.show()
    rh.rainbow.clear()
    rh.rainbow.show()

# Identifies if any of the lamps in the room are on
# Return Value: True if any lamps are on, otherwise False


def islampon():
    global selected_room
    result = False
    roomon = b.get_group(selected_room)
    result = roomon['state']['any_on']
    return result


def display_led_indicator():
    if rooms[selected_room]['is_on']:
        rh.rainbow.set_pixel(3, 255, 211, 0, 0.1)
    else:
        rh.rainbow.clear()
    rh.rainbow.show()

# When the A button is pressed, run redalert
@rh.touch.A.press()
def touch_a(channel):
    print('Button A pressed')
    rh.lights.rgb(1, 0, 0)
    global selected_room, number_rooms, is_asleep
    if is_asleep:
        display_room_name()
        is_asleep = False
        return
    elif selected_room > 1:
        selected_room = selected_room - 1
    else:
        selected_room = number_rooms
    display_room_name()


@rh.touch.A.release()
def release_a(channel):
    print('Button A Released')
    rh.lights.rgb(0, 0, 0)


# When the B button is pressed, go to next room
@rh.touch.B.press()
def touch_b(channel):
    print('Button B pressed')
    rh.lights.rgb(0, 1, 0)
    global selected_room, number_rooms, is_asleep
    if is_asleep:
        display_room_name()
        is_asleep = False
        return
    elif selected_room < number_rooms:
        selected_room = selected_room + 1
    else:
        selected_room = 1
    display_room_name()


@rh.touch.B.release()
def release_b(channel):
    print('Button B Released')
    rh.lights.rgb(0, 0, 0)

# When the C button is pressed, run toggle light off/on
@rh.touch.C.press()
def touch_c(channel):
    print('Button C pressed')
    rh.lights.rgb(0, 0, 1)
    global selected_room, is_asleep
    if is_asleep:
        display_room_name()
        is_asleep = False
        return
    lampon = islampon()
    if lampon:
        b.set_group(selected_room, 'on', False)
        rooms[selected_room]['is_on'] = False
    else:
        b.set_group(selected_room, 'on', True)
        rooms[selected_room]['is_on'] = True
    display_led_indicator()
    time.sleep(defaultwaittime)


@rh.touch.C.release()
def release_c(channel):
    print('Button C Released')
    rh.lights.rgb(0, 0, 0)


# ================================================================
# Main loop - keep going forever
# ================================================================
while True:
    go_to_sleep()
    time.sleep(18)
