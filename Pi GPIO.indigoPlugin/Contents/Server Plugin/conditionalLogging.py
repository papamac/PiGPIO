# coding=utf-8
###############################################################################
#                                                                             #
#                       MODULE conditionalLogging.py                          #
#                                                                             #
###############################################################################
"""
 PACKAGE:  Raspberry Pi General Purpose Input/Output for Indigo
  MODULE:  conditionalLogging.py
   TITLE:  Conditional logging by message type
FUNCTION:  conditionalLogging.py

 ****************************** needs work *************************************

           provides classes to define and manage five
           different categories of Pi GPIO devices.  Each class initializes,
           configures, starts, and stops io device objects for each Indigo
           device.  Class methods also execute device actions and update
           device states.
   USAGE:  pigpioDevices.py is included by the primary plugin class,
           Plugin.py.  Its methods are called as needed by Plugin.py methods.
  AUTHOR:  papamac
 VERSION:  0.7.2
    DATE:  March 5, 2023


UNLICENSE:

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>


Pi GPIO SUMMARY DESCRIPTION:

Raspberry Pi is a powerful credit card sized computer with extensive General
Purpose Input/Output (GPIO) capabilities that make it an ideal addition to an
Indigo Home Automation System.  Physical analog and digital input/output
devices, hosted on the Pi, are linked to Indigo device objects, giving Indigo
the ability to sense the real world and manage it in near real time.  One or
more Pi's connect to the Indigo host via wired or wireless ethernet.  Each Pi
runs a pigpio daemon (written by joan2937) that manages the interface between
the Pi GPIO's and this Pi GPIO plugin.

See the README.md file in the top level PiGPIO folder for more functional
details and operating instructions.  For details on the Raspberry Pi, its GPIO
system, and joan2937's amazing pigpio library, please refer to:

RPi computers:      <https://www.raspberrypi.com/products/
RPi OS:             <https://www.raspberrypi.com/software/>
RPi official doc's: <https://www.raspberrypi.com/documentation/computers/>
RPi GPIO system :   <https://www.raspberrypi.com/documentation/computers
                     /os.html#gpio-and-the-40-pin-header>
pigpio library:     <https://abyz.me.uk/rpi/pigpio/>
pigpio code:        <https://github.com/joan2937/pigpio/>


DEPENDENCIES/LIMITATIONS:

****************************** needs work *************************************


CHANGE LOG:

Major changes to the Pi GPIO plugin are described in the CHANGES.md file in the
top level bundle directory.  Changes of lesser importance may be described in
individual module docstrings if appropriate.

v0.7.2    3/5/2023  Add conditional logging by message type.
"""
###############################################################################
#                                                                             #
#                       MODULE conditionalLogging.py                          #
#                   DUNDERS, IMPORTS, and GLOBAL Constants                    #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '0.7.2'
__date__ = '3/5/2023'

from logging import getLogger

L = getLogger("Plugin")        # Use the Indigo Plugin logger.
LOGGING_MESSAGE_TYPES = ['analog', 'digital', 'resource', 'startStop']


###############################################################################
#                                                                             #
#                       MODULE conditionalLogging.py                          #
#                                  CLASS LD                                   #
#                                                                             #
###############################################################################

class LD:
    """"
    Methods for conditional debug logging by message type.
    """
    @staticmethod  # Analog device debug logging.
    def analog(message, *args, **kwargs):
        if 'analog' in LOGGING_MESSAGE_TYPES:
            L.debug(message, *args, **kwargs)

    @staticmethod  # Digital device debug logging.
    def digital(message, *args, **kwargs):
        if 'digital' in LOGGING_MESSAGE_TYPES:
            L.debug(message, *args, **kwargs)

    @staticmethod  # pigpiod resource management debug logging.
    def resource(message, *args, **kwargs):
        if 'resource' in LOGGING_MESSAGE_TYPES:
            L.debug(message, *args, **kwargs)

    @staticmethod  # Starting/stopping debug logging.
    def startStop(message, *args, **kwargs):
        if 'startStop' in LOGGING_MESSAGE_TYPES:
            L.debug(message, *args, **kwargs)


###############################################################################
#                                                                             #
#                       MODULE conditionalLogging.py                          #
#                                  CLASS LI                                   #
#                                                                             #
###############################################################################

class LI:
    """"
    Methods for conditional info logging by message type.
    """
    @staticmethod  # Starting info logging.
    def startStop(message, *args, **kwargs):
        if 'startStop' in LOGGING_MESSAGE_TYPES:
            L.info(message, *args, **kwargs)
