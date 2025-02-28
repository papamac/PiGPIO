# coding=utf-8
"""
###############################################################################
#                                                                             #
#                            Pi GPIO Indigo Plugin                            #
#                             MODULE ioDevices.py                             #
#                                                                             #
###############################################################################

  BUNDLE:  Raspberry Pi General Purpose Input/Output for Indigo
           (Pi GPIO.indigoPlugin)
  MODULE:  ioDevices.py
   TITLE:  Pi GPIO io device management
FUNCTION:  ioDevices.py provides classes to define and manage six types
           of Pi GPIO devices.
   USAGE:  ioDevices.py is included by the primary plugin module,
           plugin.py.  Its methods are called as needed by plugin.py methods.
  AUTHOR:  papamac
 VERSION:  0.10.1
    DATE:  March 25, 2024

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

MODULE ioDevices.py DESCRIPTION:

The ioDevices module contains the global data structures, module level
functions, and classes that define the detailed behavior of all the io devices
currently supported by the plugin.  The primary IoDevice class is an abstract
base class that provides common methods that are used by all subclasses.  Six
subclasses, ADC12, ADC18, DAC12, DockerPiRelay, IoExpander, and PiGPIO, contain
methods that are specific to a particular set of related io devices.

DEPENDENCIES/LIMITATIONS:

The classes and methods in the pigpioDevices module depend on the rgpio Python
library and the corresponding rgpio daemon running on the Raspberry Pi.  Both
of these were written by joan2937, et al. and are available in joan's lg
repository on GitHub (gitHub.com/joan2937/lg).  The current version is v0.2.2
released on May 3,2023.  The rgpio Python library is included in the plugin
bundle as the module rgpio.py.  The rgpio daemon is available for installation
in the current Raspberry Pi OS distribution based on Debian bookworm.

CHANGE LOG:

Major changes to the Pi GPIO plugin are described in the CHANGES.md file in the
top level bundle directory.  Changes of lesser importance may be described in
individual module docstrings if appropriate.

Note 2/25/2024: Some of the following descriptions may seem confusing because
the original module used joan2937's pigpio.py library and the pigpio daemon.
These were not upgraded to support the Raspberry Pi 5 and were replaced by
papamac in v0.10.0 with their lg archive equivalents, rgpio.py and the rgpio
daemon.  The historical record both here and in CHANGES.md retain references to
the original pigpio software.

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
v0.5.8   9/11/2022  Add support for Docker Pi Relay devices and 8/10-bit dac's.
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
                    IoExpander devices.
                    (2) Change spi integrity check for ADC12 devices.  Use an
                    absolute change in the digital code on consecutive readings
                    to indicate failure rather than a percentage change in
                    consecutive voltage measurements.
                    (3) Refactor hardware interrupt relay management.  In the
                    IoExpander class, dynamically add and remove the interrupt
                    devices in response to ConfigUi changes.  In the PiGPIO
                    class, include add and remove methods that are invoked by
                    IoExpander.  Add a deviceDeleted method to the IoDevice
                    class to remove interrupt devices that were deleted.
                    (4) Change spi bitRate units from kb/s to Mb/s.
v0.9.0    6/8/2023  Refactor ioDevices.py and plugin.py to reduce the
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
v0.10.0  2/25/2024  (1) Replace pigpio.py with rgpio.py to accommodate changes
                    in Raspberry Pi 5.
                    (2) Update the files and wiki.
v0.10.1  3/25/2024  (1) Refactor a key filename and class name to be consistent
                    with the change from pigpio to rgpio: pigpioDevices.py
                    becomes ioDevices.py and class PiGPIODevice becomes class
                    IoDevice.
                    (2) Update the files and wiki.
                    (3) Divide class IoDevice into parts separated by banner
                    comments for readability.
                    (4) Update ioDevices.py comments and docstrings.
v0.10.2   4/1/2024  Update the wiki in preparation for the initial release.
v1.0.0   4/15/2024  Initial GitHub release.
"""
###############################################################################
#                                                                             #
#                   DUNDERS, IMPORTS, and GLOBAL CONSTANTS                    #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '0.10.1'
__date__ = '3/25/2024'

import indigo

from abc import ABC, abstractmethod
from datetime import datetime
from logging import getLogger
import time

from conditionalLogging import LD, LI
import rgpio

# General global constants:

L = getLogger("Plugin")  # Standard Plugin logger.
ON_OFF = ('off', 'on')   # onOffState text values.

# Global dictionary of io device class names keyed by io device type:
# IO_DEV_CLASS[ioDevType] = ioDevClass

IO_DEV_CLASS = {
    'dkrPiRly': 'DockerPiRelay',
    'MCP23008': 'IoExpander',     'MCP23017': 'IoExpander',
    'MCP23S08': 'IoExpander',     'MCP23S17': 'IoExpander',
    'MCP3202':  'ADC12',          'MCP3204':  'ADC12',
    'MCP3208':  'ADC12',
    'MCP3422':  'ADC18',          'MCP3423':  'ADC18',
    'MCP3424':  'ADC18',
    'MCP4801':  'DAC12',          'MCP4802':  'DAC12',
    'MCP4811':  'DAC12',          'MCP4812':  'DAC12',
    'MCP4821':  'DAC12',          'MCP4822':  'DAC12',
    'pigpio':   'PiGPIO'}

# gpio chip numbers keyed by the Raspberry Pi model name.

GPIO_CHIP = {
    'Raspberry Pi 4 Model B':         0,
    'Raspberry Pi 5 Model B':         4,
    'Raspberry Pi Compute Module 4':  0,
    'Raspberry Pi Zero 2 W':          0}

###############################################################################
#                                                                             #
#                        GLOBAL INTERNAL DICTIONARIES                         #
#                                                                             #
###############################################################################

# Prior trigger data that are used to limit frequent event triggers keyed by
# the event name:

_priorTriggerTime = {}
_limitTriggers = {}

# io device instance objects keyed by device id:
# _ioDevices[dev.id] = <io device instance object>

_ioDevices = {}

# Shared rgpiod resources that are used by multiple io devices keyed by the
# resource id:

_resources = {}


###############################################################################
#                                                                             #
#                          INTERNAL MODULE FUNCTIONS                          #
#                                                                             #
# def _executeEventTriggers(dev, eventType, eventName, description='')        #
# def _pigpioError(dev, errorType, errorMessage)                              #
#                                                                             #
###############################################################################

