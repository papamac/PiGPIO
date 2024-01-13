# coding=utf-8
"""
###############################################################################
#                                                                             #
#                            Pi GPIO Indigo Plugin                            #
#                           MODULE pigpioDevices.py                           #
#                                                                             #
###############################################################################

  BUNDLE:  Raspberry Pi General Purpose Input/Output for Indigo
           (Pi GPIO.indigoPlugin)
  MODULE:  pigpioDevices.py
   TITLE:  Pi GPIO io device management
FUNCTION:  pigpioDevices.py provides classes to define and manage six types
           of Pi GPIO devices.
   USAGE:  pigpioDevices.py is included by the primary plugin module,
           plugin.py.  Its methods are called as needed by plugin.py methods.
  AUTHOR:  papamac
 VERSION:  0.9.2
    DATE:  September 12, 2023

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

The Pi GPIO plugin bundle has two primary Python modules/classes: plugin.py
encapsulates the Indigo device behavior in the Plugin class, and this module,
pigpioDevices.py encapsulates detailed Raspberry Pi GPIO device behavior in the
PiGPIODevice class and its six subclasses.  A PiGPIODevice subclass instance is
created for each Indigo device defined by plugin.py.  The plugin bundle
contains two supporting Python modules: pigpio.pi with classes/methods to
access the pigpio server daemon and conditionalLogging.py to provide flexible
Indigo logging by message type and logging level.  It also includes several xml
files that define Indigo GUIs, actions, and events.

MODULE pigpioDevices.py DESCRIPTION:

The pigpioDevices module is a collection of global data structures, module
level functions and classes that encapsulates all of the behavior or all the
Raspberry Pi io devices currently supported by the plugin.  The primary
PiGPIODevice class is an abstract base class that provides common methods that
are used by all subclasses.  Six subclasses, ADC12, ADC18, DAC12,
DockerPiRelay, IOExpander, and PiGPIO, contain methods that are specific to
a particular set of related io devices.

DEPENDENCIES/LIMITATIONS:

The classes and methods in the pigpioDevices module depend on the pigpio Python
library and the corresponding Raspberry Pi pigpio daemon server software.  Both
of these were written by joan2937, et al and are available on
gitHub.com/joan2937/pigpio.  The current version is v79 released on March 2,
2021.  The pigpio Python library is included in the plugin bundle as the module
pygpio.py.  The pigpio daemon is included in current Raspberry Pi OS
distributions.  There has been no recent change activity in this software and
it generally works well with the plugin.

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
v0.7.1   2/15/2023  Simplify code for spi integrity checks.
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
v0.9.2   9/12/2023  (1) Refactor resource management methods (again!) to
                    further simplify io device starting/stopping.
                    (2) Limit frequent triggers to no more than one every 5
                    minutes.
                    (3) Add method docstrings for most methods.
                    (4) Update module docstring in preparation for initial
                    release.
"""
###############################################################################
#                                                                             #
#                   DUNDERS, IMPORTS, and GLOBAL Constants                    #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '0.9.2'
__date__ = '9/12/2023'

import indigo

from abc import ABC, abstractmethod
from datetime import datetime
from logging import getLogger
from time import sleep

from conditionalLogging import LD, LI
import pigpio

# General global constants:

L = getLogger("Plugin")  # Standard Plugin logger.
ON_OFF = ('off', 'on')   # onOffState text values.

# Global dictionary of io device data keyed by io device type:
# IODEV_DATA[ioDevType] = (ioDevClass, interface)

IO_DEV_CLASS = {
    'dkrPiRly': 'DockerPiRelay',
    'MCP23008': 'IOExpander',     'MCP23017': 'IOExpander',
    'MCP23S08': 'IOExpander',     'MCP23S17': 'IOExpander',
    'MCP3202':  'ADC12',          'MCP3204':  'ADC12',
    'MCP3208':  'ADC12',
    'MCP3422':  'ADC18',          'MCP3423':  'ADC18',
    'MCP3424':  'ADC18',
    'MCP4801':  'DAC12',          'MCP4802':  'DAC12',
    'MCP4811':  'DAC12',          'MCP4812':  'DAC12',
    'MCP4821':  'DAC12',          'MCP4822':  'DAC12',
    'pigpio':   'PiGPIO'}

###############################################################################
#                                                                             #
#                        Global Internal Dictionaries                         #
#                                                                             #
###############################################################################

# Prior trigger data that are used to limit frequent event triggers keyed by
# the event name:

_priorTriggerTime = {}
_limitTriggers = {}

# io device instance objects keyed by device id:
# _ioDevices[dev.id] = <io device instance object>

_ioDevices = {}

# Shared pigpiod resources that are used by by multiple io devices keyed by the
# resource id:

_resources = {}


###############################################################################
#                                                                             #
#                         Internal Module Functions                           #
#                                                                             #
# def _getDev(devName)                                                        #
# def _hexStr(byteList)                                                       #
# def _executeEventTriggers(dev, eventType, eventName, description='')        #
# def _pigpioError(dev, errorType, errorMessage)                              #
#                                                                             #
###############################################################################

def _getDev(devName):
    """
    Return a valid Indigo device object from the Indigo device name.  If the
    Device is not in the database, return None.  if the device is in the
    dictionary, but is not enabled and configured, return False.  This function
    is a stronger form of the method get to ensure that a returned device is
    not only available, but is usable.
    """
    dev = indigo.devices.get(devName)
    if dev:
        if not dev.configured or not dev.enabled:
            return
    return dev


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


