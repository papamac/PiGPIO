# coding=utf-8
###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                                                                             #
###############################################################################
"""
 PACKAGE:  Raspberry Pi General Purpose Input/Output for Indigo
  MODULE:  pigpioDevices.py
   TITLE:  Pi GPIO device management
FUNCTION:  pigpioDevices.py provides classes to define and manage five
           different categories of Pi GPIO devices.  Each class initializes,
           configures, starts, and stops io device objects for each Indigo
           device.  Class methods also execute device actions and update
           device states.
   USAGE:  pigpioDevices.py is included by the primary plugin class,
           Plugin.py.  Its methods are called as needed by Plugin.py methods.
  AUTHOR:  papamac
 VERSION:  0.9.1
    DATE:  June 17, 2023

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

pigpioDevices.py DESCRIPTION:

****************************** needs work *************************************

DEPENDENCIES/LIMITATIONS:

****************************** needs work *************************************

CHANGE LOG:

Major changes to the Pi GPIO plugin are described in the CHANGES.md file in the
top level bundle directory.  Changes of lesser importance may be described in
individual module docstrings if appropriate.

v0.5.0  11/28/2021  Fully functional beta version with minimal documentation.
v0.5.2   1/19/2022  Use common IODEV_DATA dictionary to unambiguously identify
                    a device's interface type (GPIO, I2C, or SPI)
v0.5.3   3/28/2022  Generalize trigger execution, including an option to limit
                    triggers for frequently recurring events.  Add events for
                    pigpio errors with limited triggers for Start Errors and
                    Stop Errors.
v0.5.4   4/ 3/2022  Fix a bug in _executeEventTriggers.
v0.5.5   4/12/2022  Set option to limit triggers to be the default for all
                    event types.
v0.5.6   5/ 2/2022  Fix a bug that erroneously disables the gpio bounce filter
                    when bounce filter warning messages are not selected.
v0.5.7   7/20/2022  Update for Python 3.
v0.5.8   9/11/2022  Add support for Docker Pi Relay devices and 8/10-bit dacs.
v0.5.9  10/12/2022  Add glitch filter option for built-in GPIO inputs.
v0.6.0  11/20/2022  Use properties in pluginProps and pluginPrefs directly
                    without duplicating them as ioDev instance objects.  Update
                    pigpio resource management to accurately maintain the
                    connection resource use counts.
v0.6.1  11/21/2022  Improve efficiency in interrupt relay.
v0.7.0   2/14/2023  (1) Implement common sensor value processing for both
                    analog input and analog output devices.  Optionally enable
                    sensor value percentage change detection, analog on/off
                    thresholding, and limit checking.
                    (2) Change the device types for analog input and analog
                    output devices to custom to enable optional selection of
                    the display state id for analog devices.
                    (3) Fix a bug in the ADC12 class that failed to read ADC
                    channels 4-7.
v0.7.1   2/15/2023  Simplify code for SPI integrity checks.
v0.7.2    3/5/2023  (1) Refactor and simplify code for pigpio resource
                    management, exception management, and interrupt processing.
                    (2) Add conditional logging by message type.
v0.8.0   3/20/2023  Change the device types for analog input and analog output
                    devices from custom types back to sensor and relay types
                    respectively.  Let these devices retain their native
                    display state id (onOffState), but allow the user to select
                    the apparent display state by manipulating the onOffState
                    uiValue.  This has the advantage of retaining the device
                    controls in the Indigo Home Window that are not available
                    for custom devices.
v0.8.1   5/13/2023  (1) Fix a bug in the initialization of digital outputs on
                    IOExpander devices.
                    (2) Change spi integrity check for ADC12 devices.  Use an
                    absolute change in the digital code on consecutive readings
                    to indicate failure rather than a percentage change in
                    consecutive voltage measurements.
                    (3) Refactor hardware interrupt relay management.  In the
                    IOExpander class, dynamically add and remove the interrupt
                    devices in response to ConfigUi changes.  In the PiGPIO
                    class, include add and remove methods that are invoked by
                    IOExpander.  Add a deviceDeleted method to the PiGPIODevice
                    class to remove interrupt devices that were deleted.
                    (4) Change spi bitRate units from kb/s to Mb/s.
v0.9.0    6/8/2023  Refactor pigpioDevices.py and plugin.py to reduce the
                    numbers of global variables shared across modules.  Create
                    new module-level methods in pigpioDevices to log startup
                    and shutdown device status summaries.
v0.9.1   6/17/2023  (1) Change _executeEventTriggers to save needed data in the
                    trigger plugin props vs. the device states or a variable.
                    (2) Remove the stop triggerEvent from the pigpioError
                    event type.
"""
###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                   DUNDERS, IMPORTS, and GLOBAL Constants                    #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '0.9.1'
__date__ = '6/17/2023'

from abc import ABC, abstractmethod
from datetime import datetime
from logging import getLogger
from random import random
from time import sleep

import indigo

from conditionalLogging import LD
import pigpio

# General global constants:

L = getLogger("Plugin")        # Use the Indigo Plugin logger.
ON, OFF = BIT = (1, 0)         # on/off states and valid bit values.
ON_OFF = ('off', 'on')         # onOffState text values.
GPIO, I2C, SPI = (0, 1, 2)     # Interface types.
IF = ('gpio', 'i2c-', 'spi-')  # Interface text values.
I2CBUS = 1                     # Primary i2c bus.
SPIBUS = 0                     # Primary spi bus.

# Global display image selector tuple indexed by the onOffState state.
# IMAGE_SEL[onOffState] = indigo image selector enumeration value

IMAGE_SEL = (indigo.kStateImageSel.SensorOff,  # Normal sensor off/on
             indigo.kStateImageSel.SensorOn)

# Global public dictionary of io device data keyed by io device type:
# IODEV_DATA[ioDevType] = (ioDevClass, interface)

IODEV_DATA = {
    'dkrPiRly': ('DockerPiRelay', I2C),
    'MCP23008': ('IOExpander',    I2C),   'MCP23017': ('IOExpander',   I2C),
    'MCP23S08': ('IOExpander',    SPI),   'MCP23S17': ('IOExpander',   SPI),
    'MCP3202':  ('ADC12',         SPI),   'MCP3204':  ('ADC12',        SPI),
    'MCP3208':  ('ADC12',         SPI),
    'MCP3422':  ('ADC18',         I2C),   'MCP3423':  ('ADC18',        I2C),
    'MCP3424':  ('ADC18',         I2C),
    'MCP4801':  ('DAC12',         SPI),   'MCP4802':  ('DAC12',        SPI),
    'MCP4811':  ('DAC12',         SPI),   'MCP4812':  ('DAC12',        SPI),
    'MCP4821':  ('DAC12',         SPI),   'MCP4822':  ('DAC12',        SPI),
    'pigpio':   ('PiGPIO',        GPIO)}

###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                   Global Internal Dictionaries and Lists                    #
#                                                                             #
###############################################################################

# Internal dictionary of io device instance objects keyed by device id:
# _ioDevices[dev.id] = <io device instance object>

_ioDevices = {}

# Internal list of io device counts indexed by the raspi host id and interface
# type:
# _ioDevCounts[pi id][interface type] = count

_ioDevCounts = {}