def _executeEventTriggers(dev, eventType, eventName, description='',
                          limitTriggers=False):
    """
    Conditionally execute all Indigo triggers for an eventType/eventName.  If
    a named event occurs at a frequency greater than 1 per second, limit the
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
    _ioDevices[dev.id].stop()


###############################################################################
#                                                                             #
#                           PUBLIC MODULE FUNCTIONS                           #
#                                                                             #
# def getIoDev(dev, new=False)                                                #
# def getRpiModel(connection)                                                 #
# def logStartupSummary()                                                     #
# def logShutdownSummary()                                                    #
#                                                                             #
###############################################################################

def getIoDev(dev, new=False):
    """
    Find or create a unique io device object (an instance of a IoDevice
    subclass) for a Pi GPIO plugin device.  Return the object to the caller or
    return None if there is no device available.

    If an io device exists in the internal _ioDevices dictionary, return it.

    If there is no existing object and new=False, assume that the object should
    be available but is missing.  Return None and do not create a new instance.
    new=False calls are used to access io device methods after PiGPIO device
    startup (e.g., getIoDev(dev).read()).

    If there is no existing object and new=True, instantiate a new io device
    object using the PiGPIO device properties.  If there are any startup
    exceptions, call _pigpioError and return None.  If startup succeeds, save
    the newly instantiated io device object in the io devices dictionary and
    return it to the caller.  new=True calls are used when the caller wishes
    to create a new io device (e.g., in the deviceStartComm method, or __init__
    methods for other io devices).
    """
    ioDev = _ioDevices.get(dev.id)  # Get existing io device, if available.

    if new:  # Create and return a new io device object.
        if not ioDev:  # Proceed only if no existing io device.

            # Get the io device class from the IO_DEV_CLASS dictionary.

            ioDevType = dev.pluginProps['ioDevType']
            ioDevClass = IO_DEV_CLASS[ioDevType]

            # Create and start a new instance of the device class.

            try:
                ioDev = globals()[ioDevClass](dev)
            except ConnectionError as errorMessage:
                _pigpioError(dev, 'conn', errorMessage)
            except Exception as errorMessage:
                _pigpioError(dev, 'start', errorMessage)
            else:  # No startup exceptions; complete io device startup.
                LI.startStop('"%s" started as a %s on %s',  # Log it.
                             dev.name, dev.deviceTypeId, dev.address)
                dev.setErrorStateOnServer(None)  # Clear any device errors.
                ioDev.start()

    return ioDev if ioDev and ioDev.running() else None


def getRpiModel(connection):
    """
    Read the '/proc/cpuinfo' file from a connected pi and parse the file to
    extract the rpi model name.  This model name is used to look up the rpi
    gpioChip number in the global GPIO_CHIP dictionary.
    """
    model = None
    if connection.connected:
        rgpio.exceptions = False
        cpuInfo = connection.file_open('/proc/cpuinfo', rgpio.FILE_READ)
        if cpuInfo >= 0:
            nb, bytes_ = connection.file_read(cpuInfo, 2000)
            connection.file_close(cpuInfo)
            if nb > 0:
                b1 = bytes_.find(b'Model\t\t: ')
                b2 = bytes_.find(b' Rev ')
                if b1 != -1 and b2 != -1:
                    model = str(bytes_[b1 + 9:b2], encoding='utf-8',
                                errors='strict')
        rgpio.exceptions = True
    return model


def logStartupSummary():
    """
    Log the number of io devices started and the number of rgpiod resources
    used.
    """
    L.info('%s io devices started using %s rgpiod resources',
           len(_ioDevices), len(_resources))


def logShutdownSummary():
    """ Log the io device and resource status at shutdown. """
    if _ioDevices:
        L.warning('%s io devices still active at shutdown',
                  len(_ioDevices))
    else:
        L.info('All io devices stopped')

    if _resources:
        L.warning('%s rgpiod resources still reserved at shutdown',
                  len(_resources))
    else:
        L.info('All rgpiod resources stopped/closed')


###############################################################################
#                                                                             #
#                               CLASS IoDevice                                #
#                                                                             #
###############################################################################

class IoDevice(ABC):
    """
    IoDevice is an abstract base class (ABC) that is used in defining all six
    of the io device subclasses.  It defines a number of internal and public
    methods that are common to all the subclasses.  These methods define the
    common io device behavior:

                      COMMON INSTANCE INITIALIZATION METHOD

    __init__                  Initializes common instance io device attributes
                              and connects to the rgpio daemon.

                            RESOURCE MANAGEMENT METHODS

    _getConnection            Creates/reserves a connection to the rgpio daemon
                              for the io device.
    _getGpioHandle            Opens/reserves a handle to access a built-in GPIO
                              chip set.
    _getI2cHandle             Opens/reserves a handle to access an i2c device.
    _getSpiHandle             Opens/reserves a handle to access a spi device.
    _releaseConnection        Releases/stops a connection.
    _releaseHandle            Releases/closes a gpio, i2c, or spi handle.

                       STATE MANAGEMENT/PROCESSING METHODS

    _updateOnOffState         Updates the device onOffState on the Indigo
                              server.
    _updateSensorValueStates  Updates device sensor value states on the Indigo
                              server and processes sensor values.

                                 ABSTRACT METHODS

    _read                     Abstract _read method to be overridden in each
                              subclass.
    _write                    Abstract _write method to be overridden in each
                              subclass, even if the subclass device is read
                              only.

                               COMMON PUBLIC METHODS

    read                      Calls the subclass _read method to read the io
                              device.
    write                     Calls the subclass _write method to write to the
                              io device.
    poll                      Called by the runConcurrentThread method in
                              plugin.py to read io devices (poll them) at a
                              unique rate for each device.
    start                     Starts the io device by signaling that all
                              startup functions have completed successfully and
                              the device is running.
    running                   Returns the io device running status.
    stop                      Stops an io device and releases its reserved
                              resources.

    The internal resource/state management methods listed above are used by the
    six subclasses to address io devices and record/process the results of io
    device operations.  The _read and _write abstract methods must be
    overridden by each subclass with unique methods that actually perform the
    detailed io operations using rgpio library calls.

    The public methods are called by Plugin object methods in plugin.py to
    initiate io device operations and to stop/close the device.

    All six of the io device subclasses follow the following model:

    class Device(IoDevice):

        def __init__(self, dev):  # Constructor method.
            IoDevice.__init__(self, dev)  # Common initialization.
            self._h, self._hId = self._getXXXXHandle()  # Get the handle/hId.
            ... unique initialization for the io device.

        def ... unique internal methods, if needed, to support the _read and
            _write methods.

        def _read(self):  # Implementation of abstract _read method.
            ... unique code and rgpio library calls to read an io device.

        def _write(self, value):  # Implementation of abstract _write method.
            ... unique code and rgpio library calls to write to an io device.

        def ... unique public methods, if needed, to manage callbacks and
                relay/service interrupts.
    """
    ###########################################################################
    #                                                                         #
    #                             CLASS IoDevice                              #
    #                                   PART                                  #
    #                                                                         #
    #                                   III                                   #
    #                                    I                                    #
    #                                    I                                    #
    #                                    I                                    #
    #                                    I                                    #
    #                                   III                                   #
    #                                                                         #
    #                      CLASS ATTRIBUTES AND METHODS                       #
    #                                                                         #
    # def _getDev(devName)                                                    #
    # def _hexStr(byteList)                                                   #
    #                                                                         #
    #                 COMMON INSTANCE INITIALIZATION METHOD                   #
    #                                                                         #
    # def __init__(self, dev)                                                 #
    #                                                                         #
    ###########################################################################

    I2CBUS = 1  # Primary i2c bus.
    SPIBUS = 0  # Primary spi bus.
    IMAGE_SEL = (indigo.kStateImageSel.SensorOff,  # Sensor off/on image sel.
                 indigo.kStateImageSel.SensorOn)

    @classmethod
    def _getDev(cls, devName):
        """
        Lookup a device name the Indigo devices database.  If the device is in
        the database, and is both configured and enabled, return the device
        object.  Otherwise, return None.  This function is a stronger form of
        the usual indigo.devices.get(devName) that ensures that the device not
        only exists, but is available to use.
        """
        dev = indigo.devices.get(devName)
        if dev:
            if dev.configured and dev.enabled:
                return dev

    @classmethod
    def _hexStr(cls, byteList):
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

    def __init__(self, dev):
        """
        Add the new io device object to the io devices dictionary, initialize
        common internal instance attributes, and connect to the rgpio daemon.
        Set a common Indigo home window state image for all io devices.
        """

        # Add the io device instance object to the internal _ioDevices
        # dictionary.  This makes the io device immediately available to the
        # stop method in case there are startup exceptions.

        _ioDevices[dev.id] = self

        # Initialize common internal instance attributes:

        self._dev = dev          # Indigo device reference.
        self._running = False    # Startup completed satisfactorily.
        self._c = None           # rgpiod connection object.
        self._h = None           # gpio, i2c or spi handle.
        self._hId = None         # gpio, i2c or spi handle id.
        self._callbackId = None  # gpio callback identification object.
        self._pollCount = 0      # Poll count for polling status monitoring.
        self._lastPoll = self._lastStatus = indigo.server.getTime()

        # Connect to the rgpio daemon and set internal connection attributes
        # for use by all subclass methods.

        self._c, self._cId = self._getConnection()

        # Set the initial device state image to override power icon defaults
        # for digital output devices.

        onOffState = dev.states['onOffState']
        dev.updateStateImageOnServer(self.IMAGE_SEL[onOffState])

    ###########################################################################
    #                                                                         #
    #                             CLASS IoDevice                              #
    #                                   PART                                  #
    #                                                                         #
    #                                III   III                                #
    #                                 I     I                                 #
    #                                 I     I                                 #
    #                                 I     I                                 #
    #                                 I     I                                 #
    #                                III   III                                #
    #                                                                         #
    #                       RESOURCE MANAGEMENT METHODS                       #
    #                                                                         #
    # def _getConnection(self)                                                #
    # def _getGpioHandle(self)                                                #
    # def _getI2cHandle(self)                                                 #
    # def _getSpiHandle(self)                                                 #
    # def _releaseConnection(self)                                            #
    # def _releaseHandle(self)                                                #
    #                                                                         #
    ###########################################################################
    """
    The rgpio daemon (rgpiod), running on one or more pi hosts, performs
    detailed bit oriented io operations as directed by method calls from the
    rgpio library.  Each rgpiod instance reserves a limited local resource in
    the form of an integer "handle" when an io device is started.  A handle can
    be reserved for a single io device, or in most cases, it can be shared by
    multiple related devices.  For example, an MCP3423 i2c 4-channel ADC can
    reserve 4 handles (one for each channel/device), or a single handle with
    the common i2c address can be used for all four devices.  Since each rgpiod
    instance has a limited number of handles that it can assign, it is clearly
    beneficial to share handles whenever possible.  The purpose of the resource
    management methods is to ensure that rgpiod resources are utilized
    efficiently as io devices are dynamically started and stopped.
    
    The ioDevices module contains a global resources dictionary (_resources)
    that contains a resource and its use count for all active resources.  It 
    is keyed by a resource id that uniquely describes a set of devices that can
    share the resource on a particular pi.  Using the above example, the handle
    id for the four channel ADC must contain the the pi's host id or address/
    port and the ADC chip's i2c address.  When the first io device (e.g.
    channel 1) is started, an i2c handel id is created, an i2c handel is opened
    in rgpiod, and the handle with a use count of 1 is saved in the resources
    dictionary keyed by the handel id.  Starting a second device will generate
    the same handle id which can be used to get the handle from the resources
    dictionary without opening a new one.  The use count must, of course, be
    incremented to record the sharing.  Stopping a device will decrement the
    use count and eventually close the handle when the count becomes 0.  This
    releases the handle back to rgpiod where it can be opened for a different
    io device if needed.
    
    The _get... and _release... methods in this section generalize the basic
    resource management approach described above to apply to four types of
    resources:
    
    (1) A CONNECTION OBJECT identifies a connection to a specific rgpio daemon
    running on a specific pi host.  Connection objects are used to invoke
    instance methods in the rgpio library to perform all input/output
    operations on individual GPIO pins, i2c devices, and spi devices.
    A CONNECTION ID includes a host id, or alternatively, the pi's address and
    rgpiod port number.
    
    (2) A GPIO HANDLE is an integer that identifies a specific GPIO chip set
    on a specific pi host.  rgpio library methods use the gpio handle to direct
    input/output operations to the desired GPIO chip set.  At the current time,
    Raspberry Pis use only one GPIO chip set, but this could change in the
    future.
    A GPIO HANDLE ID includes the connection id to identify its pi host/rgpiod
    instance, text to identify it as a gpio handle, and the GPIO chip number.
    
    (3) An I2C HANDLE is an integer that identifies a specific i2c device on
    a specific pi host.  rgpio library methods use the i2c handle to direct
    input/output operations to the desired i2c device.
    An I2C HANDLE ID includes the connection id to identify its pi host/rgpiod
    instance, text to identify it as a i2c handle, and the i2c device address. 
    
    (4) An SPI HANDLE is an integer that identifies a specific spi channel,
    using a specific input/output data rate, on a specific pi host. rgpio
    library methods use the spi handle to direct input/output operations to the
    desired spi channel/device.
    An SPI HANDLE ID includes the connection id to identify its pi host/rgpiod
    instance, text to identify it as a spi handle, the spi channel number, and
    the input/output bit rate.
    
    Every io device instance must have a connection object attribute to
    identify its pi host/rgpiod instance.  The IoDevice.__init__ method calls
    the self._getConnection method to get a connection object and its id.  For
    convenient access in later code, these are assigned to the instance
    attributes self._c and self._cId.
    
    Similarly, every io device instance must also have a handle attribute to
    identify a specific GPIO chip set or i2c/spi destination for its input/
    output operations.  The IoDevice subclass constructor (SubClass.__init__)
    calls the self._get....Handle method to get a gpio, i2c, or spi handle
    depending on the io device type.  The handle and its id are assigned to the
    self._h and self._hId instance attributes for later reference.
    
    The stop public instance method is called to terminate an io device's
    operations and release its resources. To release resources it calls the
    self._releaseConnection and self._releaseHandel methods.
    """

    def _getConnection(self):
        """
        Get a connection object for the io device and update the resources
        dictionary:

        Create a connection id using the host id, host address, and port number
        from the Indigo device pluginProps.  Get the connection tuple
        (connection object, use count, and gpioChip) for this id, if available,
        from the resources dictionary.

        If no connection exists, use the rgpio.sbc module function to create a
        new one.  If successful, use the getRpiModel module function to get the
        model of the connected pi and look up the gpioChip for that model.  If
        the connection, model access, or the gpioChip lookup fails, raise a
        ConnectionError exception.

        Reserve the existing or new connection by incrementing its use count
        and updating/adding its connection tuple in the resources dictionary.
        Log the connection usage for debug and return the connection and its
        id.
        """
        hostId = self._dev.pluginProps['hostId']
        hostAddress = self._dev.pluginProps['hostAddress']
        portNumber = self._dev.pluginProps['portNumber']
        connectionId = (hostId if hostId and portNumber == '8889'
                        else hostAddress + ':' + portNumber)
        connection, useCount, gpioChip = _resources.get(connectionId,
                                                        (None, 0, None))

        if not connection:  # No existing connection; create a new one.
            LD.resource('"%s" connecting to %s', self._dev.name, connectionId)
            connection = rgpio.sbc(hostAddress, int(portNumber))
            if not connection.connected:  # Connection failed.
                connection.stop()  # Release any rgpiod resources immediately.
                raise ConnectionError('connection failed')
            model = getRpiModel(connection)
            if not model:
                connection.stop()  # Release any rgpiod resources immediately.
                raise ConnectionError('rpi model info not found')
            LD.startStop('"%s" model = %s', self._dev.name, model)
            gpioChip = GPIO_CHIP.get(model)
            if gpioChip is None:
                connection.stop()  # Release any rgpiod resources immediately.
                raise ConnectionError('gpio chip number not found')
            LD.startStop('"%s" gpioChip = %s', self._dev.name, gpioChip)

        useCount += 1  # Reserve the connection for this io device.
        _resources[connectionId] = connection, useCount, gpioChip
        LD.resource('"%s" using connection %s(%s)',
                    self._dev.name, connectionId, useCount)
        return connection, connectionId

    def _getGpioHandle(self):
        """
        Get a gpio handle for the io device and update the resources
        dictionary:

        Append '.gpio.' and the gpioChip number to the connection id to create
        a gpio handle id for this connection and chip set.  Get the resource
        tuple (gpio handle, use count) for this id, if available, from the
        resources dictionary.  If no handle exists, use the rgpio library
        method gpiochip_open to open a new one.

        Reserve the existing or new handle by incrementing its use count and
        updating/adding the resource tuple in the dictionary.  Log the
        handle usage for debug and return the handle and its id.
        """
        prefix = self._cId + '.gpio'
        gpioChip = _resources[self._cId][2]  # Get gpioChip from _resources.
        handleId = prefix + '.' + str(gpioChip)

        handle, useCount = _resources.get(handleId, (None, 0))
        if handle is None:  # No existing gpio handle; open a new one.
            LD.resource('"%s" opening new handle id %s',
                        self._dev.name, handleId)
            handle = self._c.gpiochip_open(gpioChip)

        useCount += 1  # Reserve the handle for this io device.
        _resources[handleId] = handle, useCount
        LD.resource('"%s" using handle %s%s(%s)',
                    self._dev.name, prefix, handle, useCount)
        return handle, handleId

    def _getI2cHandle(self):
        """
        Get an i2c handle for the io device and update the resources
        dictionary:

        Append '.i2c' and the i2c device address (in hex) to the connection id
        to create an i2c handle id for this connection and device.  Get the
        resource tuple (i2c handle, use count) for this id, if available, from
        the resources dictionary.  If no handle exists, use the rgpio library
        method i2c_open to open a new one.

        Reserve the existing or new handle by incrementing its use count and
        updating/adding the resource tuple in the dictionary.  Log the
        handle usage for debug and return the handle and its id.
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
        Get a spi handle for the io device and update the resources dictionary:

        Append '.spi', the spi channel, and the input/output bit rate to the
        connection id to create a spi handle id for this connection and device.
        Get the resource tuple (spi handle, use count) for this id, if
        available, from the resources dictionary.  If no handle exists, use the
        rgpio library method spi_open to open a new one.

        Reserve the existing or new handle by incrementing its use count and
        updating/adding the resource tuple in the dictionary.  Log the
        handle usage for debug and return the handle and its id.
        """
        prefix = self._cId + '.spi'
        spiChannel = self._dev.pluginProps['spiChannel']
        bitRate = int(500000 * float(self._dev.pluginProps['bitRate']))
        handleId = prefix + '.' + spiChannel + '.' + str(bitRate)

        handle, useCount = _resources.get(handleId, (None, 0))
        if handle is None:  # No existing spi handle; open a new one.
            LD.resource('"%s" opening new handle id %s',
                        self._dev.name, handleId)
            handle = self._c.spi_open(0, int(spiChannel), bitRate,
                                      self.SPIBUS << 8)

        useCount += 1  # Reserve the handle for this io device.
        _resources[handleId] = handle, useCount
        LD.resource('"%s" using handle %s%s(%s)',
                    self._dev.name, prefix, handle, useCount)
        return handle, handleId

    def _releaseConnection(self):
        """
        Release/stop the connection for the io device and update the resources
        dictionary:

        Use the connection id (self._cId) to get the connection object and use
        count for this io device from the resources dictionary.  Decrement the
        use count and update the dictionary to release the connection.  If the
        use count is zero, delete the connection from the dictionary and stop
        it to release any allocated resources within the rgpio daemon.
        """
        connection, useCount, gpioChip = _resources[self._cId]
        useCount -= 1
        LD.resource('"%s" releasing connection %s(%s)',
                    self._dev.name, self._cId, useCount)
        _resources[self._cId] = connection, useCount, gpioChip
        if not useCount:
            LD.resource('"%s" stopping connection to %s',
                        self._dev.name, self._cId)
            del _resources[self._cId]
            connection.stop()

    def _releaseHandle(self):
        """
        Release/close the handle for the io device and update the resources
        dictionary:

        Use the handle id (self._hId) to get the handle and use count for this
        io device from the resources dictionary.  Decrement the use count and
        update the dictionary to release the handle from this io device.  If
        the use count is zero, delete the handle from the dictionary and close
        it to return it to the rgpio daemon for reuse.
        """
        handle, useCount = _resources[self._hId]
        useCount -= 1
        hSplit = self._hId.split('.')
        hName = hSplit[0] + '.' + hSplit[1] + str(handle)
        LD.resource('"%s" releasing handle %s(%s)',
                    self._dev.name, hName, useCount)
        _resources[self._hId] = handle, useCount
        if not useCount:
            del _resources[self._hId]
            LD.resource('"%s" closing handle %s', self._dev.name, hName)
            if hSplit[1] == 'gpio':
                self._c.gpiochip_close(handle)
            elif hSplit[1] == 'i2c':
                self._c.i2c_close(handle)
            elif hSplit[1] == 'spi':
                self._c.spi_close(handle)

    ###########################################################################
    #                                                                         #
    #                             CLASS IoDevice                              #
    #                                   PART                                  #
    #                                                                         #
    #                             III   III   III                             #
    #                              I     I     I                              #
    #                              I     I     I                              #
    #                              I     I     I                              #
    #                              I     I     I                              #
    #                             III   III   III                             #
    #                                                                         #
    #                  STATE MANAGEMENT/PROCESSING METHODS                    #
    #                                                                         #
    # def _updateOnOffState(self, onOffState, sensorUiValue=None, logAll=True)#
    # def _updateSensorValueStates(self, voltage, logAll=True)                #
    #                                                                         #
    ###########################################################################

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
        def _uiValue(value):
            """
            Generate a formatted text uiValue, consisting of a floating point
            value and units, for use in the state display and limit fault
            messages.
            """
            magnitude = abs(value)
            if magnitude < 10:
                uiFormat = '%.2f %s'  # uiValue format for small value.
            elif magnitude < 100:
                uiFormat = '%.1f %s'  # uiValue format for medium value.
            else:
                uiFormat = '%i %s'  # uiValue format for large value.
            return uiFormat % (value, units)

        priorSensorValue = self._dev.states['sensorValue']  # Save prior value.

        # Compute the new sensorValue and uiValue from the ADC / DAC voltage
        # and update the states on the server.

        scalingFactor = float(self._dev.pluginProps['scalingFactor'])
        sensorValue = voltage * scalingFactor
        units = self._dev.pluginProps['units']
        sensorUiValue = _uiValue(sensorValue)
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
                uiLimit = _uiValue(float(lowLimit))
                description = '%s < %s' % (sensorUiValue, uiLimit)
                L.warning('"%s" low limit fault: %s < %s',
                          self._dev.name, sensorUiValue, uiLimit)
            else:  # highLimitFault
                triggerEvent = 'high limit fault'
                uiLimit = _uiValue(float(highLimit))
                description = '%s > %s' % (sensorUiValue, uiLimit)
            L.warning('"%s" %s: %s', self._dev.name, triggerEvent, description)

            # Execute a limit fault trigger only if it is a new limit fault.

            if not priorLimitFault:
                _executeEventTriggers(self._dev, 'limitFault', triggerEvent)

    ###########################################################################
    #                                                                         #
    #                             CLASS IoDevice                              #
    #                                   PART                                  #
    #                                                                         #
    #                             III   III     III                           #
    #                              I     I       I                            #
    #                              I      I     I                             #
    #                              I       I   I                              #
    #                              I        I I                               #
    #                             III       III                               #
    #                                                                         #
    #                            ABSTRACT METHODS                             #
    #                                                                         #
    # def _read(self, logAll=True)                                            #
    # def _write(self, value)                                                 #
    #                                                                         #
    ###########################################################################

    @abstractmethod
    def _read(self, logAll=True):
        """ Standard internal read method for all subclasses. """
        pass

    @abstractmethod
    def _write(self, value):
        """ Standard internal write method for all subclasses. """
        pass

    ###########################################################################
    #                                                                         #
    #                             CLASS IoDevice                              #
    #                                   PART                                  #
    #                                                                         #
    #                               III      III                              #
    #                                I        I                               #
    #                                 I     I                                 #
    #                                  I   I                                  #
    #                                   I I                                   #
    #                                   III                                   #
    #                                                                         #
    #                          COMMON PUBLIC METHODS                          #
    #                                                                         #
    # def read(self, logAll=True)                                             #
    # def write(self, value)                                                  #
    # def poll(self)                                                          #
    # def start(self)                                                         #
    # def running(self)                                                       #
    # def stop(self)                                                          #
    #                                                                         #
    ###########################################################################

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

    def start(self):
        """
        Start the io device by setting the self._running attribute.  This
        indicates that all startup functions have been successfully completed
        and the device is running.
        """
        self._running = True

    def running(self):
        """
        Return the io device running status.
        """
        return self._running

    def stop(self):
        """
        Stop the io device by removing it from the io devices dictionary
        and the interrupt devices list in the linked interrupt relay GPIO
        device (if applicable).  Cancel any gpio callback and release/close/
        stop any rgpio daemon shared resources.
        """
        try:
            # Remove the io device from the io devices dictionary.

            del _ioDevices[self._dev.id]

            # Check to see if the io device is an interrupt device.  If so,
            # remove it from the interrupt devices list in the interrupt relay
            # GPIO device.

            if 'hardwareInterrupt' in self._dev.pluginProps:  # Interrupt dev.
                interruptRelayGPIO = self._dev.pluginProps[
                    'interruptRelayGPIO']
                interruptRelayDev = self._getDev(interruptRelayGPIO)
                if interruptRelayDev:  # Device available?
                    rioDev = getIoDev(interruptRelayDev)
                    if rioDev:
                        LD.digital('"%s" removing interrupt device id from '
                                   '"%s"', self._dev.name, interruptRelayGPIO)
                        rioDev.updateInterruptDevices(self._dev.id, add=False)

            # Cancel the gpio callback, if any.

            if self._callbackId:
                self._callbackId.cancel()

            # Release/close/stop rgpiod shared resources.

            if self._c:  # Proceed only if the instance is connected.
                self._releaseHandle()
                self._releaseConnection()

        except Exception as errorMessage:

            # Stop exceptions often follow another Pi GPIO exception/error
            # because the device is stopped and the error often interferes
            # with the release of pigpiod resources.  Log a warning message,
            # but do not call_pigpioError and trigger another event.

            L.warning('"%s" stop error: %s', self._dev.name, errorMessage)

        # Log successful stop completion.

        LI.startStop('"%s" stopped', self._dev.name)


###############################################################################
#                                                                             #
#                                 CLASS ADC12                                 #
#                                                                             #
#                             CONSTRUCTOR METHOD                              #
#                                                                             #
# def __init__(self, dev)                                                     #
#                                                                             #
#                     IMPLEMENTATION OF ABSTRACT METHODS                      #
#                                                                             #
# def _read(self, logAll=True)                                                #
# def _write(self, value)                                                     #
#                                                                             #
###############################################################################

class ADC12(IoDevice):
    """
    Read data from the 12-bit ADC devices MCP3202, MCP3204, and MCP3208 using
    the rgpio library spi methods.  Update the states in the Indigo device.
    Implement device operation instructions and spi communications protocols
    from the following hardware references:
    MCP3202:   <https://ww1.microchip.com/downloads/en/DeviceDoc/21034F.pdf>
    MCP3204/8: <https://ww1.microchip.com/downloads/en/devicedoc/21298e.pdf>
    Check the spi read integrity if requested in the pluginProps.
    """
    def __init__(self, dev):
        """
        Initialize common and unique instance attributes for ADC12 devices.
        """
        IoDevice.__init__(self, dev)  # Common initialization.
        self._h, self._hId = self._getSpiHandle()  # spi interface.

        # Assemble data configuration tuple.

        inputConfiguration = int(dev.pluginProps['inputConfiguration'])
        adcChannel = int(self._dev.pluginProps['adcChannel'])
        self._data = (0x04 | inputConfiguration << 1 | adcChannel >> 2,
                      (adcChannel << 6) & 0xff, 0)
        if self._dev.pluginProps['ioDevType'] == 'MCP3202':
            self._data = (0x01, inputConfiguration << 7 | adcChannel << 6, 0)

    def _read(self, logAll=True):
        """
        Read the ADC output code.  Check the spi integrity, if requested, by
        reading it a second time and comparing the results.  Log a warning
        message if the values differ by more than 10 counts.  Convert the
        counts to a voltage and perform common sensor value processing, state
        updating, and logging.
        """
        def _readADCOutputCode():
            """
            Read and return a single 12-bit ADC output code (0-4095).
            """
            nBytes, bytes_ = self._c.spi_xfer(self._h, self._data)
            code = (bytes_[1] & 0x0f) << 8 | bytes_[2]
            LD.analog('"%s" read %s | %s | %s | %s',
                      self._dev.name, self._hexStr(self._data), nBytes,
                      self._hexStr(bytes_), code)
            return code

        counts = _readADCOutputCode()
        if self._dev.pluginProps['checkSPI']:  # Check spi integrity.
            counts_ = _readADCOutputCode()
            if abs(counts - counts_) > 10:
                L.warning('"%s" spi check: different values on consecutive '
                          'reads %s %s', self._dev.name, counts, counts_)
            counts = counts_

        referenceVoltage = float(self._dev.pluginProps['referenceVoltage'])
        voltage = referenceVoltage * counts / 4096
        self._updateSensorValueStates(voltage, logAll=logAll)

    def _write(self, value):
        """ Dummy method to allow writing to a read-only device. """
        pass


###############################################################################
#                                                                             #
#                                 CLASS ADC18                                 #
#                                                                             #
#                             CONSTRUCTOR METHOD                              #
#                                                                             #
# def __init__(self, dev)                                                     #
#                                                                             #
#                     IMPLEMENTATION OF ABSTRACT METHODS                      #
#                                                                             #
# def _read(self, logAll=True)                                                #
# def _write(self, value)                                                     #
#                                                                             #
###############################################################################

class ADC18(IoDevice):
    """
    Read data from the 18-bit ADC devices MCP3422, MCP3423, and MCP3424 using
    the rgpio library i2c methods.  Update the states in the Indigo device.
    Implement device operation instructions and i2c communications protocols
    from the following hardware reference:
    MCP3422/3/4: <https://ww1.microchip.com/downloads/en/devicedoc/22088c.pdf>
    Check the spi read integrity if requested in the pluginProps.
    """
    def __init__(self, dev):
        """
        Initialize common and unique instance attributes for ADC18 devices.
        """
        IoDevice.__init__(self, dev)  # Common initialization.
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

    def _read(self, logAll=True):
        """
        Start a conversion and then iteratively read the ADC until the
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
                  self._hexStr(bytes_), counts, voltage)
        self._updateSensorValueStates(voltage, logAll=logAll)

    def _write(self, value):
        """ Dummy method to allow writing to a read-only device. """
        pass