def _executeEventTriggers(dev, eventType, eventName, description='',
                          limitTriggers=False):
    """
    Conditionally execute all Indigo triggers for an eventType/eventName.  If
    a named event occurs at a frequency greater then 1 per second, limit the
    trigger execution to approximately 1 in 10 seconds.  Save data needed to
    respond to the event in the trigger object's pluginProps.  Do not limit
    trigger execution if the argument limitTriggers is False.
    """
    eventTime = datetime.now()

    # Limit frequent triggers if desired.

    if limitTriggers:
        priorTriggerTime = _priorTriggerTime.get(eventName)
        dt = (eventTime - priorTriggerTime).total_seconds() \
            if priorTriggerTime else 300.0
        if dt < 10.0:  # Turn on _limitTriggers for frequent triggers.
            if not _limitTriggers.get(eventName):
                L.warning('"%s" limiting frequent triggers for %s events',
                          dev.name, eventName)
            _limitTriggers[eventName] = True
        elif dt >= 300.0:  # Turn off _limitTriggers for infrequent triggers.
            _limitTriggers[eventName] = False
        if _limitTriggers.get(eventName):  # Do not execute the triggers.
            return

    # Execute all Indigo triggers matching the eventType and eventName.

    for trig in indigo.triggers.iter('self'):
        if trig.enabled and trig.pluginTypeId == eventType:
            pluginProps = trig.pluginProps
            triggerEvent = pluginProps['triggerEvent']
            if triggerEvent in ('any', eventName):
                pluginProps['eventTime'] = str(eventTime)
                pluginProps['devName'] = dev.name
                pluginProps['eventName'] = eventName
                pluginProps['description'] = description
                trig.replacePluginPropsOnServer(pluginProps)
                indigo.trigger.execute(trig)
    _priorTriggerTime[eventName] = eventTime


def _pigpioError(dev, errorType, errorMessage):
    """
    Perform the following standard functions for an io device error:

    1. Log the error on the Indigo log.
    2. Highlight the error in the Indigo Home Window by changing the device
       error state and setting the text to red.
    3. Execute an event trigger to invoke other actions, if any, by the
       Indigo server.
    4. Stop the io device to disable any future use until it has been manually
       restarted or the plugin has been reloaded.
    """
    errorName = errorType.replace('int', 'interrupt') + ' error'
    L.error('"%s" %s: %s', dev.name, errorName, errorMessage)
    dev.setErrorStateOnServer('%s err' % errorType)
    _executeEventTriggers(dev, 'pigpioError', errorName.upper(),
                          limitTriggers=True)
    getIoDev(dev).stop()


###############################################################################
#                                                                             #
#                          Public Module Functions                            #
#                                                                             #
# def getIoDev(dev, new=False)                                                #
# def logStartupSummary()                                                     #
# def logShutdownSummary()                                                    #
#                                                                             #
###############################################################################

def getIoDev(dev, new=False):
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
    startup (e.g., getIoDev(dev).read()).

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

            # Get the io device class from the IO_DEV_CLASS dictionary.

            ioDevType = dev.pluginProps['ioDevType']
            ioDevClass = IO_DEV_CLASS[ioDevType]

            # Create and start a new instance of the device class.

            try:
                ioDev = globals()[ioDevClass](dev)
            except ConnectionError as errorMessage:
                _pigpioError(dev, 'conn', errorMessage)
                return
            except Exception as errorMessage:
                _pigpioError(dev, 'start', errorMessage)
                return

            # Complete successful io device startup.

            LI.startStop('"%s" started as a %s on %s',  # Log it for debug.
                         dev.name, dev.deviceTypeId, dev.address)
            dev.setErrorStateOnServer(None)  # Clear any PiGPIO device errors.

    return ioDev  # return the io device object.


def logStartupSummary():
    """
    Log the number of io devices started and the number of pigpio resources
    used.
    """
    L.info('%s io devices started using %s pigpio resources',
           len(_ioDevices), len(_resources))


def logShutdownSummary():
    """ Log the io device and resource status at shutdown. """
    if _ioDevices:
        L.warning('%s io devices still active at shutdown',
                  len(_ioDevices))
    else:
        L.info('All io devices stopped')

    if _resources:
        L.warning('%s pigpio resources still reserved at shutdown',
                  len(_resources))
    else:
        L.info('All pigpio resources stopped/closed')


###############################################################################
#                                                                             #
#                             CLASS PiGPIODevice                              #
#                                                                             #
# Internal instance methods:                                                  #
#                                                                             #
# def __init__(self, dev)                                                     #
# def _getConnection(self)                                                    #
# def _getI2cHandle(self)                                                     #
# def _getSpiHandle(self)                                                     #
# def _releaseConnection(self, connectionId)                                  #
# def _releaseHandle(self, handleId)                                          #
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
#                                                                             #
###############################################################################

