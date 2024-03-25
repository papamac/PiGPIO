# coding=utf-8
"""
###############################################################################
#                                                                             #
#                            Pi GPIO Indigo Plugin                            #
#                        MODULE conditionalLogging.py                         #
#                                                                             #
###############################################################################

  BUNDLE:  Raspberry Pi General Purpose Input/Output for Indigo
           (Pi GPIO.indigoPlugin)
  MODULE:  conditionalLogging.py
   TITLE:  Conditional logging by message type
FUNCTION:  conditionalLogging.py provides optional logging of four message
           types (analog, digital, resource, and startStop) based on user
           selections in the plugin.py pluginPrefs.
   USAGE:  conditionalLogging.py is included by the two primary plugin modules,
           plugin.py and ioDevices.py  Its methods are called as needed by
           module functions and methods.
  AUTHOR:  papamac
 VERSION:  0.9.2
    DATE:  September 10, 2023

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

Pi GPIO PLUGIN BUNDLE DESCRIPTION:

The Pi GPIO plugin bundle has two primary Python modules: plugin.py
encapsulates the plugin device behavior in the Plugin class, and this module,
ioDevices.py, encapsulates detailed io device behavior in the IoDevice
class and its six subclasses.  An IoDevice subclass instance is created for
each plugin device started by plugin.py.  The plugin bundle contains two
supporting Python modules: rgpio.pi with classes/methods to access the rgpio
daemon and conditionalLogging.py to provide flexible Indigo logging by message
type and logging level.  It also includes several xml files that define plugin
devices, actions, and events.

MODULE conditionalLogging.py DESCRIPTION:

The PluginConfig.xml defines four types of messages that are conditionally
logged by the ioDevices.py module: analog, digital, resource, and
startStop.  The pluginPrefs ConfigUi allows the user to select one or more of
these message types for optional logging.  Messages are logged only if they are
selected.  Some are logged at the DEBUG logging level and some are logged at
the INFO level.  With the ability to filter logged messages by both message
type and logging level, the user can flexibly configure the log to meet his
needs.  This is most helpful with detailed debug messages.

The conditionalLogging.py module provides two classes with methods to implement
this flexible logging feature.  The LD class has methods LD.analog, LD.digital,
LD.resource, and LD.startStop to log each of the message types at the DEBUG
logging level.  Similarly, the LI class has methods to log each of the message
types at the INFO level.  These classes and methods are called by functions and
methods in the ioDevices.py module as appropriate.

The LD and LI classes each have an init method to allow their other methods to
access the plugin.py module's pluginPrefs.  The Plugin class __init__ method
calls LD.init and LI.init with the plugin instance object as an argument.
LD.init and LI.init save the plugin object as a class constant named PLUGIN.
The message type methods can then access LD.PLUGIN.pluginPrefs or
LI.PLUGIN.pluginPrefs to obtain the currently selected message types from the
list pluginPrefs['loggingMessageTypes'].

CHANGE LOG:

Major changes to the Pi GPIO plugin are described in the CHANGES.md file in the
top level bundle directory.  Changes of lesser importance may be described in
individual module docstrings if appropriate.

v0.7.2    3/5/2023  Add conditional logging by message type.
v0.9.2   9/10/2023  (1) Add init methods to classes LD and LI to capture the
                    plugin object from plugin.py object initialization.  Use
                    the plugin object in LD and LI methods to directly access
                    pluginPrefs.
                    (2) Update module docstring in preparation for initial
                    release.
"""
###############################################################################
#                                                                             #
#                       MODULE conditionalLogging.py                          #
#                   DUNDERS, IMPORTS, and GLOBAL Constants                    #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '0.9.2'
__date__ = '9/10/2023'

from logging import getLogger

L = getLogger("Plugin")        # Use the Indigo Plugin logger.


###############################################################################
#                                                                             #
#                       MODULE conditionalLogging.py                          #
#                                  CLASS LD                                   #
#                                                                             #
###############################################################################

class LD:
    """" Methods for conditional debug logging by message type. """
    PLUGIN = None

    @staticmethod
    def init(plugin):
        """ Save the plugin instance object for use by other methods. """
        LD.PLUGIN = plugin

    @staticmethod
    def analog(message, *args, **kwargs):
        """ Log analog messages if requested in pluginPrefs """
        if 'analog' in LD.PLUGIN.pluginPrefs['loggingMessageTypes']:
            L.debug(message, *args, **kwargs)

    @staticmethod
    def digital(message, *args, **kwargs):
        """ Log digital messages if requested in pluginPrefs """
        if 'digital' in LD.PLUGIN.pluginPrefs['loggingMessageTypes']:
            L.debug(message, *args, **kwargs)

    @staticmethod
    def resource(message, *args, **kwargs):
        """ Log resource messages if requested in pluginPrefs """
        if 'resource' in LD.PLUGIN.pluginPrefs['loggingMessageTypes']:
            L.debug(message, *args, **kwargs)

    @staticmethod
    def startStop(message, *args, **kwargs):
        """ Log startStop messages if requested in pluginPrefs """
        if 'startStop' in LD.PLUGIN.pluginPrefs['loggingMessageTypes']:
            L.debug(message, *args, **kwargs)


###############################################################################
#                                                                             #
#                       MODULE conditionalLogging.py                          #
#                                  CLASS LI                                   #
#                                                                             #
###############################################################################

class LI:
    """" Methods for conditional info logging by message type. """
    PLUGIN = None

    @staticmethod
    def init(plugin):
        """ Save the plugin instance object for use by other methods. """
        LI.PLUGIN = plugin

    @staticmethod
    def analog(message, *args, **kwargs):
        """ Log analog messages if requested in pluginPrefs """
        if 'analog' in LI.PLUGIN.pluginPrefs['loggingMessageTypes']:
            L.info(message, *args, **kwargs)

    @staticmethod
    def digital(message, *args, **kwargs):
        """ Log digital messages if requested in pluginPrefs """
        if 'digital' in LI.PLUGIN.pluginPrefs['loggingMessageTypes']:
            L.info(message, *args, **kwargs)

    @staticmethod
    def resource(message, *args, **kwargs):
        """ Log resource messages if requested in pluginPrefs """
        if 'resource' in LI.PLUGIN.pluginPrefs['loggingMessageTypes']:
            L.info(message, *args, **kwargs)

    @staticmethod
    def startStop(message, *args, **kwargs):
        """ Log startStop messages if requested in pluginPrefs """
        if 'startStop' in LI.PLUGIN.pluginPrefs['loggingMessageTypes']:
            L.info(message, *args, **kwargs)