# Internal dictionary of pigpiod shared resources that are reserved/released by
# by multiple io devices.  Each entry in the dictionary is a tuple containing a
# resource value and a use count.  Resources are added when they are needed,
# but not currently in the dictionary; they are reserved by incrementing the
# use count, and released by decrementing the use count.  When a resource's use
# count becomes 0, it is removed from the dictionary and closed/stopped as
# needed to return it to the pigpio daemon.
# (resource, use count) = _resources[resource id]

_resources = {}


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                         Internal Module Functions                           #
#                                                                             #
# def _raiseRandomException(errorMessage, frequency=20)                       #
# def _hexStr(byteList)                                                       #
# def _executeEventTriggers(dev, eventType, eventName, description='')        #
# def _pigpioError(dev, errorType, errorMessage)                              #
#                                                                             #
###############################################################################


def _raiseRandomException(errorMessage, frequency=50):
    """
    Raise a random exception in a segment of code to test exception handling.
    frequency is the percentage of function calls that will be interrupted.
    """
    if random() < frequency / 100:
        raise Exception(errorMessage)


def _hexStr(byteList):
    """
    Convert a list of byte integers (0 - 255) to a text string of 2-digit
    hex values separated by spaces.  The byteList argument may be either a
    list of normal integers or a bytearray.  For example,
    _hexStr([2, 17, 255, 0xFF]) returns '02 11 ff ff'.
    """
    hexString = ''
    for byte in byteList:
        hexString += '%02x ' % byte
    return hexString[:-1]


def _executeEventTriggers(dev, eventType, eventName, description=''):
    """
    Execute all Indigo triggers for an eventType/eventName.  Save data needed
    to respond to the event the trigger object's pluginProps.
    """
    for trig in indigo.triggers.iter('self'):
        if trig.enabled and trig.pluginTypeId == eventType:
            pluginProps = trig.pluginProps
            triggerEvent = pluginProps['triggerEvent']
            if triggerEvent in ('any', eventName):
                pluginProps['datetime'] = str(datetime.now())
                pluginProps['devName'] = dev.name
                pluginProps['eventName'] = eventName
                pluginProps['description'] = description
                trig.replacePluginPropsOnServer(pluginProps)
                indigo.trigger.execute(trig)


def _pigpioError(dev, errorType, errorMessage):
    """
    Perform the following standard functions for an io device error:

    1.  Log the error on the Indigo log.
    2.  Highlight the error in the Indigo Home Window by changing the device
        error state and setting the text to red.
    3.  Execute an event trigger to invoke other actions, if any, by the
        Indigo server.
    4.  Stop the io device to disable any future use until it has been manually
        restarted or the plugin has been reloaded.
    """
    errorName = errorType.replace('int', 'interrupt') + ' error'
    L.error('"%s" %s: %s', dev.name, errorName, errorMessage)
    dev.setErrorStateOnServer('%s err' % errorType)
    _executeEventTriggers(dev, 'pigpioError', errorName.upper())
    ioDevice(dev).stop()


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                          Public Module Functions                            #
#                                                                             #
# def ioDevice(dev, new=False)                                                #
# def logStartupSummary()                                                     #
# def logShutdownSummary()                                                    #
#                                                                             #
###############################################################################

def ioDevice(dev, new=False):
    """
    Find or create a unique io device object (an instance of a PiGPIODevice
    subclass) for a PiGPIO plugin device.  Create a new object only if there is
    no existing one.  Return the object to the caller or return None if there
    is no device available.

    If an io device exists in the internal _ioDevices dictionary, always return
    it.

    If there is no existing object and new=False, assume that the object should
    be available but is missing.  Return None and do not create a new instance.
    new=False calls are used to access io device methods after PiGPIO device
    startup (e.g., ioDevice(dev).read()).

    If there is no existing object and new=True, instantiate a new io device
    object using the PiGPIO device properties.  If there are any startup
    exceptions, call _pigpioError and return None.  If startup succeeds, return
    the newly instantiated io device object.  new=True calls are used when a
    PiGPIO device may not have been started (e.g., in the deviceStartComm
    method, or __init__ methods for other io devices).
    """
    ioDev = _ioDevices.get(dev.id)  # Get existing io device, if available.
    if not ioDev:  # No io device in dictionary.

        if not new:  # The io device should exist.  Return None.
            return

        else:  # The PiGPIO device was not started.  Create a new io device.

            # Get the io device class from the io device type and the
            # IODEV_DATA dictionary.

            ioDevType = dev.pluginProps['ioDevType']
            ioDevClass = IODEV_DATA[ioDevType][0]

            # Create a new instance of the device class.

            try:
                ioDev = globals()[ioDevClass](dev)
            except ConnectionError as errorMessage:
                _pigpioError(dev, 'conn', errorMessage)
                return
            except Exception as errorMessage:
                _pigpioError(dev, 'start', errorMessage)
                return

            # Log successful io device startup for debug.  Clear errors on the
            # server and initialize the device state.

            LD.startStop('"%s" started as a %s on %s',
                         dev.name, dev.deviceTypeId, dev.address)
            dev.setErrorStateOnServer(None)  # Clear any PiGPIO device errors.
            ioDev.read(logAll=None)  # Get the device initial state.

    return ioDev  # return the io device object.


def logStartupSummary():
    """
    Log a summary of the io devices that were started by raspi host and
    interface type.
    """
    L.info('')
    L.info('io device startup summary:')
    L.info('raspi host  total  gpio  i2c   spi')
    allPi = 3 * [0]
    for piId in _ioDevCounts:
        piTot = sum(_ioDevCounts[piId])
        L.info('%10s   %3i   %3i   %3i   %3i', piId, piTot,
               *_ioDevCounts[piId])
        allPi = list(map(sum, zip(allPi, _ioDevCounts[piId], strict=True)))
    allTot = sum(allPi)
    L.info('%10s   %3i   %3i   %3i   %3i', 'totals', allTot, *allPi)
    L.info('')

def logShutdownSummary():
    """
    Log the io device and resource status at shutdown.
    """
    if _ioDevices:
        L.warning('%s io devices still active at shutdown',
                  len(_ioDevices))
    else:
        L.info('All io devices stopped')

    if _resources:
        L.warning('%s pigpiod resources still assigned/open at shutdown',
                  len(_resources))
    else:
        L.info('All pigpiod resources stopped/closed')


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                             CLASS PiGPIODevice                              #
#                                                                             #
# Internal instance methods:                                                  #
#                                                                             #
# def __init__(self, dev)                                                     #
# def _updateOnOffState(self, onOffState, sensorUiValue=None, logAll=True)    #
# def _uiValue(value, units)                                                  #
# def _updateSensorValueStates(self, voltage, logAll=True)                    #
#                                                                             #
# Abstract methods that must be included in all subclasses:                   #
#                                                                             #
# def _read(self, logAll=True)                                                #
# def _write(self, value)                                                     #
#                                                                             #
# Public instance methods that are common to all subclasses:                  #
#                                                                             #
# def read(self, logAll=True)                                                 #
# def write(self, value)                                                      #
# def poll(self)                                                              #
# def stop(self)                                                              #
# def deviceDeleted(self)                                                     #
#                                                                             #
###############################################################################