class PiGPIODevice(ABC):
    """
    PiGPIODevice is an abstract base class (ABC) that is used in defining all
    six of the io device subclasses.  It defines a number of internal and
    public methods that are common to all of the subclasses.  These methods
    encapsulate all of the common PiGPIODevice behavior:

    __init__                  Initializes common instance attributes and
                              connects to a pigpio daemon.
    _getConnection            Creates/reserves a connection to a pigpio daemon.
    _getI2cHandle             Opens/reserves a handle to access an i2c device.
    _getSpiHandle             Opens/reserves a handle to access a spi device.
    _releaseConnection        Releases/stops a connection.
    _releaseHandle            Releases/closes an i2c or spi handle.
    _updateOnOffState         Updates the onOffState on the Indigo server.
    _uiValue                  Computes uiValues for sensor value processing.
    _updateSensorValueStates  Updates sensor value states on the Indigo server
                              and processes sensor values.
    read                      Calls the _read abstract method.
    write                     Calls the _write abstract method.
    poll                      Called by the runConcurrentThread method in
                              plugin.py to read io devices (poll them) at a
                              unique rate for each device.
    stop                      Stops an io device and releases its reserved
                              resources.

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

    # Class constants:

    I2CBUS = 1  # Primary i2c bus.
    SPIBUS = 0  # Primary spi bus.
    IMAGE_SEL = (indigo.kStateImageSel.SensorOff,  # Sensor off/on image sel.
                 indigo.kStateImageSel.SensorOn)

    # Internal instance methods:

    def __init__(self, dev):
        """
        Add the new io device object to the io devices dictionary, initialize
        common internal instance attributes, and connect to the pigpio daemon.
        Set a common Indigo home window state image for all io devices.
        """

        # Add the io device instance object to the internal _ioDevices
        # dictionary.

        _ioDevices[dev.id] = self

        # Initialize common internal instance attributes:

        self._dev = dev          # Indigo device reference.
        self._c = None           # pigpiod connection object.
        self._h = None           # i2c or spi handle.
        self._hId = None         # i2c or spi handle id.
        self._callbackId = None  # gpio callback identification object.
        self._pollCount = 0      # Poll count for polling status monitoring.
        self._lastPoll = self._lastStatus = indigo.server.getTime()

        # Connect to the pigpio daemon and set internal connection attributes
        # for use by all class/subclass methods.

        self._c, self._cId = self._getConnection()

        # Set the initial device state image to override power icon defaults
        # for digital output devices.

        onOffState = dev.states['onOffState']
        dev.updateStateImageOnServer(self.IMAGE_SEL[onOffState])

    # Internal pigpiod resource management methods.

    def _getConnection(self):
        """
        A connection object establishes a connection to a specific pigpio
        daemon running on a specific pi host.  Connection object methods in the
        pigpio library perform all input/output operations on individual gpio
        pins, i2c devices, and spi devices.

        Create a pigpio connection id using the host id, host address, and port
        number from the Indigo device pluginProps.  Get a connection object for
        this id from the resources dictionary.  If no connection exists, use
        the pigpio.pi module function to create a new one.  Reserve the
        existing or new connection object by incrementing its use count and
        updating the dictionary.  Log the connection usage for debug.  Return
        the connection object and id.
        """
        hostId = self._dev.pluginProps['hostId']
        hostAddress = self._dev.pluginProps['hostAddress']
        portNumber = self._dev.pluginProps['portNumber']
        connectionId = hostId if hostId else hostAddress + ':' + portNumber

        connection, useCount = _resources.get(connectionId, (None, 0))
        if not connection:  # No existing connection; create a new one.
            LD.resource('"%s" connecting to %s', self._dev.name, connectionId)
            connection = pigpio.pi(hostAddress, portNumber)
            if not connection.connected:  # Connection failed.
                connection.stop()  # Release any pigpiod resources immediately.
                raise ConnectionError('connection failed')

        useCount += 1  # Reserve the connection for this io device.
        _resources[connectionId] = connection, useCount
        LD.resource('"%s" using connection %s(%s)',
                    self._dev.name, connectionId, useCount)
        return connection, connectionId

    def _getI2cHandle(self):
        """
        An i2c handle is an integer that identifies a specific i2c device on
        a specific pi host.  Connection object methods use the i2c handle to
        direct operations to the desired device.

        Create an i2c handle id using the i2c device's address from the Indigo
        device pluginProps.  Include the connection id to make it unique for
        this io device's connection.  Get a handle for this id from the
        resources dictionary.  If no handle exists, use the pigpio library
        method i2c_open to open a new one.  Reserve the existing or new handle
        by incrementing its use count and updating the dictionary.  Log the
        handle usage for debug.  Return the handle and the handle id.
        """
        prefix = self._cId + '.i2c'
        i2cAddress = self._dev.pluginProps['i2cAddress']
        handleId = prefix + '.' + i2cAddress

        handle, useCount = _resources.get(handleId, (None, 0))
        if handle is None:  # No existing i2c handle; open a new one.
            LD.resource('"%s" opening new handle id %s',
                        self._dev.name, handleId)
            handle = self._c.i2c_open(self.I2CBUS, int(i2cAddress, base=16))

        useCount += 1  # Reserve the handle for this io device.
        _resources[handleId] = handle, useCount
        LD.resource('"%s" using handle %s%s(%s)',
                    self._dev.name, prefix, handle, useCount)
        return handle, handleId

    def _getSpiHandle(self):
        """
        An spi handle is an integer that identifies a specific spi channel,
        using a specific input/output data rate, on a specific pi host.
        Connection object methods use the spi handle to direct operations to
        one or more devices connected to the spi channel.

        Create a spi handle id using the spi device's channel number and bit
        rate from the Indigo device pluginProps.  Include the connection id to
        make it unique for this io device's connection.  Get a handle for this
        id from the resources dictionary.  If no handle exists, use the pigpio
        library method spi_open to open a new one.  Reserve the existing or new
        handle by incrementing its use count and updating the dictionary.  Log
        the handle usage for debug.  Return the handle and the handle id.
        """
        prefix = self._cId + '.spi'
        spiChannel = self._dev.pluginProps['spiChannel']
        bitRate = int(500000 * float(self._dev.pluginProps['bitRate']))
        handleId = prefix + '.' + spiChannel + '.' + str(bitRate)

        handle, useCount = _resources.get(handleId, (None, 0))
        if handle is None:  # No existing spi handle; open a new one.
            LD.resource('"%s" opening new handle id %s',
                        self._dev.name, handleId)
            handle = self._c.spi_open(int(spiChannel), bitRate,
                                      self.SPIBUS << 8)

        useCount += 1  # Reserve the handle for this io device.
        _resources[handleId] = handle, useCount
        LD.resource('"%s" using handle %s%s(%s)',
                    self._dev.name, prefix, handle, useCount)
        return handle, handleId

    def _releaseConnection(self, connectionId):
        """
        Get the connection and use count for this io device from the resources
        dictionary.  Decrement the use count and update the dictionary to
        release the connection.  If the use count is zero, delete the
        connection and stop it to return all resources to the pigpio daemon.
        """
        connection, useCount = _resources[connectionId]
        useCount -= 1
        LD.resource('"%s" releasing connection %s(%s)',
                    self._dev.name, connectionId, useCount)
        _resources[connectionId] = connection, useCount
        if not useCount:
            LD.resource('"%s" stopping connection to %s',
                        self._dev.name, connectionId)
            del _resources[connectionId]
            connection.stop()

    def _releaseHandle(self, handleId):
        """
        Get the handle and use count for this io device from the resources
        dictionary.  Decrement the use count and update the dictionary to
        release the handle.  If the use count is zero, delete the handle
        and close it to return all resources to the pigpio daemon.
        """
        handle, useCount = _resources[handleId]
        useCount -= 1
        hSplit = handleId.split('.')
        hName = hSplit[0] + '.' + hSplit[1] + str(handle)
        LD.resource('"%s" releasing handle %s(%s)',
                    self._dev.name, hName, useCount)
        _resources[handleId] = handle, useCount
        if not useCount:
            del _resources[handleId]
            LD.resource('"%s" closing handle %s', self._dev.name, hName)
            if hSplit[1] == 'i2c':
                self._c.i2c_close(handle)
            else:
                self._c.spi_close(handle)

    # Internal support methods:

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
        uiValue = sensorUiValue if displayStateId == 'sensorValue' \
            else onOffUiValue
        self._dev.updateStateOnServer(key='onOffState', value=onOffState,
                                      uiValue=uiValue, clearErrorState=False)
        self._dev.updateStateImageOnServer(self.IMAGE_SEL[onOffState])

        # Log the onOffState if a change is detected and logAll is not None.
        # If there is no change, log it if logAll is True.

        onOffText = onOffUiValue
        onOffText += ' <' + sensorUiValue + '>' if sensorUiValue else ''
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
        Perform common sensor value processing, state updating, and logging
        for both ADC and DAC devices.  Compute the sensor value from the ADC or
        DAC voltage.  Compute the uiValue and update the sensorValue state on
        the Indigo server.  Optionally perform sensor value percentage change
        detection, analog onOffState thresholding, and limit checking.  Update
        states, log results, and execute event triggers based on processing
        results.
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

        percentChange = 100.0 * abs((sensorValue - priorSensorValue)
            / priorSensorValue) if priorSensorValue else 0.001
        changeThreshold = self._dev.pluginProps['changeThreshold']
        changeDetected = False if changeThreshold == 'None' \
            else percentChange > float(changeThreshold)
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
        onOffState = 0 if onThreshold == 'None' \
            else sensorValue > float(onThreshold)
        self._updateOnOffState(onOffState, sensorUiValue=sensorUiValue,
                               logAll=logAll)

        # Perform limit checking and determine the limitFault states.

        lowLimit = self._dev.pluginProps['lowLimit']  # Check low limit.
        lowLimitFault = False if lowLimit == 'None' \
            else sensorValue < float(lowLimit)

        highLimit = self._dev.pluginProps['highLimit']  # Check high limit.
        highLimitFault = False if highLimit == 'None' \
            else sensorValue > float(highLimit)

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
        """ Standard internal read method for all subclasses. """
        pass

    @abstractmethod
    def _write(self, value):
        """ Standard internal write method for all subclasses. """
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
        Read the io device at the specified polling interval.  Log the polled
        value if it has changed from the previous value or if the logAll
        property is set.  If status monitoring is enabled, accumulate polling
        statistics and log them at the specified status interval.
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
        Stop the pigpio device by removing it from the io devices dictionary
        and the interrupt devices list in the linked interrupt relay GPIO
        device (if applicable).  Cancel any gpio callback and release/close/
        stop any pigpio daemon shared resources.
        """
        try:
            # Remove the io device from the io devices dictionary.

            del _ioDevices[self._dev.id]

            # Check to see if the io device is an interrupt device.  If so,
            # remove it from the from the interrupt devices list in the
            # interrupt relay GPIO device.

            if 'hardwareInterrupt' in self._dev.pluginProps:  # Interrupt dev.
                interruptRelayGPIO = self._dev.pluginProps[
                    'interruptRelayGPIO']
                interruptRelayDev = _getDev(interruptRelayGPIO)
                if interruptRelayDev:  # Device available?
                    rioDev = getIoDev(interruptRelayDev)
                    if rioDev:
                        LD.digital('"%s" removing interrupt device id from '
                                   '"%s"', self._dev.name, interruptRelayGPIO)
                        rioDev.updateInterruptDevices(self._dev.id, add=False)

            # Cancel the gpio callback, if any.

            if self._callbackId:
                self._callbackId.cancel()

            # Release/close/stop pigpiod shared resources.

            if self._c:  # Proceed only if the instance is connected.
                if self._h is not None:  # Bypass for gpio devices.
                    self._releaseHandle(self._hId)
                self._releaseConnection(self._cId)

        except Exception as errorMessage:

            # Stop exceptions often follow another Pi GPIO exception/error
            # because the device is stopped and the error often interferes
            # with the release of pigpiod resources.  Log a warning message,
            # but do not call_pigpioError and trigger another event.

            L.warning('"%s" stop error: %s', self._dev.name, errorMessage)

        # Log successful stop completion for debugging.

        LI.startStop('"%s" stopped', self._dev.name)