###############################################################################
#                                                                             #
#                                 CLASS DAC12                                 #
#                                                                             #
#                             CONSTRUCTOR METHOD                              #
#                                                                             #
# def __init__(self, dev)                                                     #
#                                                                             #
#                     IMPLEMENTATION OF ABSTRACT METHODS                      #
#                                                                             #
# def _read(self, logAll=True)                                                #
# def _write(self, value)                                                     #
#                                                                             #
###############################################################################

class DAC12(IoDevice):
    """
    Write data to the 8/10/12-bit DAC devices MCP4801, MCP4802, MCP4811,
    MCP4812, MCP4821, and MCP4822 using the rgpio library spi methods.  Update
    the states in the Indigo device.  Implement device operation instructions
    and spi communications protocols from the following hardware references.
    MCP4801/11/21: <https://ww1.microchip.com/downloads/en/DeviceDoc/22244B.pdf>
    MCP4802/12/22: <https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/20002249B.pdf>
    """
    def __init__(self, dev):
        """
        Initialize common and unique instance attributes for DAC12 devices.
        """
        IoDevice.__init__(self, dev)  # Common initialization.
        self._h, self._hId = self._getSpiHandle()  # spi interface.

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
                      inputCode, self._hexStr(data), nBytes)
        else:
            L.warning('"%s" converted input code %s is outside of DAC '
                      'range; write ignored', self._dev.name, inputCode)
            return

        # Update/log the sensor value states.

        self._updateSensorValueStates(voltage)