class PiGPIODevice(ABC):
    """
    PiGPIODevice is an abstract base class (ABC) that is used in defining all
    six of the Pi GPIO device subclasses.  It defines a number of internal and
    public methods that are common to all of the subclasses.  These methods
    encapsulate all of the common PiGPIODevice behavior:

    __init__                  Initializes common instance attributes and
                              assigns reusable pigpio daemon resources.
    _updateOnOffState         Updates the onOffState on the Indigo server.
    _uiValue                  Computes uiValues for sensor value processing.
    _updateSensorValueStates  Updates sensor value states on the Indigo server
                              and processes sensor values.
    read                      Calls the _read abstract method.
    write                     Calls the _write abstract method.
    poll                      Called by the runConcurrentThread method in
                              plugin.py to read io devices (poll them) at a
                              unique rate for each device.
    stop                      Stops an io device and releases its allocated
                              resources.
    deviceDeleted             Removes deleted interrupt devices from internal
                              interrupt relay lists and then calls stop.

    There are two abstract internal methods that must be overridden by each
    subclass.  These are:

    _read
    _write

    These methods encapsulate the unique behavior (typically bit manipulation
    and pigpio daemon calls) that is required for the different devices.

    All of the io device subclasses follow the following model:

    class IODevice(PiGPIODevice):

        def __init__(self, dev):
            PiGPIODevice.__init__(self, dev)  # Common initialization.
            ... unique initialization for the IODevice.

        def ...unique internal methods, if needed, to support the _read and
            _write methods.

        def _read(self)  # Implementation of abstract _read method.
            ... unique code to perform an IODevice read.

        def _write(self, value)  # Implementation of abstract _write method.
            ... unique code to perform an IODevice write.

        def ... unique public methods, if needed.  These are used to manage
            callbacks and interrupt relay.
    """

    # Internal instance methods:

    def __init__(self, dev):
        """
        Initializes common instance attributes and assigns reusable pigpio
        daemon resources.  There are four types of reusable resources:
        connection, gpio, i2c handle, and spi handle.

        There is a single connection resource for each Raspberry Pi that is
        used by the plugin.  __init__ assigns the same connection resource to
        all devices that read/write from/to hardware hosted on the connected
        pi.  Existing connections are fetched from an internal _resources
        dictionary.  If there is no existing connection, __init__ creates a
        new connection, saves it in the dictionary, and assigns it to the
        device.

        The _resources dictionary also includes a dynamic use count for each
        entry that is incremented when the resource is assigned to a device
        and decremented when it is released (see the stop method).  When the
        stop method finds that the use count is zero, it returns the resource
        to the pigpio daemon and removes it from the _resources dictionary.
        This process underlies the management of all four types of reusable
        resources (not just connections).

        The gpio, i2c handle, and spi handle resources are unique for each
        connection.  Each resource includes the connection id when saved in
        the internal _resources dictionary.  gpio resource entries are used only
        to count devices using gpio pins.  The i2c and spi resources are
        pointers (handles) to pigpiod channels with common characteristics
        (e.g., the same i2c device address).  They are used by the subclasses
        to perform device i/o using the pigpio methods.

        __init__ assigns a connection resource to the instance attribute
        self._pi for each io device.  Based on the io device type, it assigns
        one of the remaining resource types to the instance attribute
        self._handle.  The device type is assigned to the attribute
        self._interface.  These 3 instance attributes are used by the
        subclasses to perform their unique i/o operations.

        __init__ also counts the io devices by connection and interface type as
        an aid to the user in managing pigpio devices.
        """
        # Add the io device instance object to the internal _ioDevices
        # dictionary.

        _ioDevices[dev.id] = self

        # Save private reference to the Indigo device objects.

        self._dev = dev

        # Initialize common internal instance attributes:

        self._piId = None
        self._callbackId = None  # gpio callback identification object.
        ioDevType = dev.pluginProps['ioDevType']
        self._interface = IODEV_DATA[ioDevType][1]
        self._pollCount = 0  # Poll count for polling status monitoring.
        self._lastPoll = self._lastStatus = indigo.server.getTime()

        # Get the pigpio daemon connection (self._pi) from the _resources
        # dictionary.  If no connection is found, create a new one.

        hostAddress = self._dev.pluginProps['hostAddress']
        portNumber = self._dev.pluginProps['portNumber']
        hostId = self._dev.pluginProps['hostId']
        self._piId = hostId if hostId else hostAddress + ':' + portNumber

        self._pi, piCount = _resources.get(self._piId, (None, 0))
        if self._pi is None:  # No existing connection; initialize a new one.
            self._pi = pigpio.pi(hostAddress, portNumber)
            if not self._pi.connected:  # Connection failed.
                self._pi = None
                errorMessage = 'pigpio connection failed'
                raise ConnectionError(errorMessage)
            LD.resource('New pigpio connection %s', self._piId)
            _ioDevCounts[self._piId] = 3*[0]
        piCount += 1
        _resources[self._piId] = self._pi, piCount

        # Get a gpio, i2c, or spi handle (self._handle) from the resource
        # dictionary.  If no handle is found, open a new one.

        if self._interface is GPIO:
            self._hId = self._piId + '|gpio'
            self._handle, hCount = _resources.get(self._hId, (None, 0))
            self._handle = ''

        elif self._interface is I2C:  # Get an i2c handle.
            i2cAddress = self._dev.pluginProps['i2cAddress']
            self._hId = self._piId + '|' + i2cAddress
            self._handle, hCount = _resources.get(self._hId, (None, 0))
            if self._handle is None:  # No existing i2c handle; open a new one.
                self._handle = self._pi.i2c_open(I2CBUS, int(i2cAddress,
                                                             base=16))
                LD.resource('New handle opened %s i2c-%s',
                            self._piId, self._handle)

        else:  # self._interface is SPI; get an spi handle.
            spiChannel = self._dev.pluginProps['spiChannel']
            bitRate = int(500000 * float(self._dev.pluginProps['bitRate']))
            self._hId = self._piId + '|' + spiChannel + '|' + str(bitRate)
            self._handle, hCount = _resources.get(self._hId, (None, 0))
            if self._handle is None:  # No existing spi handle; open a new one.
                self._handle = self._pi.spi_open(int(spiChannel), bitRate,
                                                 SPIBUS << 8)
                LD.resource('New handle opened %s spi-%s', self._piId,
                            self._handle)

        # Update the _resources dictionary.

        hCount += 1
        _resources[self._hId] = self._handle, hCount
        LD.resource('"%s" assigned shared pigpiod resources %s (%s) %s%s (%s)',
                    self._dev.name, self._piId, piCount, IF[self._interface],
                    self._handle, hCount)
        _ioDevCounts[self._piId][self._interface] += 1

        # Set the initial device state image to override power icon defaults
        # for digital output devices.

        onOffState = dev.states['onOffState']
        dev.updateStateImageOnServer(IMAGE_SEL[onOffState])

    def _updateOnOffState(self, onOffState, sensorUiValue=None, logAll=True):
        """
        Update the onOffState for an analog or digital device on the Indigo
        server along with a user selected uiValue.  Log the onOffState if it
        has changed and logAll is not None.  If there is no change, log the
        unchanged state if logAll is True.
        """
        priorOnOffState = self._dev.states['onOffState']  # Save prior state.

        # Compute the uiValue based on the displayStateId and update the state
        # on the server.

        onOffUiValue = ON_OFF[onOffState]
        displayStateId = self._dev.pluginProps.get('displayStateId')
        uiValue = (sensorUiValue if displayStateId == 'sensorValue'
                   else onOffUiValue)
        self._dev.updateStateOnServer(key='onOffState', value=onOffState,
                                      uiValue=uiValue, clearErrorState=False)
        self._dev.updateStateImageOnServer(IMAGE_SEL[onOffState])

        # Log the onOffState if a change is detected and logAll is not None.
        # If there is no change, log it if logAll is True.

        onOffText = onOffUiValue
        onOffText += (' <' + sensorUiValue + '>' if sensorUiValue else '')
        if onOffState != priorOnOffState and logAll is not None:
            L.info('"%s" update onOffState to %s', self._dev.name, onOffText)
        elif logAll:
            L.info('"%s" onOffState is %s', self._dev.name, onOffText)

    @staticmethod
    def _uiValue(value, units):
        """
        Generate a formatted text uiValue, consisting of a floating point
        value and units, for use in the state display and limit fault messages.
        """
        magnitude = abs(value)
        if magnitude < 10:
            uiFormat = '%.2f %s'  # uiValue format for small value.
        elif magnitude < 100:
            uiFormat = '%.1f %s'  # uiValue format for medium value.
        else:
            uiFormat = '%i %s'    # uiValue format for large value.
        return uiFormat % (value, units)

    def _updateSensorValueStates(self, voltage, logAll=True):
        """
        Compute the sensor value from the ADC or DAC voltage.  Compute the
        uiValue and update the sensorValue state on the server.  Optionally
        perform sensor value percentage change detection, analog onOffState
        thresholding, and limit checking.  Update states, log results, and
        execute event triggers based on processing results.
        """
        priorSensorValue = self._dev.states['sensorValue']  # Save prior value.

        # Compute the new sensorValue and uiValue from the ADC / DAC voltage
        # and update the states on the server.

        scalingFactor = float(self._dev.pluginProps['scalingFactor'])
        sensorValue = voltage * scalingFactor
        units = self._dev.pluginProps['units']
        sensorUiValue = self._uiValue(sensorValue, units)
        self._dev.updateStateOnServer(key='sensorValue', value=sensorValue,
                            uiValue=sensorUiValue, clearErrorState=False)

        # Compute the sensorValue percentage change and the changeDetected
        # state value.  Update the changeDetected state on the server.

        percentChange = (100.0 * abs((sensorValue - priorSensorValue)
            / priorSensorValue if priorSensorValue else 0.001))
        changeThreshold = self._dev.pluginProps['changeThreshold']
        changeDetected = (False if changeThreshold == 'None'
                          else percentChange > float(changeThreshold))
        self._dev.updateStateOnServer(key='changeDetected',
                                      value=changeDetected)

        # Log the sensorValue if a change is detected and logAll is not None.
        # If there is no change, log it if logAll is True.

        if changeDetected and logAll is not None:
            L.info('"%s" update sensorValue to %.4f %s',
                   self._dev.name, sensorValue, units)
        elif logAll:
            L.info('"%s" sensorValue is %.4f %s',
                   self._dev.name, sensorValue, units)

        # Determine the onOffState based on analog thresholding.  Update and
        # log the onOffState.

        onThreshold = self._dev.pluginProps['onThreshold']
        onOffState = (OFF if onThreshold == 'None'
                      else sensorValue > float(onThreshold))
        self._updateOnOffState(onOffState, sensorUiValue=sensorUiValue,
                               logAll=logAll)

        # Perform limit checking and determine the limitFault states.

        lowLimit = self._dev.pluginProps['lowLimit']  # Check low limit.
        lowLimitFault = (False if lowLimit == 'None' else
                    sensorValue < float(lowLimit))

        highLimit = self._dev.pluginProps['highLimit']  # Check high limit.
        highLimitFault = (False if highLimit == 'None' else
                    sensorValue > float(highLimit))

        # Save the prior limit fault state and update the current state.

        priorLimitFault = self._dev.states['limitFault']
        limitFault = lowLimitFault or highLimitFault
        self._dev.updateStateOnServer(key='limitFault', value=limitFault)

        if limitFault:  # Process limit fault.

            # Set the display image and log a limit fault message.

            self._dev.updateStateImageOnServer(
                indigo.kStateImageSel.SensorTripped)

            if lowLimitFault:
                triggerEvent = 'low limit fault'
                uiLimit = self._uiValue(float(lowLimit), units)
                description = '%s < %s' % (sensorUiValue, uiLimit)
                L.warning('"%s" low limit fault: %s < %s',
                          self._dev.name, sensorUiValue, uiLimit)
            else:  # highLimitFault
                triggerEvent = 'high limit fault'
                uiLimit = self._uiValue(float(highLimit), units)
                description = '%s > %s' % (sensorUiValue, uiLimit)
            L.warning('"%s" %s: %s', self._dev.name, triggerEvent, description)

            # Execute a limit fault trigger only if it is a new limit fault.

            if not priorLimitFault:
                _executeEventTriggers(self._dev, 'limitFault', triggerEvent)

    # Abstract methods that must be included in all subclasses:

    @abstractmethod
    def _read(self, logAll=True):
        pass

    @abstractmethod
    def _write(self, value):
        pass

    # Public instance methods that are common to all subclasses:

    def read(self, logAll=True):
        """
        Read from the io device using the subclassed _read method.  Direct any
        exceptions to the module-level standard error handling method.
        """
        try:
            self._read(logAll=logAll)
        except Exception as errorMessage:
            _pigpioError(self._dev, 'read', errorMessage)

    def write(self, value):
        """
        Write to the io device using the subclassed _write method.  Direct any
        exceptions to the module-level standard error handling method.
        """
        try:
            self._write(value)
        except Exception as errorMessage:
            _pigpioError(self._dev, 'write', errorMessage)

    def poll(self):
        """
        
        """
        if self._dev.pluginProps['polling']:
            now = indigo.server.getTime()
            secsSinceLast = (now - self._lastPoll).total_seconds()
            pollingInterval = float(self._dev.pluginProps['pollingInterval'])
            if secsSinceLast >= pollingInterval:
                logAll = self._dev.pluginProps['logAll']
                self.read(logAll=logAll)
                self._pollCount += 1
                self._lastPoll = now
                if self._dev.pluginProps['monitorStatus']:
                    secsSinceLast = (now - self._lastStatus).total_seconds()
                    statusInterval = float(self._dev.pluginProps
                                           ['statusInterval'])
                    if secsSinceLast >= 60 * statusInterval:
                        averageInterval = secsSinceLast / self._pollCount
                        averageRate = 1 / averageInterval
                        L.info('"%s" average polling interval is %4.2f '
                               'secs, rate is %4.2f per sec',
                               self._dev.name, averageInterval, averageRate)
                        self._pollCount = 0
                        self._lastStatus = now

    def stop(self):
        """
        Stop the pigpio device by removing it from the io devices dictionary.
        Decrement the use count for the device's shared resources. Return
        any shared resources to the pigpio daemon if the use count becomes
        zero.  This completes the pigpiod reusable resource management scheme
        discussed in the __init__ method pydocs.
        """
        try:
            # Remove the io device from the io devices dictionary.

            del _ioDevices[self._dev.id]

            # Cancel the gpio callback, if any.

            if self._callbackId:
                self._callbackId.cancel()

            self._pi, piCount = _resources.get(self._piId, (None, 0))
            if self._pi:

                # Release pigpiod shared resources by decrementing the shared
                # use count.  Close/stop the resource if the use count becomes
                # zero.

                piCount -= 1
                _resources[self._piId] = self._pi, piCount

                self._handle, hCount = _resources.get(self._hId, (None, 0))
                if self._handle is not None:  # Include GPIO devices.

                    hCount -= 1
                    _resources[self._hId] = self._handle, hCount

                    LD.resource('"%s" released shared pigpiod resources '
                                '%s (%s) %s%s (%s)', self._dev.name,
                                self._piId, piCount, IF[self._interface],
                                self._handle, hCount)
                    _ioDevCounts[self._piId][self._interface] -= 1

                    if not hCount:

                        # No more users for this handle.  Close the handle and
                        # delete the resource.

                        if self._interface is I2C:
                            self._pi.i2c_close(self._handle)
                            LD.resource('Handle closed %s i2c-%s',
                                        self._piId, self._handle)
                        elif self._interface is SPI:
                            self._pi.spi_close(self._handle)
                            LD.resource('Handle closed %s spi-%s',
                                        self._piId, self._handle)
                        del _resources[self._hId]
                        self._handle = None

                if not piCount:

                    # No more users for this pigpiod connection.  Stop the
                    # connection and delete the resource.

                    self._pi.stop()
                    LD.resource('pigpiod connection stopped %s', self._piId)
                    del _resources[self._piId]
                    self._pi = None

        except Exception as errorMessage:

            # Stop exceptions often follow another Pi GPIO exception/error
            # because the device is stopped and the error frequently interferes
            # with the release of pigpiod resources.  Log a warning message,
            # but do not call_pigpioError and trigger another event.

            L.warning('"%s" stop error: %s', self._dev.name, errorMessage)

        # Log successful stop completion for debugging.

        LD.startStop('"%s" stopped', self._dev.name)

    def deviceDeleted(self):
        """
        Check to see if the deleted io device was an interrupt device that
        relayed it's hardware interrupt through a gpio callback.  If so, remove
        it's device id from the from the interrupt devices list in the
        interrupt relay gpio device.
        """
        relayGPIO = self._dev.pluginProps.get('interruptRelayGPIO')
        if relayGPIO:
            LD.digital('"%s" device deleted; removing device id from "%s"',
                       self._dev.name, relayGPIO)
            relayDev = indigo.devices[relayGPIO]
            ioDev = _ioDevices[relayDev.id]
            ioDev.removeInterruptDevice(self._dev.id)


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                                CLASS ADC12                                  #
#                                                                             #
# Internal instance methods:                                                  #
#                                                                             #
# def __init__(self, dev)                                                     #
# def _readSpiOutputCode(self)                                                #
#                                                                             #
# Implementation of abstract methods:                                         #
#                                                                             #
# def _read(self, logAll=True)                                                #
# def _write(self, value)                                                     #
#                                                                             #
###############################################################################