###############################################################################
#                                                                             #
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
    """
    Read data from the 12-bit ADC devices MCP3202, MCP3204, and MCP3208 using
    the pigpio library spi methods.  Update the states in the Indigo device.
    Implement device operation instructions and spi communications protocols
    from the following hardware references.

    MCP3202:    <https://ww1.microchip.com/downloads/en/DeviceDoc/21034F.pdf>
    MCP3204/8:  <https://ww1.microchip.com/downloads/en/devicedoc/21298e.pdf>

    Check the spi read integrity if requested in the pluginProps.
    """

    # Internal instance methods:

    def __init__(self, dev):
        """
        Initialize common and unique instance attributes for ADC12 devices.
        """
        PiGPIODevice.__init__(self, dev)  # Common initialization.
        self._h, self._hId = self._getSpiHandle()  # spi interface.

        # Assemble data configuration tuple.

        inputConfiguration = int(dev.pluginProps['inputConfiguration'])
        adcChannel = int(self._dev.pluginProps['adcChannel'])
        self._data = (0x04 | inputConfiguration << 1 | adcChannel >> 2,
                      (adcChannel << 6) & 0xff, 0)
        if self._dev.pluginProps['ioDevType'] == 'MCP3202':
            self._data = (0x01, inputConfiguration << 7 | adcChannel << 6, 0)

    def _readADCOutputCode(self):
        """
        Read and return a single 12-bit ADC output code (0-4095).
        """
        nBytes, bytes_ = self._c.spi_xfer(self._h, self._data)
        counts = (bytes_[1] & 0x0f) << 8 | bytes_[2]
        LD.analog('"%s" read %s | %s | %s | %s', self._dev.name,
                  _hexStr(self._data), nBytes, _hexStr(bytes_), counts)
        return counts

    # Implementation of abstract methods:

    def _read(self, logAll=True):
        """
        Read the ADC output code.  Check the spi integrity, if requested, by
        reading it a second time and comparing the results.  Log a warning
        message if the values differ by more than 10 counts.  Convert the
        counts to a voltage and perform common sensor value processing, state
        updating, and logging.
        """
        counts = self._readADCOutputCode()
        if self._dev.pluginProps['checkSPI']:  # Check spi integrity.
            counts_ = self._readADCOutputCode()
            if abs(counts - counts_) > 10:
                L.warning('"%s" spi check: different values on consecutive '
                          'reads %s %s', self._dev.name, counts, counts_)
            counts = counts_

        referenceVoltage = float(self._dev.pluginProps['referenceVoltage'])
        voltage = referenceVoltage * counts / 4096
        self._updateSensorValueStates(voltage, logAll=logAll)

    def _write(self, value):
        """ Dummy method to allow a write to a read-only device. """
        pass


