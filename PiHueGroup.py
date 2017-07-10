#!/usr/bin/python3

'''
    File name: PiHueGroup.py
    Author: Tim Richardson
    Date created: 04/07/2017
    Date last modified: 10/07/2017
    Python Version: 3.4

	Description:
	Control Philips Hue lights using a Pimoroni TouchpHAT - group light version

    Requirements:
    * Raspberry Pi (http://raspberrypi.org/)
    * Philips Hue (http://www2.meethue.com)
    * Pimoroni TouchpHAT (https://shop.pimoroni.com/products/touch-phat)

    The Raspberry Pi must be on the same network as the Hue bridge
    You must set the bridgeip to be the IP address of your bridge
    and edit the list of lights in your network in 'lights[]'

    You can edit/expand the colour 'xy' values and the alerts
'''

# Import libraries
# Install phue and touchphat with pip3
# pip3 install phue
# pip3 install touchphat
from phue import Bridge
import touchphat
import time

# ==============================================================================================
# Setup
# ==============================================================================================
touchphat.all_off()

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Stuff you need to change!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# The IP address of the Hue bridge and a list of lights you want to use
bridgeip = '192.168.13.178'  # <<<<<<<<<<<
# The 'group' of lights you want to change - i.e. the Room Name in the Hue app
groupname = 'Hut 8'  # <<<<<<<<<<<

# -----------------------------------------------------------------------------------------------
# Do some internal setup
# -----------------------------------------------------------------------------------------------
# Connect to the bridge
b = Bridge(bridgeip)

# IMPORTANT: If running for the first time:
#    Uncomment the b.connect() line
#    Ppress button on bridge
#    Run the code
# This will save your connection details in /home/pi/.python_hue
# Delete that file if you change bridges
# b.connect() # <<<<<<<<<<

# Find the group number from the group name
allgroups = b.get_group()
groupnumber = 0
for group in allgroups.keys():
    if allgroups[group]['name'] == groupname:
        groupnumber = int(group)
        break

if groupnumber == 0:
    print('The group name you have supplied in groupname is not recognised. Please try again. Exiting.')
    exit()

# Hue 'xy' colours - expand at will
redxy = (0.675, 0.322)
greenxy = (0.4091, 0.518)
bluexy = (0.167, 0.04)
yellowxy = (0.4325035269415173, 0.5007488105282536)
bluevioletxy = (0.2451169740627056, 0.09787810393609737)
orangexy = (0.6007303214398861, 0.3767456073628519)
whitexy = (0.32272672086556803, 0.3290229095590793)

# Alert Patterns
# Used to change the status of lights
# First two numbers are the number of repeat cycles, and the delay between changes
# Followed by dictionaries of the change of light status.
# Use any valid HUE setting - e.g. on, bri, xy, ct, sat, hue, transformationtime
# But remember that dimmable lamps only dim ('bri') and don't change colour ('no 'xy')
redAlert = [6, 0.5,
            {'on': True, 'bri': 255, 'xy': redxy},
            {'on': False}]

amberAlert = [6, 0.5,
              {'on': True, 'bri': 255, 'xy': orangexy},
              {'on': False}]

greenAlert = [6, 0.5,
              {'on': True, 'bri': 255, 'xy': greenxy},
              {'on': False}]

blueAlert = [6, 0.5,
             {'on': True, 'bri': 255, 'xy': bluexy},
             {'on': False}]

# For turning the lights all on to bright white
allwhite = {'on': True, 'bri': 255, 'xy': whitexy}

# If an alert is ongoing, this will be True
inalert = False

# Wait time between sending messages to the bridge - to stop congestion
defaultwaittime = 0.41


# = End of Setup ============================================================================

# -------------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------------

# Get the status of the group
def getgroupstatus():
    groupstatus = b.get_group(groupnumber)
    return groupstatus


# Return the status of the group to what it was before the alert
# Input: Dictionary of the status of the group (obtained from getgroupstatus()
def putgroupstatus(groupstatus):
    global groupnumber

    b.set_group(groupnumber, {'xy': groupstatus['action']['xy'], 'bri': groupstatus['action']['bri'],
                              'on': groupstatus['action']['on']}, transitiontime=0)
    time.sleep(defaultwaittime)


    # Runs through the alert dictionary defined in alertpattern
    # Input: alertpattern containes the pre-defined alert pattern


def huealert(alertpattern):
    global inalert, groupnumber

    # Only run if we're not already in an alert
    if not inalert:
        inalert = True
        # Get the current status of the lamps
        preAlertStatus = getgroupstatus()

        # Using the pre-defined alert patterns, change the lamp status
        for rep in range(alertpattern[0]):
            for runalert in range(2, len(alertpattern)):
                b.set_group(groupnumber, alertpattern[runalert], transitiontime=0)
                time.sleep(alertpattern[1])

        # Return the lamps to the previous status
        putgroupstatus(preAlertStatus)
        inalert = False


# Identifies if any of the lamps in the group are on
# Return Value: True if any lamps are on, otherwise False
def islampon():
    global inalert, groupnumber

    result = False

    if not inalert:
        groupon = b.get_group(groupnumber)
        result = groupon['state']['any_on']

    return result


# When the A button is pressed, run redalert
@touchphat.on_touch("A")
def toucha():
    huealert(redAlert)
    touchphat.led_off("A")


# When the B button is pressed, run amberAlert
@touchphat.on_touch("B")
def touchb():
    huealert(amberAlert)
    touchphat.led_off("B")


# When the C button is pressed, run greenAlert
@touchphat.on_touch("C")
def touchc():
    huealert(greenAlert)
    touchphat.led_off("C")


# When the D button is pressed, run blueAlert
@touchphat.on_touch("D")
def touchd():
    huealert(blueAlert)
    touchphat.led_off("D")


# When 'enter' is pressed, the group is turned on to 'bright white'
# (i.e. what is defined in the dictionary 'allwhite'. Change at will.
@touchphat.on_touch("Enter")
def touchenter():
    global groupnumber, allwhite

    b.set_group(groupnumber, allwhite, transitiontime=0)
    time.sleep(defaultwaittime)
    touchphat.led_off("Enter")
    touchphat.led_on("Back")


# When the Back button is pressed, toggle the lamp on/off status
@touchphat.on_touch("Back")
def touchback():
    global inalert, groupnumber

    if not inalert:
        lampon = islampon()
        inalert = True
        if lampon:
            b.set_group(groupnumber, 'on', False)
            touchphat.led_off("Back")
        else:
            b.set_group(groupnumber, 'on', True)
            touchphat.led_on("Back")
        time.sleep(1)
        inalert = False


# ================================================================
# Main loop - keep going forever
# ================================================================
while True:
    if inalert:
        time.sleep(1)
    else:
        if islampon():
            touchphat.led_on("Back")
        else:
            touchphat.led_off("Back")
        time.sleep(10)