class ADC12(PiGPIODevice):

    # Internal instance methods:

    def __init__(self, dev):
        PiGPIODevice.__init__(self, dev)  # Common initialization.

        # Assemble data tuple for ADC12 devices.

        inputConfiguration = int(dev.pluginProps['inputConfiguration'])
        adcChannel = int(self._dev.pluginProps['adcChannel'])
        self._data = (0x04 | inputConfiguration << 1 | adcChannel >> 2,
                      (adcChannel << 6) & 0xff, 0)
        ioDevType = self._dev.pluginProps['ioDevType']
        if ioDevType == 'MCP3202':
            self._data = (0x01, inputConfiguration << 7 | adcChannel << 6, 0)

    def _readSpiOutputCode(self):
        nBytes, bytes_ = self._pi.spi_xfer(self._handle, self._data)
        counts = (bytes_[1] & 0x0f) << 8 | bytes_[2]
        LD.analog('"%s" read %s | %s | %s | %s', self._dev.name,
                  _hexStr(self._data), nBytes, _hexStr(bytes_), counts)
        return counts

    # Implementation of abstract methods:

    def _read(self, logAll=True):
        counts = self._readSpiOutputCode()
        if self._dev.pluginProps['checkSPI']:  # Check SPI integrity.
            counts_ = self._readSpiOutputCode()
            if abs(counts - counts_) > 10:
                L.warning('"%s" spi check: different values on consecutive '
                          'reads %s %s', self._dev.name, counts, counts_)
            counts = counts_

        referenceVoltage = float(self._dev.pluginProps['referenceVoltage'])
        voltage = referenceVoltage * counts / 4096
        self._updateSensorValueStates(voltage, logAll=logAll)

    def _write(self, value):
        pass


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                                CLASS ADC18                                  #
#                                                                             #
# Internal instance methods:                                                  #
#                                                                             #
# def __init__(self, dev)                                                     #
# def _readSpiOutputCode(self)                                                #
#                                                                             #
# Implementation of abstract methods:                                         #
#                                                                             #
# def _read(self, logAll=True)                                                #
# def _write(self, value)                                                     #
#                                                                             #
###############################################################################