###############################################################################
#                                                                             #
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
    """
    Read data from the 18-bit ADC devices MCP3422, MCP3423, and MCP3424 using
    the pigpio library i2c methods.  Update the states in the Indigo device.
    Implement device operation instructions and i2c communications protocols
    from the following hardware references.

    MCP3422/3/4: <https://ww1.microchip.com/downloads/en/devicedoc/22088c.pdf>

    Check the spi read integrity if requested in the pluginProps.
    """

    # Internal instance method:

    def __init__(self, dev):
        """
        Initialize common and unique instance attributes for ADC18 devices.
        """
        PiGPIODevice.__init__(self, dev)  # Common initialization.
        self._h, self._hId = self._getI2cHandle()  # i2c interface.

        # Assemble ADC configuration byte.

        notReady = 0x80  # Not-ready bit.
        adcChannel = int(dev.pluginProps['adcChannel'])
        conversionMode = 0  # One-shot conversion mode.
        resolution = int(dev.pluginProps['resolution'])
        resolutionIndex = (resolution - 12) >> 1
        gain = dev.pluginProps['gain']
        gainIndex = '1248'.find(gain)
        self._config = notReady | adcChannel << 5 | conversionMode << 4 \
            | resolutionIndex << 2 | gainIndex

    # Implementation of abstract methods:

    def _read(self, logAll=True):
        """
        Start a conversion and then iteratively read the ADC until the the
        conversion completes. Convert the ADC counts to a voltage and perform
        common sensor value processing, state updating, and logging.
        """

        # Start the conversion in the single shot mode.

        self._c.i2c_write_byte(self._h, self._config)

        # Read the conversion register until the not-ready bit is cleared in
        # the returned config byte (last byte received).  This indicates that
        # the output register has been updated (ready == ~ notReady).

        notReady = 0x80  # Not-ready bit.
        config = self._config & (~ notReady)  # Clear the not-ready bit.
        resolution = int(self._dev.pluginProps['resolution'])
        numToRead = 3 if resolution < 18 else 4  # Num of bytes to read.

        numReads = 0
        while True:
            numBytes, bytes_ = self._c.i2c_read_i2c_block_data(
                self._h, config, numToRead)
            numReads += 1
            if not (bytes_[-1] & notReady):  # Stop if ready.
                break

        # Pack bytes from the returned bytearray into a single integer output
        # code.

        counts = -1 if bytes_[0] & 0x80 else 0
        for byte in bytes_[:-1]:
            counts = counts << 8 | byte

        # Compute the voltage and update/log the sensor value states.

        referenceVoltage = 2.048  # Internal reference voltage (volts).
        maxCode = 1 << (resolution - 1)  # maxCode = 2 ** (resolution - 1).
        gain = int(self._dev.pluginProps['gain'])
        voltage = referenceVoltage * counts / (maxCode * gain)
        LD.analog('"%s" read %s | %s | %s | %s', self._dev.name, numReads,
                  _hexStr(bytes_), counts, voltage)
        self._updateSensorValueStates(voltage, logAll=logAll)

    def _write(self, value):
        """ Dummy method to allow a write to a read-only device. """
        pass


###############################################################################
#                                                                             #
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
    """
    Write data to the 8/10/12-bit DAC devices MCP4801, MCP4802, MCP4811,
    MCP4812, MCP4821, and MCP4822 using the pigpio library spi methods.  Update
    the states in the Indigo device.  Implement device operation instructions
    and spi communications protocols from the following hardware references.

    MCP4801/11/21:  <https://ww1.microchip.com/downloads/en/DeviceDoc/22244B.pdf>
    MCP4802/12/22:  <https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/20002249B.pdf>
    """

    # Internal instance method:

    def __init__(self, dev):
        """
        Initialize common and unique instance attributes for DAC12 devices.
        """
        PiGPIODevice.__init__(self, dev)  # Common initialization.
        self._h, self._hId = self._getSpiHandle()  # spi interface.

    # Implementation of abstract methods:

    def _read(self, logAll=True):
        """
        Perform common sensor value processing/logging using the current sensor
        value state.  Get the current sensor value from the Indigo device and
        compute the equivalent DAC input voltage.  Perform the same sensor
        value processing, state updating, and logging functions as those used
        for ADC devices.
        """
        sensorValue = self._dev.states['sensorValue']
        scalingFactor = float(self._dev.pluginProps['scalingFactor'])
        voltage = sensorValue / scalingFactor
        self._updateSensorValueStates(voltage, logAll=logAll)

    def _write(self, value):
        """
        Check the sensor value argument, convert it to a DAC input code and
        write it to the DAC.  Perform common sensor value processing, state
        updating, and logging.
        """

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
            nBytes = self._c.spi_write(self._h, data)
            LD.analog('"%s" xfer %s | %s | %s | %s', self._dev.name, voltage,
                      inputCode, _hexStr(data), nBytes)
        else:
            L.warning('"%s" converted input code %s is outside of DAC '
                      'range; write ignored', self._dev.name, inputCode)
            return

        # Update/log the sensor value states.

        self._updateSensorValueStates(voltage)