###############################################################################
#                                                                             #
#                             CLASS DockerPiRelay                             #
#                                                                             #
#                             CONSTRUCTOR METHOD                              #
#                                                                             #
# def __init__(self, dev)                                                     #
#                                                                             #
#                     IMPLEMENTATION OF ABSTRACT METHODS                      #
#                                                                             #
# def _read(self, logAll=True)                                                #
# def _write(self, value)                                                     #
#                                                                             #
###############################################################################

class DockerPiRelay(IoDevice):
    """
    Write a single bit value to a dkrPiRly device using the rgpio library i2c
    methods.  Update the onOffState in the Indigo device.  Implement device
    operation instructions and i2c communications protocols from the following
    hardware reference.

    <https://wiki.52pi.com/index.php?title=EP-0099>
    """
    def __init__(self, dev):
        """
        Initialize common and unique instance attributes for DockerPiRelay
        devices.
        """
        IoDevice.__init__(self, dev)  # Common initialization.
        self._h, self._hId = self._getI2cHandle()  # i2c interface.

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
                    time.sleep(float(self._dev.pluginProps['turnOffDelay']))
                    self._write(0)
        else:
            L.warning('"%s" invalid output value %s; write ignored',
                      self._dev.name, value)


###############################################################################
#                                                                             #
#                              CLASS IoExpander                               #
#                                                                             #
#                             CONSTRUCTOR METHOD                              #
#                                                                             #
# def __init__(self, dev)                                                     #
#                                                                             #
#                          INTERNAL INSTANCE METHODS                          #
#                                                                             #
# def _readSPIByte(self, register, data)                                      #
# def _readRegister(self, register)                                           #
# def _writeRegister(self, register, byte)                                    #
# def _updateRegister(self, register, bit)                                    #
#                                                                             #
#                     IMPLEMENTATION OF ABSTRACT METHODS                      #
#                                                                             #
# def _read(self, logAll=True)                                                #
# def _write(self, value)                                                     #
#                                                                             #
#                           PUBLIC INSTANCE METHODS                           #
#                                                                             #
# def interrupt(self):                                                        #
# def resetInterrupt(self)                                                    #
#                                                                             #
###############################################################################