class ADC18(PiGPIODevice):

    # Internal instance method:

    def __init__(self, dev):
        PiGPIODevice.__init__(self, dev)  # Common initialization.

        # Assemble ADC configuration byte.

        notReady = 0x80  # Not-ready bit.
        adcChannel = int(dev.pluginProps['adcChannel'])
        conversionMode = 0  # One-shot conversion mode.
        resolution = int(dev.pluginProps['resolution'])
        resolutionIndex = (resolution - 12) >> 1
        gain = dev.pluginProps['gain']
        gainIndex = '1248'.find(gain)
        self._config = (notReady | adcChannel << 5 | conversionMode << 4
                        | resolutionIndex << 2 | gainIndex)

    # Implementation of abstract methods:

    def _read(self, logAll=True):

        # Start the conversion in the single shot mode.

        self._pi.i2c_write_byte(self._handle, self._config)

        # Read the conversion register until the not-ready bit is cleared in
        # the returned config byte (last byte received).  This indicates that
        # the output register has been updated (ready == ~ notReady).

        notReady = 0x80  # Not-ready bit.
        config = self._config & (~ notReady)  # Clear the not-ready bit.
        resolution = int(self._dev.pluginProps['resolution'])
        numToRead = 3 if resolution < 18 else 4  # Num of bytes to read.

        numReads = 0
        while True:
            numBytes, bytes_ = self._pi.i2c_read_i2c_block_data(self._handle,
                                    config, numToRead)
            numReads += 1
            if not (bytes_[-1] & notReady):  # Stop if ready.
                break

        # Pack bytes from the returned bytearray into a single integer output
        # code.

        counts = -1 if bytes_[0] & 0x80 else 0
        for byte in bytes_[:-1]:
            counts = counts << 8 | byte

        # Compute the voltage and update the sensor value state.

        referenceVoltage = 2.048  # Internal reference voltage (volts).
        maxCode = 1 << (resolution - 1)  # maxCode = (2 ** (resolution - 1)).
        gain = int(self._dev.pluginProps['gain'])
        voltage = (referenceVoltage * counts / (maxCode * gain))
        LD.analog('"%s" read %s | %s | %s | %s', self._dev.name, numReads,
                  _hexStr(bytes_), counts, voltage)
        self._updateSensorValueStates(voltage, logAll=logAll)

    def _write(self, value):
        pass


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                                CLASS DAC12                                  #
#                                                                             #
# Internal instance method:                                                   #
#                                                                             #
# def __init__(self, dev)                                                     #
#                                                                             #
# Implementation of abstract methods:                                         #
#                                                                             #
# def _read(self, logAll=True)                                                #
# def _write(self, value)                                                     #
#                                                                             #
###############################################################################