###############################################################################
#                                                                             #
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
    """
    Write a single bit value to a dkrPiRly device using the pigpio library i2c
    methods.  Update the onOffState in the Indigo device.  Implement device
    operation instructions and i2c communications protocols from the following
    hardware reference.

    <https://wiki.52pi.com/index.php?title=EP-0099>
    """

    # Internal instance method:

    def __init__(self, dev):
        """
        Initialize common and unique instance attributes for DockerPiRelay
        devices.
        """
        PiGPIODevice.__init__(self, dev)  # Common initialization.
        self._h, self._hId = self._getI2cHandle()  # i2c interface.

    # Implementation of abstract methods:

    def _read(self, logAll=True):
        """
        Perform common onOffState updating and logging using the current Indigo
        device onOffState.
        """
        onOffState = self._dev.states['onOffState']
        self._updateOnOffState(onOffState, logAll=logAll)

    def _write(self, value):
        """
        Check the bit value argument and write it to the relay device.
        Update the Indigo device onOffState.  Implement the momentary
        activation function, if requested.
        """
        bit = 99
        try:
            bit = int(value)
        except ValueError:
            pass
        if bit in (0, 1):
            relayNumber = int(self._dev.pluginProps['relayNumber'])
            self._c.i2c_write_byte_data(self._h, relayNumber, bit)
            LD.digital('"%s" write %s', self._dev.name, ON_OFF[bit])
            self._updateOnOffState(bit)
            if bit:
                if self._dev.pluginProps['momentary']:
                    sleep(float(self._dev.pluginProps['turnOffDelay']))
                    self._write(0)
        else:
            L.warning('"%s" invalid output value %s; write ignored',
                      self._dev.name, value)