class IoExpander(IoDevice):
    """
    Read and write bit values from/to the 8/16-bit IO Expander Devices
    MCP23008, MCP23S08, MCP23017 and MCP23S17 using the rgpio library i2c/spi
    methods.  Link devices requiring a hardware interrupt to interrupt relay
    gpio devices if requested.  Update the onOffState in the Indigo device.
    Implement device operation instructions and i2c/spi communications
    protocols from the following hardware references.
    MCP32008/S08: <https://ww1.microchip.com/downloads/en/DeviceDoc/21919e.pdf>
    MCP32017/S17: <https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf>
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
    """
    # The above addresses (except the last one) are for the MCP23X08 and the
    # MCP23X17 Port A in the BANK 1 register address mapping.  Port B addresses
    # add 0x10 to the corresponding Port A addresses.
    """
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

    def __init__(self, dev):
        """
        Initialize common instance attributes for IoExpander devices.  Get an
        i2c or spi handle for the device based on the io device type.
        Determine whether the device is to be used as a digital input or a
        digital output.  Initialize device registers and internal instance
        attributes for the intended use.  If the device is to be used with
        a hardware interrupt, manage the interrupt devices lists in prior and
        current interrupt relay GPIO devices.
        """
        IoDevice.__init__(self, dev)  # Common initialization.
        self._i2c = 'S' not in dev.pluginProps['ioDevType']
        self._h, self._hId = (self._getI2cHandle() if self._i2c else
                              self._getSpiHandle())

        # Define unique internal instance attributes.

        ioPort = dev.pluginProps['ioPort']
        self._offset = 0x10 if ioPort == 'b' else 0x00
        bitNumber = int(dev.pluginProps['bitNumber'])
        self._mask = 1 << bitNumber
        """"
        Configure the IOCON register with a common set of bits (BANK, SEQOP,
        and HAEN) that apply to all io devices that use the same hardware chip.
        Note that the IOCON register is written multiple times (once for each
        io device object), but it doesn't matter because the same value is
        written each time.

        The IOCON configuration is complicated by the fact that the internal
        register address mapping (BANK 0 or 1) is not known.  The following
        sequence of 2 writes addresses this problem.  It works for all MCP23XXX
        devices regardless of the initial configuration.  For details please
        see the appropriate MCP23XXX data sheets. These may be downloaded from:
        https://www.microchip.com/en-us/product/MCP230008
        https://www.microchip.com/en-us/product/MCP230017
        """
        iocon = self.BANK | self.SEQOP | self.HAEN | self.INTPOL

        self._writeRegister('IOCONB0', iocon)
        self._writeRegister('IOCON', iocon)

        """
        Configure the IODIR, IPOL, GPPU, DEFVAL, INTCON, and GPINTEN registers
        by setting the specific bit for this device (self._bitNum) in each
        register.  Leave all other bits unchanged. These configuration changes
        use the self._updateRegister method to read the register, change the
        appropriate bit, and then write it back.
        """
        # Set registers by device type:

        if dev.deviceTypeId == 'digitalOutput':
            self._updateRegister('IODIR', self.OUTPUT)
            self._updateRegister('GPINTEN', 0)  # No interrupt for output.

        elif dev.deviceTypeId == 'digitalInput':
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

                priorInterruptRelayDev = self._getDev(priorInterruptRelayGPIO)
                if priorInterruptRelayDev:  # Device available?
                    getIoDev(priorInterruptRelayDev) \
                        .updateInterruptDevices(dev.id, add=False)

            if interruptRelayGPIO:

                # Check interruptRelayGPIO device for validity and for relay
                # interrupts enabled.  If OK, add this device to the interrupt
                # devices list in the interruptRelayGPIO device.

                interruptRelayDev = self._getDev(interruptRelayGPIO)
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

    def _readSPIByte(self, register, control):
        """
        Read and return a single byte of data over the spi bus as directed by
        the spi control tuple.
        """
        nBytes, bytes_ = self._c.spi_xfer(self._h, control)
        LD.digital('"%s" readRegister %s %s | %s | %s', self._dev.name,
                   register, self._hexStr(control), nBytes,
                   self._hexStr(bytes_))
        return bytes_[-1]

    def _readRegister(self, register):
        """
        Read and return a single byte of data from the specified device
        register.  Use rgpio library methods for i2c or spi based on the
        device type.  For a spi operation, check the read integrity if
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
            byte = self._readSPIByte(register, control)

            if self._dev.pluginProps['checkSPI']:  # Check spi integrity.
                byte_ = self._readSPIByte(register, control)
                if byte != byte_:
                    L.warning('"%s" readRegister %s spi check: unequal '
                              'consecutive reads %02x %02x',
                              self._dev.name, register, byte, byte_)
                    byte = byte_
        return byte

    def _writeRegister(self, register, byte):
        """
        Write a single byte of data to the specified device register.  Use
        rgpio library methods for i2c or spi based on the device type.
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
                       self._dev.name, register, self._hexStr(control), nBytes)

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
                    time.sleep(float(self._dev.pluginProps['turnOffDelay']))
                    self._write(0)  # Turn it off.
        else:
            L.warning('"%s" invalid output value %s; write ignored',
                      self._dev.name, value)

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
#                             CONSTRUCTOR METHOD                              #
#                                                                             #
# def __init__(self, dev)                                                     #
#                                                                             #
#                          INTERNAL INSTANCE METHOD                           #
#                                                                             #
# def _callback(self, gpioNumber, pinBit, tic)                                #
#                                                                             #
#                     IMPLEMENTATION OF ABSTRACT METHODS                      #
#                                                                             #
# def _read(self, logAll=True)                                                #
# def _write(self, value)                                                     #
#                                                                             #
#                           PUBLIC INSTANCE METHOD                            #
#                                                                             #
# def updateInterruptDevices(self, intDevId, add=True)                        #
#                                                                             #
###############################################################################

class PiGPIO(IoDevice):
    """
    Read and write bit values from/to built-in Raspberry Pi gpio pins using
    rgpio library methods and update/log the Indigo device onOffState.
    Respond to digital input callbacks (interrupts) to perform contact bounce
    filtering and interrupt relay if requested.  For digital outputs, perform
    pulse width modulation (pwm) and momentary turn-on processing if requested.
    Manage an internal interrupt devices list for use interrupt relay.
    """
    PUD = {'off':  rgpio.SET_PULL_NONE,  # GPIO pullup parameter definitions.
           'up':   rgpio.SET_PULL_UP,
           'down': rgpio.SET_PULL_DOWN}

    def __init__(self, dev):
        """
        Initialize common instance attributes and set rgpio daemon parameters
        for PiGPIO devices.  For digital input devices, setup callback, glitch
        filter, and interrupt relay options if requested.  For digital outputs,
        setup pwm processing if requested.
        """
        IoDevice.__init__(self, dev)  # Common initialization.
        self._h, self._hId = self._getGpioHandle()  # gpio interface.

        # Set internal instance attributes and configure the gpio device.

        self._gpioNumber = int(dev.pluginProps['gpioNumber'])

        if dev.deviceTypeId == 'digitalInput':
            pullup = dev.pluginProps['pullup']
            pud = self.PUD[pullup]
            if dev.pluginProps['callback']:  # alert/callback device
                self._c.gpio_claim_alert(self._h, self._gpioNumber,
                                         rgpio.BOTH_EDGES, pud)
                self._callbackId = self._c.callback(self._h, self._gpioNumber,
                                         rgpio.BOTH_EDGES, self._callback)
                if dev.pluginProps['glitchFilter']:
                    glitchTime = int(dev.pluginProps['glitchTime'])
                    self._c.gpio_set_debounce_micros(self._h, self._gpioNumber,
                                                     glitchTime)
                self._priorTimestamp = 0
                if self._dev.pluginProps['relayInterrupts']:
                    self._interruptDevices = []  # Interrupt devices list.
            else:  # non-alert/callback input device
                self._c.gpio_claim_input(self._h, self._gpioNumber, pud)

        elif dev.deviceTypeId == 'digitalOutput':
            self._c.gpio_claim_output(self._h, self._gpioNumber)

    def _callback(self, gpioChip, gpioNumber, pinBit, timestamp):
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
            dt = timestamp - self._priorTimestamp  # nanoseconds since last cb.
            if dt < 0:
                dt += 1 << 64
            self._priorTimestamp = timestamp
            dt /= 1000.0  # microseconds since last callback.
            dt = min(dt, 200000)  # Ignore anything above 200 msec.
            LD.digital('"%s" callback %i %i %i %i %i', self._dev.name,
                       gpioChip, gpioNumber, pinBit, timestamp, dt)
            logAll = True  # Default logging option for state update.
            if pinBit in (0, 1):
                bit = pinBit ^ self._dev.pluginProps['invert']

                # Relay interrupt, if requested.

                if self._dev.pluginProps['relayInterrupts']:
                    if bit:  # Rising edge; interrupt occurred.
                        self._c.gpio_set_watchdog_micros(self._h,
                            self._gpioNumber, 200000)  # Set watchdog to 200 ms
                        for intDevId in self._interruptDevices:
                            if _ioDevices[intDevId].interrupt():  # Interrupt.
                                break  # Only one match per interrupt.
                        else:  # No match.
                            L.warning('"%s" no device match for hardware '
                                      'interrupt', self._dev.name)
                    else:  # Falling edge; interrupt reset.
                        LD.digital('"%s" interrupt time is %s ms',
                                   self._dev.name, dt / 1000)
                        self._c.gpio_set_watchdog_micros(self._h,
                            self._gpioNumber, 0)  # Reset the watchdog timer.
                    logAll = None  # Set logAll to suppress logging.

                # Update the GPIO device onOffState for both normal and
                # interrupt relay callbacks.

                self._updateOnOffState(bit, logAll=logAll)

            elif pinBit == rgpio.TIMEOUT:  # Timeout; try to force a reset.
                L.warning('"%s" interrupt reset timeout', self._dev.name)
                for intDevId in self._interruptDevices:
                    _ioDevices[intDevId].resetInterrupt()  # Force int reset.
                self._c.gpio_set_watchdog_micros(self._h,
                    self._gpioNumber, 0)  # Reset the watchdog timer.

                # Check to see if it worked.

                pinBit = self._c.gpio_read(self._h, self._gpioNumber)
                bit = pinBit ^ self._dev.pluginProps['invert']
                if bit:  # Interrupt is still active.
                    L.warning('"%s" forced reset failed', self._dev.name)

        except Exception as errorMessage:
            _pigpioError(self._dev, 'int', errorMessage)

    def _read(self, logAll=True):
        """
        Read a bit value from the gpio pin and invert it if requested.  Update
        and log the Indigo device onOffState.
        """
        invert = self._dev.pluginProps.get('invert', False)
        bit = self._c.gpio_read(self._h, self._gpioNumber) ^ invert
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
            self._c.gpio_write(self._h, self._gpioNumber, bit)
            LD.digital('"%s" write %s', self._dev.name, ON_OFF[bit])
            self._updateOnOffState(bit)
            if bit:
                if self._dev.pluginProps['pwm']:
                    frequency = int(self._dev.pluginProps['frequency'])
                    dutyCycle = int(self._dev.pluginProps['dutyCycle'])
                    self._c.tx_pwm(self._h, self._gpioNumber, frequency,
                                   dutyCycle)
                if self._dev.pluginProps['momentary']:
                    time.sleep(float(self._dev.pluginProps['turnOffDelay']))
                    self._write(0)
        else:
            L.warning('"%s" invalid output value %s; write ignored',
                      self._dev.name, value)

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