class DAC12(PiGPIODevice):

    # Internal instance method:

    def __init__(self, dev):
        PiGPIODevice.__init__(self, dev)  # Common initialization.

    # Implementation of abstract methods:

    def _read(self, logAll=True):
        sensorValue = self._dev.states['sensorValue']
        scalingFactor = float(self._dev.pluginProps['scalingFactor'])
        voltage = sensorValue / scalingFactor
        self._updateSensorValueStates(voltage, logAll=logAll)

    def _write(self, value):

        # Check the argument.

        try:
            sensorValue = float(value)
        except ValueError:
            L.warning('"%s" invalid output value %s; write ignored',
                      self._dev.name, value)
            return

        # Convert the sensorValue to a DAC input code and write to the DAC.

        scalingFactor = float(self._dev.pluginProps['scalingFactor'])
        voltage = sensorValue / scalingFactor
        referenceVoltage = 2.048  # Internal reference voltage (volts).
        gain = int(self._dev.pluginProps['gain'])
        inputCode = int(voltage * 4096 / (referenceVoltage * gain))

        if 0 <= inputCode < 4096:
            dacChannel = int(self._dev.pluginProps['dacChannel'])
            data = (dacChannel << 7 | (gain & 1) << 5 | 0x10 | inputCode >> 8,
                    inputCode & 0xff)
            nBytes = self._pi.spi_write(self._handle, data)
            LD.analog('"%s" xfer %s | %s | %s | %s', self._dev.name, voltage,
                      inputCode, _hexStr(data), nBytes)
        else:
            L.warning('"%s" converted input code %s is outside of DAC '
                      'range; write ignored', self._dev.name, inputCode)
            return

        # Update and log the sensorValue states.

        self._updateSensorValueStates(voltage)


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                            CLASS DockerPiRelay                              #
#                                                                             #
# Internal instance method:                                                   #
#                                                                             #
# def __init__(self, dev)                                                     #
#                                                                             #
# Implementation of abstract methods:                                         #
#                                                                             #
# def _read(self, logAll=True)                                                #
# def _write(self, value)                                                     #
#                                                                             #
###############################################################################

class DockerPiRelay(PiGPIODevice):

    # Internal instance method:

    def __init__(self, dev):
        PiGPIODevice.__init__(self, dev)  # Common initialization.

    # Implementation of abstract methods:

    def _read(self, logAll=True):
        onOffState = self._dev.states['onOffState']
        self._updateOnOffState(onOffState, logAll=logAll)

    def _write(self, value):
        bit = 99
        try:
            bit = int(value)
        except ValueError:
            pass
        if bit in BIT:
            relayNumber = int(self._dev.pluginProps['relayNumber'])
            self._pi.i2c_write_byte_data(self._handle, relayNumber, bit)
            LD.digital('"%s" write %s', self._dev.name, ON_OFF[bit])
            self._updateOnOffState(bit)
            if bit:
                if self._dev.pluginProps['momentary']:
                    sleep(float(self._dev.pluginProps['turnOffDelay']))
                    self._write(OFF)
        else:
            L.warning('"%s" invalid output value %s; write ignored',
                      self._dev.name, value)


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                              CLASS IOExpander                               #
#                                                                             #
# Internal instance methods:                                                  #
#                                                                             #
# def __init__(self, dev)                                                     #
# def _readSpiByte(self, register, data)                                      #
# def _readRegister(self, register)                                           #
# def _writeRegister(self, register, byte)                                    #
# def _updateRegister(self, register, bit)                                    #
#                                                                             #
# Implementation of abstract methods:                                         #
#                                                                             #
# def _read(self, logAll=True)                                                #
# def _write(self, value)                                                     #
#                                                                             #
# Public instance methods:                                                    #
#                                                                             #
# def interrupt(self):                                                        #
# def resetInterrupt(self)                                                    #
#                                                                             #
###############################################################################