###############################################################################
#                                                                             #
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
    Read and write bit values from/to the 8/16-bit IO Expander Devices
    MCP23008, MCP23S08, MCP23017 and MCP23S17 using the pigpio library i2c/spi
    methods.  Link devices requiring a hardware interrupt to interrupt relay
    gpio devices if requested.  Update the onOffState in the Indigo device.
    Implement device operation instructions and i2c/spi communications
    protocols from the following hardware references.

    MCP32008/S08:  <https://ww1.microchip.com/downloads/en/DeviceDoc/21919e.pdf>
    MCP32017/S17:  <https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf>
    """

    # Class constants.
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
        """
        Initialize common instance attributes for IOExpander devices.  Get an
        i2c or spi handle for the device based on the io device type.
        Determine whether the device is to be used as a digital input or a
        digital output.  Initialize device registers and internal instance
        attributes for the intended use.  If the device is to be used with
        a hardware interrupt, manage the interrupt devices lists in prior and
        current interrupt relay GPIO devices.
        """
        PiGPIODevice.__init__(self, dev)  # Common initialization.
        self._i2c = 'S' not in dev.pluginProps['ioDevType']
        if self._i2c:
            self._h, self._hId = self._getI2cHandle()  # i2c interface.
        else:
            self._h, self._hId = self._getSpiHandle()  # spi interface.

        # Define unique internal instance attributes.

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

        # Set registers by device type:

        if dev.deviceTypeId == 'digitalOutput':
            self._updateRegister('IODIR', self.OUTPUT)
            self._updateRegister('GPINTEN', 0)  # No interrupt for output.

        else:  # dev.deviceTypeId == 'digitalInput'
            self._updateRegister('IODIR', self.INPUT)
            invert = self._dev.pluginProps['invert']
            self._updateRegister('IPOL', invert)  # Set input polarity.
            pullup = dev.pluginProps['pullup']
            self._updateRegister('GPPU', pullup == 'up')  # Set pullup option.
            self._updateRegister('DEFVAL', 0)  # Clear default bit.
            self._updateRegister('INTCON', 0)  # Interrupt on change.

            # Update the interrupt devices lists in the prior and current
            # interrupt relay GPIO devices.

            priorInterruptRelayGPIO = dev.pluginProps[
                                      'priorInterruptRelayGPIO']
            interruptRelayGPIO = dev.pluginProps['interruptRelayGPIO']
            LD.digital('"%s" prior, current interrupt relay GPIOs are: %s, %s',
                       dev.name, priorInterruptRelayGPIO, interruptRelayGPIO)

            if priorInterruptRelayGPIO != interruptRelayGPIO:

                # If the relay device changed, remove this device (the
                # interrupt device) from the interrupt devices list in the
                # prior relay device.

                priorInterruptRelayDev = _getDev(priorInterruptRelayGPIO)
                if priorInterruptRelayDev:  # Device available?
                    getIoDev(priorInterruptRelayDev) \
                        .updateInterruptDevices(dev.id, add=False)

            if interruptRelayGPIO:

                # Check interruptRelayGPIO device for validity and for relay
                # interrupts enabled.  If OK, add this device to the interrupt
                # devices list in the interruptRelayGPIO device.

                interruptRelayDev = _getDev(interruptRelayGPIO)
                if interruptRelayDev:  # Device available?
                    if interruptRelayDev.pluginProps['relayInterrupts']:
                        getIoDev(interruptRelayDev, new=True) \
                            .updateInterruptDevices(dev.id)
                    else:  # Interrupt relay is not enabled.
                        L.warning('"%s" interrupt relay device "%s" is not '
                                  'enabled for interrupt relay',
                                  dev.name, interruptRelayGPIO)
                else:
                    L.warning('"%s" interrupt relay device "%s" is not in '
                              'database or is not configured/enabled',
                              dev.name, interruptRelayGPIO)

            # There may be an interrupt pending.  Update interrupt control
            # register only after the current interrupt device list is updated.

            hardwareInterrupt = dev.pluginProps['hardwareInterrupt']
            self._updateRegister('GPINTEN', hardwareInterrupt)

    def _readSpiByte(self, register, control):
        """
        Read and return a single byte of data over the spi bus as directed by
        the spi control tuple.
        """
        nBytes, bytes_ = self._c.spi_xfer(self._h, control)
        LD.digital('"%s" readRegister %s %s | %s | %s', self._dev.name,
                   register, _hexStr(control), nBytes, _hexStr(bytes_))
        return bytes_[-1]

    def _readRegister(self, register):
        """
        Read and return a single byte of data from the specified device
        register.  Use pigpio library methods for i2c or spi based on the
        device type.  For an spi operation, check the read integrity if
        requested in the pluginProps.
        """
        registerAddress = self.REG_BASE_ADDR[register] + self._offset

        if self._i2c:  # MCP230XX - i2c interface
            byte = self._c.i2c_read_byte_data(self._h, registerAddress)
            LD.digital('"%s" readRegister %s %02x',
                       self._dev.name, register, byte)
        else:  # MCP23SXX - spi interface
            spiDevAddress = int(self._dev.pluginProps['spiDevAddress'], 16)
            control = (spiDevAddress << 1 | self.READ, registerAddress, 0)
            byte = self._readSpiByte(register, control)

            if self._dev.pluginProps['checkSPI']:  # Check spi integrity.
                byte_ = self._readSpiByte(register, control)
                if byte != byte_:
                    L.warning('"%s" readRegister %s spi check: unequal '
                              'consecutive reads %02x %02x',
                              self._dev.name, register, byte, byte_)
                    byte = byte_
        return byte

    def _writeRegister(self, register, byte):
        """
        Write a single byte of data to the specified device register.  Use
        pigpio library methods for i2c or spi based on the device type.
        """
        registerAddress = self.REG_BASE_ADDR[register] + self._offset

        if self._i2c:  # MCP230XX - i2c interface
            self._c.i2c_write_byte_data(self._h, registerAddress, byte)
            LD.digital('"%s" writeRegister %s %02x',
                       self._dev.name, register, byte)

        else:  # MCP23SXX - spi interface
            spiDevAddress = int(self._dev.pluginProps['spiDevAddress'], 16)
            control = (spiDevAddress << 1 | self.WRITE, registerAddress, byte)
            nBytes = self._c.spi_write(self._h, control)
            LD.digital('"%s" writeRegister %s %s | %s',
                       self._dev.name, register, _hexStr(control), nBytes)

    def _updateRegister(self, register, bit):
        """
        Read a device register, replace the bit specified by the device bit
        number (from the pluginProps) with the bit argument, and then write the
        register if it has changed.
        """
        byte = self._readRegister(register)
        updatedByte = byte | self._mask if bit else byte & ~self._mask
        if updatedByte != byte:
            LD.digital('"%s" updateRegister %s %02x | %s | %02x',
                       self._dev.name, register, byte, bit, updatedByte)
            self._writeRegister(register, updatedByte)

    # Implementation of abstract methods:

    def _read(self, logAll=True):
        """
        Read the GPIO register, extract the bit specified by the device bit
        number (from the pluginProps), and update/log the Indigo device
        onOffState.
        """
        byte = self._readRegister('GPIO')
        bit = 1 if byte & self._mask else 0
        self._updateOnOffState(bit, logAll=logAll)

    def _write(self, value):
        """
        Check the argument for a valid bit value, then use it to replace the
        GPIO register bit specified by the device bit number (from the
        pluginProps).  Update/log the Indigo device onOffState.  If the device
        is being turned on and momentary turn-on is requested in the
        pluginProps, sleep for the turnOffDelay time and then recursively call
        _write to turn it off.
        """
        bit = 99
        try:
            bit = int(value)
        except ValueError:
            pass
        if bit in (0, 1):  # Value is a valid bit value.
            self._updateRegister('GPIO', bit)
            self._updateOnOffState(bit)
            if bit:  # Device was turned on.
                if self._dev.pluginProps['momentary']:
                    sleep(float(self._dev.pluginProps['turnOffDelay']))
                    self._write(0)  # Turn it off.
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
        """
        Clear a pending interrupt from a digital input device by reading the
        GPIO register.  This method may be called by the interrupt relay gpio
        device if the interrupt times out, i.e., none of the devices in its
        interrupt devices list respond positively to their interrupt method
        calls.
        """
        try:
            self._readRegister('GPIO')
        except Exception as errorMessage:
            _pigpioError(self._dev, 'int', errorMessage)


###############################################################################
#                                                                             #
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
# Public instance method:                                                     #
#                                                                             #
# def updateInterruptDevices(self, intDevId, add=True)                        #
#                                                                             #
###############################################################################

class PiGPIO(PiGPIODevice):
    """
    Read and write bit values from/to built-in Raspberry Pi gpio pins using
    pigpio library methods and update/log the Indigo device onOffState.
    Respond to digital input callbacks (interrupts) to perform contact bounce
    filtering and interrupt relay if requested.  For digital outputs, perform
    pulse width modulation (pwm) and momentary turn-on processing if requested.
    Manage an internal interrupt devices list for use interrupt relay.
    """
    # Class constant:

    PUD = {'off':  pigpio.PUD_OFF,  # GPIO pullup parameter definitions.
           'up':   pigpio.PUD_UP,
           'down': pigpio.PUD_DOWN}

    # Internal instance methods:

    def __init__(self, dev):
        """
        Initialize common instance attributes and set pigpio daemon parameters
        for PiGPIO devices.  For digital input devices, setup callback, glitch
        filter, and interrupt relay options if requested.  For digital outputs,
        setup pwm processing if requested.
        """
        PiGPIODevice.__init__(self, dev)  # Common initialization.

        # Set internal instance attributes and configure the gpio device.

        self._gpioNumber = int(dev.pluginProps['gpioNumber'])

        if dev.deviceTypeId == 'digitalInput':
            self._c.set_mode(self._gpioNumber, pigpio.INPUT)
            pullup = dev.pluginProps['pullup']
            self._c.set_pull_up_down(self._gpioNumber, self.PUD[pullup])
            if dev.pluginProps['callback']:
                self._callbackId = self._c.callback(self._gpioNumber,
                                        pigpio.EITHER_EDGE, self._callback)
                self._priorTic = self._c.get_current_tick()
                if dev.pluginProps['glitchFilter']:
                    glitchTime = int(dev.pluginProps['glitchTime'])
                    self._c.set_glitch_filter(self._gpioNumber, glitchTime)
                if self._dev.pluginProps['relayInterrupts']:
                    self._interruptDevices = []  # Interrupt devices list.

        elif dev.deviceTypeId == 'digitalOutput':
            self._c.set_mode(self._gpioNumber, pigpio.OUTPUT)
            if dev.pluginProps['pwm']:
                self._c.set_PWM_range(self._gpioNumber, 100)
                frequency = int(dev.pluginProps['frequency'])
                self._c.set_PWM_frequency(self._gpioNumber, frequency)

    def _callback(self, gpioNumber, pinBit, tic):
        """
        Respond to an input device callback.  Apply the contact bounce filter
        if requested for both rising and falling transitions.  Relay the
        interrupt if requested on a rising edge by invoking the interrupt
        method for devices in the interrupt devices list until the first device
        responds.  Cancel the watchdog timer on a falling edge to close out the
        interrupt.  Update the Indigo device onOffState for both rising and
        falling transitions.  If the interrupt watchdog timer expires, attempt
        to clear the interrupt by calling the interruptReset method for all
        devices in the interrupt devices list.
        """
        try:
            dt = pigpio.tickDiff(self._priorTic, tic)
            self._priorTic = tic
            LD.digital('"%s" callback %s %s %s %s',
                       self._dev.name, gpioNumber, pinBit, tic, dt)
            logAll = True  # Default logging option for state update.
            if pinBit in (0, 1):
                bit = pinBit ^ self._dev.pluginProps['invert']

                # Apply the contact bounce filter, if requested.

                if self._dev.pluginProps['bounceFilter']:
                    if dt < self._dev.pluginProps['bounceTime']:  # Bouncing.
                        if self._dev.pluginProps['logBounce']:
                            L.warning('"%s" %s µs bounce; update to %s '
                                'ignored', self._dev.name, dt, ON_OFF[bit])
                        return  # Ignore the bounced state change.

                # Relay interrupt, if requested.

                elif self._dev.pluginProps['relayInterrupts']:
                    if bit:  # Rising edge; interrupt occurred.
                        # Set watchdog for 200 ms.
                        self._c.set_watchdog(self._gpioNumber, 200)
                        for intDevId in self._interruptDevices:
                            if _ioDevices[intDevId].interrupt():  # Interrupt.
                                break  # Only one match per interrupt.
                        else:  # No match.
                            L.warning('"%s" no device match for hardware '
                                      'interrupt', self._dev.name)
                    else:  # Falling edge; interrupt reset.
                        LD.digital('"%s" interrupt time is %s ms',
                                   self._dev.name, dt / 1000)
                        self._c.set_watchdog(self._gpioNumber, 0)  # Nix wdog.
                    logAll = None  # Set logAll to suppress logging.

                # Update the GPIO device onOffState for both normal and
                # interrupt relay callbacks.

                self._updateOnOffState(bit, logAll=logAll)

            elif pinBit == pigpio.TIMEOUT:  # Timeout; try to force a reset.
                L.warning('"%s" interrupt reset timeout', self._dev.name)
                for intDevId in self._interruptDevices:
                    _ioDevices[intDevId].resetInterrupt()  # Force int reset.
                self._c.set_watchdog(self._gpioNumber, 0)  # Nix watchdog.

                # Check to see if it worked.

                pinBit = self._c.read(self._gpioNumber)
                bit = pinBit ^ self._dev.pluginProps['invert']
                if bit:  # Interrupt is still active.
                    L.warning('"%s" forced reset failed', self._dev.name)

        except Exception as errorMessage:
            _pigpioError(self._dev, 'int', errorMessage)

    # Implementation of abstract methods:

    def _read(self, logAll=True):
        """
        Read a bit value from the gpio pin and invert it if requested.  Update
        and log the Indigo device onOffState.
        """
        invert = self._dev.pluginProps.get('invert', False)
        bit = self._c.read(self._gpioNumber) ^ invert
        LD.digital('"%s" read %s', self._dev.name, ON_OFF[bit])
        self._updateOnOffState(bit, logAll=logAll)

    def _write(self, value):
        """
        Check the argument for a valid bit value, write it to the gpio pin, and
        update/log the Indigo device onOffState.  If the device is being turned
        on and pwm is requested, start the pwm output by setting the pwm duty
        cycle.  If momentary turn-on is requested, sleep for the turnOffDelay
        time and then recursively call _write to turn it off.
        """
        bit = 99
        try:
            bit = int(value)
        except ValueError:
            pass
        if bit in (0, 1):
            self._c.write(self._gpioNumber, bit)
            LD.digital('"%s" write %s', self._dev.name, ON_OFF[bit])
            self._updateOnOffState(bit)
            if bit:
                if self._dev.pluginProps['pwm']:
                    dutyCycle = int(self._dev.pluginProps['dutyCycle'])
                    self._c.set_PWM_dutycycle(self._gpioNumber, dutyCycle)
                if self._dev.pluginProps['momentary']:
                    sleep(float(self._dev.pluginProps['turnOffDelay']))
                    self._write(0)
        else:
            L.warning('"%s" invalid output value %s; write ignored',
                      self._dev.name, value)

    # Public instance method:

    def updateInterruptDevices(self, intDevId, add=True):
        """
        Add/remove an interrupt device id to/from the internal interrupt
        devices list in current device.  If add is True, add the device to the
        list, and if add is False remove it from the list.  Do not add a
        duplicate interrupt device id to the list, and do not attempt to remove
        one that is not already in the list.  Log any add/remove actions and
        the resulting interrupt devices list for debug.
        """

        # Check for a non-integer argument... yes, it has happened... I don't
        # know why.  Remove the following code segment once the source of the
        # non-integer intDevId's is located and fixed.

        if not isinstance(intDevId, int):  # Is in intDevId an integer?
            intDevId = int(intDevId)  # No, make it one.
            intDev = indigo.devices[intDevId]
            L.warning('"%s" updateInterruptDevices intDevId argument is not '
                      'an integer %s', intDev.name, intDevId)

        # Add/remove the interrupt device id.

        inList = intDevId in self._interruptDevices
        if add ^ inList:  # (add and not inlist) or (not add and inList)
            self._interruptDevices.append(intDevId) if add \
                else self._interruptDevices.remove(intDevId)
            LD.digital('"%s" interrupt devices list updated %s%s',
                       self._dev.name, ('-', '+')[add], intDevId)
            LD.digital(self._interruptDevices)