class IOExpander(PiGPIODevice):
    """
    """

    # MCP23XXX register address constants:

    REG_BASE_ADDR = {'IODIR':   0x00,  # I/O Direction Register.
                     'IPOL':    0x01,  # Input Polarity Register.
                     'GPINTEN': 0x02,  # Interrupt-on-change Control Register.
                     'DEFVAL':  0x03,  # Default Value Register.
                     'INTCON':  0x04,  # Interrupt-on-Change Control Register.
                     'IOCON':   0x05,  # I/O Configuration Register.
                     'GPPU':    0x06,  # Pullup Resistor Config Register.
                     'INTF':    0x07,  # Interrupt Flag Register.
                     'INTCAP':  0x08,  # Interrupt Capture Register.
                     'GPIO':    0x09,  # Port Register.
                     'OLAT':    0x0a,  # Output Latch Register.
                     'IOCONB0': 0x0b}  # IOCON register for port B in the
    #                                    BANK 0 mapping.

    # The above addresses (except the last one) are for the MCP23X08 and the
    # MCP23X17 Port A in the BANK 1 register address mapping.  Port B addresses
    # add 0x10 to the corresponding Port A addresses.

    # IOCON register bit constants:

    BANK = 0x80    # Split A and B port registers are into two separate address
    #                banks (BANK 1 mapping).  This mapping maintains
    #                compatibility between the MCP23X08 and MCP23X17 addresses
    #                (see REG_BASE_ADDR).
    SEQOP = 0x20   # Disable sequential register I/O operations.  Read/write a
    #                single register at a time.
    HAEN = 0x08    # Enables address pins on the MCP23S08 (2 bits) and the
    #                MCP23S217 (3 bits).
    INTPOL = 0x02  # Set the interrupt polarity to active high.

    # IODIR bit constants:

    INPUT = 0x01
    OUTPUT = 0x00

    # Control byte constants:

    READ = 0x01
    WRITE = 0x00

    # Internal instance methods:

    def __init__(self, dev):
        PiGPIODevice.__init__(self, dev)  # Common initialization.

        # Define internal attributes.

        ioPort = dev.pluginProps['ioPort']
        self._offset = 0x10 if ioPort == 'b' else 0x00
        bitNumber = int(dev.pluginProps['bitNumber'])
        self._mask = 1 << bitNumber

        # Configure the IOCON register with a common set of bits (BANK,
        # SEQOP, and HAEN) that apply to all io device objects that use the
        # same hardware chip.  Note that the IOCON register is written
        # multiple times (once for each io device object), but it doesn't
        # matter because the same value is written each time.

        # The IOCON configuration is complicated by the fact that the
        # internal register address mapping (BANK 0 or 1) is not known.
        # The following sequence of 2 writes addresses this problem.  It
        # works for all MCP23XXX devices regardless of the initial
        # configuration.  For details please see the appropriate MCP23XXX
        # data sheets. These may be downloaded from:

        # https://www.microchip.com/en-us/product/MCP230008
        # https://www.microchip.com/en-us/product/MCP230017

        iocon = self.BANK | self.SEQOP | self.HAEN | self.INTPOL

        self._writeRegister('IOCONB0', iocon)
        self._writeRegister('IOCON', iocon)

        # Configure the IODIR, IPOL, GPPU, DEFVAL, INTCON, and GPINTEN
        # registers by setting the specific bit for this device
        # (self._bitNum) in each register.  Leave all other bits unchanged.
        # These configuration changes use the self._updateRegister method
        # to read the register, change the appropriate bit, and then write
        # it back.

        # Common register settings for input and output devices:

        self._updateRegister('DEFVAL', OFF)  # Clear default bit.
        self._updateRegister('INTCON', OFF)  # Interrupt on change.

        if dev.deviceTypeId == 'digitalOutput':

            # Unique register settings for output devices:

            self._updateRegister('IODIR', self.OUTPUT)
            self._updateRegister('GPINTEN', OFF)  # No interrupt for output.

        else:  # dev.deviceTypeId == 'digitalInput'

            # Unique register settings for input devices:

            self._updateRegister('IODIR', self.INPUT)
            invert = self._dev.pluginProps['invert']
            self._updateRegister('IPOL', invert)  # Set input polarity.
            pullup = dev.pluginProps['pullup']
            self._updateRegister('GPPU', pullup == 'up')  # Set pullup option.
            hardwareInterrupt = dev.pluginProps['hardwareInterrupt']
            self._updateRegister('GPINTEN', hardwareInterrupt)

            # Hardware interrupt relay setup for input devices.

            priorRelayGPIO = dev.pluginProps['priorInterruptRelayGPIO']
            relayGPIO = dev.pluginProps['interruptRelayGPIO']

            if priorRelayGPIO and priorRelayGPIO != relayGPIO:

                # If relay device changed, remove this device (the interrupt
                # device) from the interrupt devices list in the prior relay
                # device.

                relayDev = indigo.devices[priorRelayGPIO]
                ioDevice(relayDev).removeInterruptDevice(dev.id)

            if relayGPIO:

                # Add this device to the interrupt devices list in the current
                # relay device or remove it, depending on the hardware
                # interrupt state.

                relayDev = indigo.devices[relayGPIO]
                if hardwareInterrupt:  # Interrupt is enabled; add device.
                    ioDevice(relayDev, new=True).addInterruptDevice(dev.id)
                else:  # Interrupt is disabled; remove device.
                    ioDevice(relayDev).removeInterruptDevice(dev.id)

    def _readSpiByte(self, register, data):
        nBytes, bytes_ = self._pi.spi_xfer(self._handle, data)
        LD.digital('"%s" readRegister %s %s | %s | %s', self._dev.name,
                   register, _hexStr(data), nBytes, _hexStr(bytes_))
        return bytes_[-1]

    def _readRegister(self, register):
        registerAddress = self.REG_BASE_ADDR[register] + self._offset

        if self._interface is I2C:  # MCP230XX
            byte = self._pi.i2c_read_byte_data(self._handle, registerAddress)
            LD.digital('"%s" readRegister %s %02x',
                       self._dev.name, register, byte)
            return byte

        elif self._interface is SPI:  # MCP23SXX
            spiDevAddress = int(self._dev.pluginProps['spiDevAddress'], 16)
            data = (spiDevAddress << 1 | self.READ, registerAddress, 0)
            byte = self._readSpiByte(register, data)

            if self._dev.pluginProps['checkSPI']:  # Check SPI integrity.
                byte_ = self._readSpiByte(register, data)
                if byte != byte_:
                    L.warning('"%s" readRegister %s spi check: unequal '
                              'consecutive reads %02x %02x',
                              self._dev.name, register, byte, byte_)
                    byte = byte_

            return byte

    def _writeRegister(self, register, byte):
        registerAddress = self.REG_BASE_ADDR[register] + self._offset

        if self._interface is I2C:  # MCP230XX
            self._pi.i2c_write_byte_data(self._handle, registerAddress, byte)
            LD.digital('"%s" writeRegister %s %02x',
                       self._dev.name, register, byte)

        elif self._interface is SPI:  # MCP23SXX
            spiDevAddress = int(self._dev.pluginProps['spiDevAddress'], 16)
            data = (spiDevAddress << 1 | self.WRITE, registerAddress, byte)
            nBytes = self._pi.spi_write(self._handle, data)
            LD.digital('"%s" writeRegister %s %s | %s',
                       self._dev.name, register, _hexStr(data), nBytes)

    def _updateRegister(self, register, bit):
        byte = self._readRegister(register)
        updatedByte = byte | self._mask if bit else byte & ~self._mask
        if updatedByte != byte:
            LD.digital('"%s" updateRegister %s %02x | %s | %02x',
                       self._dev.name, register, byte, bit, updatedByte)
            self._writeRegister(register, updatedByte)

    # Implementation of abstract methods:

    def _read(self, logAll=True):
        byte = self._readRegister('GPIO')
        bit = 1 if byte & self._mask else 0
        self._updateOnOffState(bit, logAll=logAll)
        return bit

    def _write(self, value):
        bit = 99
        try:
            bit = int(value)
        except ValueError:
            pass
        if bit in BIT:
            self._updateRegister('GPIO', bit)
            self._updateOnOffState(bit)
            if bit:
                if self._dev.pluginProps['momentary']:
                    sleep(float(self._dev.pluginProps['turnOffDelay']))
                    self._write(OFF)
        else:
            L.warning('"%s" invalid output value %s; write ignored',
                      self._dev.name, value)

    # Public instance methods:

    def interrupt(self):
        """
        Read the interrupt flag register and check for an interrupt on this
        device.  If the flag bit that matches the device bit is on, read the
        interrupt capture register and update the device onOffState.  Check the
        interrupt flag register for any simultaneous interrupts that may have
        been lost.  Return True to indicate a successful interrupt.  If the
        interrupt bit for this device is off, return False to indicate that
        an interrupt did not occur on this device.
        """
        try:
            intf = self._readRegister('INTF')
            if intf & self._mask:

                # Interrupt flag bit matches device bit; read interrupt capture
                # register and update the onOffState.

                intcap = self._readRegister('INTCAP')
                bit = 1 if intcap & self._mask else 0
                LD.digital('"%s" interrupt %02x | %02x | %s',
                           self._dev.name, intf, intcap, ON_OFF[bit])
                self._updateOnOffState(bit)

                # Check for lost interrupts.

                lostInterrupts = intf ^ self._mask
                if lostInterrupts:  # Any other bits set in interrupt flag reg?
                    L.warning('"%s" lost interrupts %02x',
                              self._dev.name, lostInterrupts)
                return True  # Signal a successful interrupt.

        except Exception as errorMessage:
            _pigpioError(self._dev, 'int', errorMessage)

    def resetInterrupt(self):
        try:
            self._readRegister('GPIO')  # Read port register to clear interrupt
        except Exception as errorMessage:
            _pigpioError(self._dev, 'int', errorMessage)

###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                                CLASS PiGPIO                                 #
#                                                                             #
# Internal instance methods:                                                  #
#                                                                             #
# def __init__(self, dev)                                                     #
# def _callback(self, gpioNumber, pinBit, tic)                                #
#                                                                             #
# Implementation of abstract methods:                                         #
#                                                                             #
# def _read(self, logAll=True)                                                #
# def _write(self, value)                                                     #
#                                                                             #
# Public instance methods:                                                    #
#                                                                             #
# def addInterruptDevice(self, intDevId)                                      #
# def removeInterruptDevice(self, intDevId)                                   #
#                                                                             #
###############################################################################

class PiGPIO(PiGPIODevice):
    """
    Include discussion of callback, interrupt relay, and debouncing.
    """
    # Class constant:

    PUD = {'off': pigpio.PUD_OFF,  # GPIO pullup parameter definitions.
           'up': pigpio.PUD_UP,
           'down': pigpio.PUD_DOWN}

    # Internal instance methods:

    def __init__(self, dev):
        PiGPIODevice.__init__(self, dev)  # Common initialization.

        # Set internal instance attributes and configure the gpio device.

        self._gpioNumber = int(dev.pluginProps['gpioNumber'])

        if dev.deviceTypeId == 'digitalInput':
            self._pi.set_mode(self._gpioNumber, pigpio.INPUT)
            pullup = dev.pluginProps['pullup']
            self._pi.set_pull_up_down(self._gpioNumber, self.PUD[pullup])
            if dev.pluginProps['callback']:
                self._callbackId = self._pi.callback(self._gpioNumber,
                                        pigpio.EITHER_EDGE, self._callback)
                self._priorTic = self._pi.get_current_tick()
                if dev.pluginProps['glitchFilter']:
                    glitchTime = int(dev.pluginProps['glitchTime'])
                    self._pi.set_glitch_filter(self._gpioNumber, glitchTime)

        elif dev.deviceTypeId == 'digitalOutput':
            self._pi.set_mode(self._gpioNumber, pigpio.OUTPUT)
            if dev.pluginProps['pwm']:
                self._pi.set_PWM_range(self._gpioNumber, 100)
                frequency = int(dev.pluginProps['frequency'])
                self._pi.set_PWM_frequency(self._gpioNumber, frequency)

    def _callback(self, gpioNumber, pinBit, tic):
        try:
            dt = pigpio.tickDiff(self._priorTic, tic)
            self._priorTic = tic
            LD.digital('"%s" callback %s %s %s %s',
                       self._dev.name, gpioNumber, pinBit, tic, dt)
            logAll = True  # Default logging option for state update.
            interruptDevices = self._dev.pluginProps.get('interruptDevices')
            if pinBit in BIT:
                bit = pinBit ^ self._dev.pluginProps['invert']

                # Apply the contact bounce filter, if requested.

                if self._dev.pluginProps['bounceFilter']:
                    if dt < self._dev.pluginProps['bounceTime']:  # Bouncing.
                        if self._dev.pluginProps['logBounce']:
                            L.warning('"%s" %s µs bounce; update to %s '
                                'ignored', self._dev.name, dt, ON_OFF[bit])
                        return  # Ignore the bounced state change.

                # Relay interrupts, if requested.

                if (self._dev.pluginProps['relayInterrupts']
                        and interruptDevices):
                    if bit:  # Interrupt initiated; process it and set watchdog
                        for intDevId in interruptDevices:
                            if _ioDevices[intDevId].interrupt():  # Int device.
                                break  # Only one match allowed per interrupt.
                        else:
                            L.warning('"%s" no match in interrupt devices '
                                      'list', self._dev.name)
                            self._pi.set_watchdog(self._gpioNumber, 200)
                    else:  # Interrupt reset; log time and clear the watchdog.
                        LD.digital('"%s" interrupt time is %s ms',
                                   self._dev.name, dt / 1000)
                        self._pi.set_watchdog(self._gpioNumber, 0)
                    logAll = None  # Suppress logging for interrupt relay GPIO.

                # Update the onOff state.

                self._updateOnOffState(bit, logAll=logAll)

            else:  # Interrupt reset timeout.
                L.warning('"%s" interrupt reset timeout', self._dev.name)
                if (self._dev.pluginProps['relayInterrupts']
                        and interruptDevices):
                    for intDevId in interruptDevices:
                        _ioDevices[intDevId].resetInterrupt()
                    self._pi.set_watchdog(self._gpioNumber, 0)  # Clear wdog.

        except Exception as errorMessage:
            _pigpioError(self._dev, 'int', errorMessage)

    # Implementation of abstract methods:

    def _read(self, logAll=True):
        invert = self._dev.pluginProps.get('invert', False)
        bit = self._pi.read(self._gpioNumber) ^ invert
        LD.digital('"%s" read %s', self._dev.name, ON_OFF[bit])
        self._updateOnOffState(bit, logAll=logAll)
        return bit

    def _write(self, value):
        bit = 99
        try:
            bit = int(value)
        except ValueError:
            pass
        if bit in BIT:
            self._pi.write(self._gpioNumber, bit)
            LD.digital('"%s" write %s', self._dev.name, ON_OFF[bit])
            self._updateOnOffState(bit)
            if bit:
                if self._dev.pluginProps['pwm']:
                    dutyCycle = int(self._dev.pluginProps['dutyCycle'])
                    self._pi.set_PWM_dutycycle(self._gpioNumber, dutyCycle)
                if self._dev.pluginProps['momentary']:
                    sleep(float(self._dev.pluginProps['turnOffDelay']))
                    self._write(OFF)
        else:
            L.warning('"%s" invalid output value %s; write ignored',
                      self._dev.name, value)

    # Public instance methods:

    def addInterruptDevice(self, intDevId):
        """
        Add a new interrupt device id to the interrupt devices list in the
        current device's pluginProps.  If the interrupt device is already in
        the list, do nothing.  If there is no interrupt devices list, create a
        new empty indigo.List and add it to pluginProps before appending the
        new interrupt device.  If the interrupt devices list is changed (or
        added), replace the pluginProps on the Indigo server.
        """
        pluginProps = self._dev.pluginProps
        if 'interruptDevices' not in pluginProps:
            pluginProps['interruptDevices'] = indigo.List()
        interruptDevices = pluginProps['interruptDevices']
        if intDevId not in interruptDevices:
            interruptDevices.append(intDevId)
            pluginProps['interruptDevices'] = interruptDevices
            self._dev.replacePluginPropsOnServer(pluginProps)
            LD.digital('"%s" added %s to interrupt devices list',
                       self._dev.name, intDevId)
            LD.digital('"%s" %s', self._dev.name, interruptDevices)

    def removeInterruptDevice(self, intDevId):
        """
        Remove an unused interrupt device id from the interrupt devices list in
        the current device's pluginProps.  If the interrupt device is not in
        the list, do nothing.  If the interrupt devices list is changed,
        replace the pluginProps on the Indigo server.
        """
        pluginProps = self._dev.pluginProps
        interruptDevices = pluginProps.get('interruptDevices')
        if interruptDevices and intDevId in interruptDevices:
            interruptDevices.remove(intDevId)
            pluginProps['interruptDevices'] = interruptDevices
            self._dev.replacePluginPropsOnServer(pluginProps)
            LD.digital('"%s" removed %s from interrupt devices list',
                       self._dev.name, intDevId)
            LD.digital('"%s" %s', self._dev.name, interruptDevices)
