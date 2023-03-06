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
v0.5.4   4/ 3/2022  Fix a bug in executeEventTrigger.
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
                    (2) Fix a bug in the ADC12 class that failed to read ADC
                    channels 4-7.
v0.7.1   2/15/2023  Simplify code for SPI integrity checks.
v0.7.2    3/5/2023  (1) Refactor and simplify code for pigpio resource
                    management, exception management, and interrupt processing.
                    (2) Add conditional logging by message type.

TO DO:

1. Fix/add in-line comments for resource management segments.
2. Complete exhaustive testing of exception processing.
3. Fix/add in-line comments for conditional logging.
"""
###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                   DUNDERS, IMPORTS, and GLOBAL Constants                    #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '0.7.2'
__date__ = '3/5/2023'

from abc import ABC, abstractmethod
from datetime import datetime
from logging import getLogger
from random import random
from time import sleep

import indigo

from conditionalLogging import LD, LI
import pigpio

# General global constants and public data attributes:

L = getLogger("Plugin")        # Use the Indigo Plugin logger.
ON, OFF = BIT = (1, 0)         # on/off states and valid bit values.
ON_OFF = ('off', 'on')         # onOffState text values.
GPIO, I2C, SPI = range(3)      # Interface types.
IF = ('gpio', 'i2c-', 'spi-')  # Interface text values.
I2CBUS = 1                     # Primary i2c bus.
SPIBUS = 0                     # Primary spi bus.

# Global display image selector tuple indexed by limitCheck/onOffState states.
# IMAGE[limitCheck][onOffState] = indigo image selector enumeration value

IMAGE = ((indigo.kStateImageSel.SensorOff,  # Normal sensor off/on unless
          indigo.kStateImageSel.SensorOn),  # limit check.
         (indigo.kStateImageSel.SensorTripped,
          indigo.kStateImageSel.SensorTripped))

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
#                        Dynamic Global Dictionaries                          #
#                                                                             #
###############################################################################

# Global public dictionary of io device instance objects keyed by device id:
# ioDevices[dev.id] = <ioDev instance object>

ioDevices = {}

# Global public list of io device counts indexed by raspi host id and interface
# type:
# ioDevCounts[pi id][interface type] = count

ioDevCounts = {}

# Public dictionary of pigpiod shared resources that are reserved/released by
# by multiple plugin devices.  Each entry in the dictionary is a tuple
# containing a resource value and a use count.  Resources are added when they
# are needed, but not currently in the dictionary; they are reserved by
# incrementing the use count, and released by decrementing the use count.  When
# a resource's use count becomes 0, it is removed from the dictionary and
# closed/stopped as needed to return it to the pigpio daemon.

resources = {}

# (resource, use count) = resources[resource id]


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                             Module Functions                                #
#                                                                             #
###############################################################################


def raiseRandomException(errorMessage, frequency=20):
    if random() < frequency / 100:
        raise Exception(errorMessage)


def hexStr(byteList):
    """
    Convert a list of byte integers (0 - 255) to a text string of 2-digit
    hex values separated by spaces.  The byteList argument may be either a
    list of normal integers or a bytearray.  For example,
    hexStr([2, 17, 255, 0xFF]) returns '02 11 ff ff'.
    """
    hexString = ''
    for byte in byteList:
        hexString += '%02x ' % byte
    return hexString[:-1]


# Local module dictionary of trigger times keyed by event name:
# _triggerTime[event name] = last trigger time

_triggerTime = {}


def executeEventTrigger(eventType, event, limitTriggers=True):
    eventTime = datetime.now()

    # Conditionally limit trigger execution.

    if limitTriggers:
        priorTriggerTime = _triggerTime.get(event)
        if priorTriggerTime:
            if (eventTime - priorTriggerTime).total_seconds() < 600:
                return  # Do not execute the trigger for this event.

    # Proceed with trigger execution.

    for trig in indigo.triggers.iter('self'):
        if trig.enabled and trig.pluginTypeId == eventType:
            triggerEvent = trig.pluginProps['triggerEvent']
            if triggerEvent == 'any' or triggerEvent == event:
                indigo.trigger.execute(trig)
                _triggerTime[event] = eventTime


def pigpioFatalError(dev, error, errorMessage, limitTriggers=True):
    """
    Perform the following standard functions for a fatal device error:

    1.  Log the error on the indigo log.
    2.  Indicate the error on the indigo home display by changing the device
        error state and setting the text to red.
    3.  Executing an event trigger to invoke other actions, if any, by the
        indigo server.
    4.  Stopping the io device to disable any future use until it has been
        manually restarted or the plugin has been reloaded.
    """
    L.error('"%s" %s error: %s', dev.name, error, errorMessage)
    dev.setErrorStateOnServer('%s err' % error)
    executeEventTrigger('pigpioError', '%sError' % error,
                        limitTriggers=limitTriggers)
    ioDev = ioDevices.get(dev.id)
    if error != 'stop':  # Do not attempt to stop a second time.
        ioDev.stop()


def start(plugin, dev):
    ioDevType = dev.pluginProps['ioDevType']
    ioDevClass = IODEV_DATA[ioDevType][0]

    try:
        ioDev = globals()[ioDevClass](plugin, dev)
    except ConnectionError as errorMessage:
        pigpioFatalError(dev, 'conn', errorMessage)
        return
    except Exception as errorMessage:
        pigpioFatalError(dev, 'start', errorMessage)
        return

    LI.startStop('"%s" started as a %s on %s',
                 dev.name, dev.deviceTypeId, dev.address)
    dev.setErrorStateOnServer(None)
    ioDev.read(logAll=None)


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                             CLASS PiGPIODevice                              #
#                                                                             #
###############################################################################

class PiGPIODevice(ABC):
    """
    PiGPIODevice is an abstract base class (ABC) used in defining all Pi GPIO
    device classes.  The __init__ method initializes pigpio host access and
    polling
    *************************** needs work ************************************
    status variables.  Additional private methods initialize i2c and spi bus
    access and update the Indigo device states for digital and analog devices.
    It has one public method (stop) that terminates the instance's pigpio
    connection.  PiGPIODevice subclasses must include specific device
    initialization in their __init__ methods and public read/write/stop methods
    as appropriate.
    """

    # Internal instance methods:

    def __init__(self, plugin, dev):
        """
        Manage resources that are allocated and subsequently released/reused by
        pigpio daemons on multiple Raspberry Pi's.  Resources are typically
        assigned to and used by multiple io device objects.  This method
        manages the assignment of resources to io devices to use resources for
        multiple devices when possible and to make them available when io
        devices are stopped.

        Resource objects and use counts for all io devices are saved in an
        internal class dictionary (resources) that is indexed by a
        unique resource id.  During io device initialization, a 'get' call to
        this method will get an existing resource from the dictionary, assign
        it to the io device, and increment the use count.  If no existing
        resource is in the dictionary, a new one is allocated, assigned to the
        device, and added to the dictionary with a use count of 1.

        When an io device is stopped by an io error or an indigo devStopComm
        call, a 'release' call to this method will decrement the use count for
        an existing resource.  If the use count becomes zero the resource is
        removed from the dictionary and de-allocated in the pigpio daemon.

        There are four resourceTypes with properties as follows:

        'conn' identifies a pigpio daemon connection resource.  There is one
               'conn' resource for each Raspberry Pi used by the plugin.  Its
               resource id is a tuple of the form ('conn', hostAddress,
               portNumber).  A 'conn' resource is assigned to an io device by
               setting the device object's self._pi attribute to the resource.

        'i2c'  identifies a i2c device reference resource (aka a i2c device
               handle).  Its resource id is a tuple of the form: ('i2c',
               hostAddress, portNumber, i2cAddress).  A 'i2c' resource is
               assigned to an io device by setting the device object's
               self._handle attribute to the resource.

        'spi'  identifies a spi device reference resource (aka a spi device
               handle).  Its resource id is a tuple of the form: ('spi',
               hostAddress, portNumber, spiChannelNumber, bitRate).  A 'spi'
               resource is assigned to an io device by setting the device
               object's self._handle attribute to the resource.

        'gpio' identifies a dummy resource for built-in gpio devices that is
               used only for the purpose of use counting.  Its resource id is
               a tuple of the form ('gpio', hostAddress, portNumber).
               Maintaining 'gpio' resource use counts along with the 'i2c' and
               'spi' counts ensures that the 'conn' resource use count for each
               pi will accurately reflect the total number of devices hosted on
               that pi.
        """

        # Add the io device instance object to the public ioDevices dictionary.

        ioDevices[dev.id] = self

        # Save private references to the indigo plugin and device objects.

        self._plugin = plugin
        self._dev = dev

        # Initialize common internal instance attributes:

        self._piId = None
        self._callbackId = None  # gpio callback identification object.
        ioDevType = dev.pluginProps['ioDevType']
        self._interface = IODEV_DATA[ioDevType][1]
        self._pollCount = 0  # Poll count for polling status monitoring.
        self._lastPoll = self._lastStatus = indigo.server.getTime()

        # Get the pigpio daemon connection (self._pi) from the resources
        # dictionary.  If no connection is found, initialize a new one.

        hostAddress = self._dev.pluginProps['hostAddress']
        portNumber = self._dev.pluginProps['portNumber']
        hostId = self._dev.pluginProps['hostId']
        self._piId = hostId if hostId else hostAddress + ':' + portNumber

        self._pi, piCount = resources.get(self._piId, (None, 0))
        if self._pi is None:  # No existing connection; initialize a new one.
            self._pi = pigpio.pi(hostAddress, portNumber)
            if not self._pi.connected:  # Connection failed.
                self._pi = None
                errorMessage = 'pigpio connection failed'
                raise ConnectionError(errorMessage)
            LD.resource('New pigpio connection %s', self._piId)
            ioDevCounts[self._piId] = 3*[0]
        piCount += 1
        resources[self._piId] = self._pi, piCount

        # Get a gpio, i2c, or spi handle (self._handle) from the resource
        # dictionary.  If no handle is found, open a new one.

        if self._interface is GPIO:
            self._hId = self._piId + '|gpio'

            self._handle, hCount = resources.get(self._hId, (None, 0))
            self._handle = ''

        elif self._interface is I2C:  # Get an i2c handle.
            i2cAddress = self._dev.pluginProps['i2cAddress']
            self._hId = self._piId + '|' + i2cAddress
            self._handle, hCount = resources.get(self._hId, (None, 0))
            if self._handle is None:  # No existing i2c handle; open a new one.
                self._handle = self._pi.i2c_open(I2CBUS, int(i2cAddress,
                                                             base=16))
                LD.resource('New handle opened %s i2c-%s',
                            self._piId, self._handle)

        else:  # self._interface is SPI; get an spi handle.
            spiChannel = self._dev.pluginProps['spiChannel']
            bitRate = self._dev.pluginProps['bitRate']
            self._hId = self._piId + '|' + spiChannel + '|' + bitRate
            self._handle, hCount = resources.get(self._hId, (None, 0))
            if self._handle is None:  # No existing spi handle; open a new one.
                self._handle = self._pi.spi_open(int(spiChannel),
                               500 * int(bitRate), SPIBUS << 8)
                LD.resource('New handle opened %s spi-%s', self._piId,
                            self._handle)

        hCount += 1
        resources[self._hId] = self._handle, hCount
        LD.resource('"%s" reserved shared pigpiod resources %s (%s) %s%s (%s)',
                    self._dev.name, self._piId, piCount, IF[self._interface],
                    self._handle, hCount)
        ioDevCounts[self._piId][self._interface] += 1

        # Set the initial device state image to override power icon defaults
        # for digital output devices.

        limitFault = dev.states.get('limitFault', False)
        onOffState = dev.states['onOffState']
        dev.updateStateImageOnServer(IMAGE[limitFault][onOffState])

    def _updateOnOffState(self, onOffState, logAll=True):
        """
        If the onOffState has changed, update it on the server and log it if
        logAll is not None.  If there is no change, log the unchanged state if
        logAll is True.
        """
        if onOffState != self._dev.states['onOffState']:
            self._dev.updateStateOnServer(key='onOffState', value=onOffState,
                                          clearErrorState=False)
            limitFault = self._dev.states.get('limitFault', False)
            self._dev.updateStateImageOnServer(IMAGE[limitFault][onOffState])
            if logAll is None:
                return
            L.info('"%s" update onOffState to %s', self._dev.name,
                   ON_OFF[onOffState])
        elif logAll:
            L.info('"%s" onOffState is %s', self._dev.name,
                   ON_OFF[onOffState])

    @staticmethod
    def _uiValue(value, units):
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

    def _updateSensorValueStates(self, voltage, logAll=True):
        """
        Compute the sensor value from the ADC or DAC voltage.  Compute the
        uiValue and update the sensorValue state on the server.  Optionally
        perform sensor value percentage change detection, analog onOffState
        thresholding, and limit checking.  Update states, log results, and
        execute event triggers based on processing results.
        """
        # Compute the sensorValue and uiValue from the ADC / DAC voltage and
        # update the states on the server.

        scalingFactor = float(self._dev.pluginProps['scalingFactor'])
        sensorValue = voltage * scalingFactor
        units = self._dev.pluginProps['units']
        sensorUiValue = self._uiValue(sensorValue, units)
        self._dev.updateStateOnServer(key='sensorValue', value=sensorValue,
                                uiValue=sensorUiValue, clearErrorState=False)

        # Compute the sensorValue percentage change and the changeDetected
        # state value.  Update the changeDetected state on the server.  Log the
        # sensorValue if a change is detected or if logAll is True.

        priorSensorValue = self._dev.states['sensorValue']
        percentChange = (100.0 * abs((sensorValue - priorSensorValue)
            / priorSensorValue if priorSensorValue else 0.001))
        changeThreshold = self._dev.pluginProps['changeThreshold']
        changeDetected = (False if changeThreshold == 'None'
                          else percentChange > float(changeThreshold))
        self._dev.updateStateOnServer(key='changeDetected',
                                      value=changeDetected)
        if changeDetected:
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
        self._updateOnOffState(onOffState, logAll=logAll)

        # Perform limit checking and determine the limitFault state.  If the
        # state has changed, update and process it.

        lowLimit = self._dev.pluginProps['lowLimit']
        if lowLimit == 'None':
            lowLimit = 0.0
            lowFault = False
        else:
            lowLimit = float(lowLimit)
            lowFault = sensorValue < lowLimit

        highLimit = self._dev.pluginProps['highLimit']
        if highLimit == 'None':
            highLimit = 0.0
            highFault = False
        else:
            highLimit = float(highLimit)
            highFault = sensorValue > highLimit

        limitFault = lowFault or highFault

        if limitFault != self._dev.states['limitFault']:  # State changed.
            self._dev.updateStateOnServer(key='limitFault', value=limitFault)
            self._dev.updateStateImageOnServer(IMAGE[limitFault][onOffState])

            if limitFault:  # New limit fault detected.

                # Generate a limit fault message, log it, update the server
                # state/variable, and execute the limitFault event trigger.

                lowUiLimit = self._uiValue(lowLimit, units)
                lowMessage = ('"%s" low limit fault %s < %s'
                        % (self._dev.name, sensorUiValue, lowUiLimit))
                highUiLimit = self._uiValue(highLimit, units)
                highMessage = ('"%s" high limit fault %s > %s'
                        % (self._dev.name, sensorUiValue, highUiLimit))
                limitFaultMessage = (lowMessage, highMessage)[highFault]
                L.warning(limitFaultMessage)
                self._dev.updateStateOnServer(key='limitFaultMessage',
                                              value=limitFaultMessage)
                var = indigo.variables.get('limitFaultMessage')
                if var:  # Update existing variable.
                    indigo.variable.updateValue('limitFaultMessage',
                                                value=limitFaultMessage)
                else:  # No existing variable; create a new one.
                    indigo.variable.create('limitFaultMessage',
                                           value=limitFaultMessage)
                executeEventTrigger('limitFault', 'limitFault')

    # Abstract methods that must be included in all subclasses.

    @abstractmethod
    def _read(self, logAll=True):
        pass

    @abstractmethod
    def _write(self, value):
        pass

    # Public instance methods:

    def read(self, logAll=True):
        try:
            if self._dev.name in ('xio2.s1:27.ga0',):
                raise(Exception, 'forced read error')
            self._read(logAll=logAll)
        except Exception as errorMessage:
            pigpioFatalError(self._dev, 'read', errorMessage)

    def write(self, value):
        try:
            self._write(value)
        except Exception as errorMessage:
            pigpioFatalError(self._dev, 'write', errorMessage)

    def poll(self):
        if self._dev.pluginProps['polling']:
            now = indigo.server.getTime()
            secsSinceLast = (now - self._lastPoll).total_seconds()
            pollingInterval = float(self._dev.pluginProps['pollingInterval'])
            if secsSinceLast >= pollingInterval:
                logAll = self._dev.pluginProps['logAll']
                self.read(logAll=logAll)
                self._pollCount += 1
                self._lastPoll = now
                if self._plugin.pluginPrefs['monitorStatus']:
                    secsSinceLast = (now - self._lastStatus).total_seconds()
                    statusInterval = float(self._plugin.pluginPrefs
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
        Attempt to release all pigpiod shared resources and return to the
        daemon if they have no users.  Note that this is not possible in all
        cases.  Certain exceptions
        """
        try:
            # Remove the io device from the io devices dictionary.

            del ioDevices[self._dev.id]

            # Cancel the gpio callback, if any.

            if self._callbackId:
                self._callbackId.cancel()

            self._pi, piCount = resources.get(self._piId, (None, 0))
            if self._pi:

                # Release pigpiod shared resources by decrementing the shared
                # use count.  Close/stop the resource if the use count becomes
                # zero.

                piCount -= 1
                resources[self._piId] = self._pi, piCount

                self._handle, hCount = resources.get(self._hId, (None, 0))
                if self._handle is not None:  # Include GPIO devices.

                    hCount -= 1
                    resources[self._hId] = self._handle, hCount

                    LD.resource('"%s" released shared pigpiod resources '
                                '%s (%s) %s%s (%s)', self._dev.name,
                                self._piId, piCount, IF[self._interface],
                                self._handle, hCount)
                    ioDevCounts[self._piId][self._interface] -= 1

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
                        del resources[self._hId]
                        self._handle = None

                if not piCount:

                    # No more users for this pigpiod connection.  Stop the
                    # connection and delete the resource.

                    self._pi.stop()
                    LD.resource('pigpiod connection stopped %s', self._piId)
                    del resources[self._piId]
                    self._pi = None

        except Exception as errorMessage:
            pigpioFatalError(self._dev, 'stop', errorMessage)

        LI.startStop('"%s" stopped', self._dev.name)


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                                CLASS ADC12                                  #
#                                                                             #
###############################################################################

class ADC12(PiGPIODevice):

    # Internal instance methods:

    def __init__(self, plugin, dev):
        PiGPIODevice.__init__(self, plugin, dev)

        # Assemble data tuple for ADC12 devices.

        inputConfiguration = int(dev.pluginProps['inputConfiguration'])
        adcChannel = int(self._dev.pluginProps['adcChannel'])
        self._data = (0x04 | inputConfiguration << 1 | adcChannel >> 2,
                      (adcChannel << 6) & 0xff, 0)
        ioDevType = self._dev.pluginProps['ioDevType']
        if ioDevType == 'MCP3202':
            self._data = (0x01, inputConfiguration << 7 | adcChannel << 6, 0)

    def _readSpiVoltage(self):
        referenceVoltage = float(self._dev.pluginProps['referenceVoltage'])
        nBytes, bytes_ = self._pi.spi_xfer(self._handle, self._data)
        outputCode = (bytes_[1] & 0x0f) << 8 | bytes_[2]
        voltage = referenceVoltage * outputCode / 4096
        LD.analog('"%s" read %s | %s | %s | %s | %s',
                  self._dev.name, hexStr(self._data), nBytes,
                  hexStr(bytes_), outputCode, voltage)
        return voltage

    def _read(self, logAll=True):  # Implementation of abstract method.
        voltage = self._readSpiVoltage()
        if self._plugin.pluginPrefs['checkSPI']:  # Check SPI integrity.
            voltage_ = self._readSpiVoltage()
            percentChange = 100.0 * (abs((voltage - voltage_)
                            / voltage if voltage else 0.001))
            if percentChange >= 1.0:
                LD.analog('"%s" spi check: different values on consecutive '
                          'reads %.4f %.4f', self._dev.name, voltage, voltage_)
                voltage = voltage_

        self._updateSensorValueStates(voltage, logAll=logAll)

    def _write(self, value):  # Implementation of abstract method.
        pass


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                                CLASS ADC18                                  #
#                                                                             #
###############################################################################

class ADC18(PiGPIODevice):

    # Internal instance methods:

    def __init__(self, plugin, dev):
        PiGPIODevice.__init__(self, plugin, dev)

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

    def _read(self, logAll=True):  # Implementation of abstract method.

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

        outputCode = -1 if bytes_[0] & 0x80 else 0
        for byte in bytes_[:-1]:
            outputCode = outputCode << 8 | byte

        # Compute the voltage and update the sensor value state.

        referenceVoltage = 2.048  # Internal reference voltage (volts).
        maxCode = 1 << (resolution - 1)  # maxCode = (2 ** (resolution - 1)).
        gain = int(self._dev.pluginProps['gain'])
        voltage = (referenceVoltage * outputCode / (maxCode * gain))
        LD.analog('"%s" read %s | %s | %s | %s', self._dev.name, numReads,
                  hexStr(bytes_), outputCode, voltage)
        self._updateSensorValueStates(voltage, logAll=logAll)

    def _write(self, value):  # Implementation of abstract method.
        pass


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                                CLASS DAC12                                  #
#                                                                             #
###############################################################################

class DAC12(PiGPIODevice):

    # Internal instance methods:

    def __init__(self, plugin, dev):
        PiGPIODevice.__init__(self, plugin, dev)

    def _read(self, logAll=True):  # Implementation of abstract method.
        sensorValue = self._dev.states['sensorValue']
        scalingFactor = float(self._dev.pluginProps['scalingFactor'])
        voltage = sensorValue / scalingFactor
        self._updateSensorValueStates(voltage, logAll=logAll)

    def _write(self, value):  # Implementation of abstract method.

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
            LD.analog('"%s" xfer %s | %s | %s | %s',
                      self._dev.name, voltage, inputCode, hexStr(data), nBytes)
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
###############################################################################

class DockerPiRelay(PiGPIODevice):

    # Internal instance methods:

    def __init__(self, plugin, dev):
        PiGPIODevice.__init__(self, plugin, dev)

    def _read(self, logAll=True):  # Implementation of abstract method.
        onOffState = self._dev.states['onOffState']
        self._updateOnOffState(onOffState, logAll=logAll)

    def _write(self, value):  # Implementation of abstract method.
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

    # IOCON bit constants:

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

    def __init__(self, plugin, dev):
        PiGPIODevice.__init__(self, plugin, dev)

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

        if dev.deviceTypeId == 'digitalInput':
            self._updateRegister('IODIR', self.INPUT)
            invert = self._dev.pluginProps['invert']
            self._updateRegister('IPOL', invert)  # Set input polarity.
            pullup = dev.pluginProps['pullup']
            self._updateRegister('GPPU', pullup == 'up')  # Set pullup option.
            self._updateRegister('DEFVAL', OFF)  # Clear default bit.
            self._updateRegister('INTCON', OFF)  # Interrupt on change.
            hardwareInterrupt = dev.pluginProps['hardwareInterrupt']
            self._updateRegister('GPINTEN', hardwareInterrupt)
            if hardwareInterrupt:  # Configure int relay; get relay io dev.
                interruptRelayGPIO = dev.pluginProps['interruptRelayGPIO']
                relayDev = indigo.devices[interruptRelayGPIO]
                props = relayDev.pluginProps
                if props.get('relayInterrupts'):
                    if not props.get('interruptDevices'):
                        props['interruptDevices'] = indigo.List()
                    interruptDevices = props['interruptDevices']
                    if dev.id not in interruptDevices:
                        interruptDevices.append(dev.id)
                    props['interruptDevices'] = interruptDevices
                    relayDev.replacePluginPropsOnServer(props)
                    LD.digital('"%s" added to "%s" interrupt devices',
                               dev.name, relayDev.name)
                else:
                    L.warning('"%s" cannot add interrupt device to "%s"',
                              dev.name, relayDev.name)

        elif dev.deviceTypeId == 'digitalOutput':
            self._updateRegister('IODIR', self.OUTPUT)

    def _readSpiByte(self, register, data):
        nBytes, bytes_ = self._pi.spi_xfer(self._handle, data)
        byte = bytes_[-1]
        LD.digital('"%s" readRegister %s %s | %s | %s', self._dev.name,
                   register, hexStr(data), nBytes, hexStr(bytes_))
        return byte

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

            if self._plugin.pluginPrefs['checkSPI']:  # Check SPI integrity.
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
                       self._dev.name, register, hexStr(data), nBytes)

    def _updateRegister(self, register, bit):
        byte = self._readRegister(register)
        updatedByte = byte | self._mask if bit else byte & ~self._mask
        if updatedByte != byte:
            LD.digital('"%s" updateRegister %s %02x | %s | %02x',
                       self._dev.name, register, byte, bit, updatedByte)
            self._writeRegister(register, updatedByte)

    def _read(self, logAll=True):  # Implementation of abstract method.
        byte = self._readRegister('GPIO')
        bit = 1 if byte & self._mask else 0
        self._updateOnOffState(bit, logAll=logAll)
        return bit

    def _write(self, value):  # Implementation of abstract method.
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
            # raiseRandomException('interrupt read')
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
            pigpioFatalError(self._dev, 'int', errorMessage)

    def resetInterrupt(self):
        try:
            self._readRegister('GPIO')  # Read port register to clear interrupt
        except Exception as errorMessage:
            pigpioFatalError(self._dev, 'int', errorMessage)

###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                                CLASS PiGPIO                                 #
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

    def __init__(self, plugin, dev):
        PiGPIODevice.__init__(self, plugin, dev)

        # Set internal instance attributes and configure gpio device.

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
                            intIoDev = ioDevices.get(intDevId)
                            if intIoDev and intIoDev.interrupt():
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
                        intIoDev = ioDevices.get(intDevId)
                        if intIoDev:
                            intIoDev.resetInterrupt()
                    self._pi.set_watchdog(self._gpioNumber, 0)  # Clear wdog.

        except Exception as errorMessage:
            pigpioFatalError(self._dev, 'int', errorMessage)

    def _read(self, logAll=True):  # Implementation of abstract method.
        invert = self._dev.pluginProps.get('invert', False)
        bit = self._pi.read(self._gpioNumber) ^ invert
        LD.digital('"%s" read %s', self._dev.name, ON_OFF[bit])
        self._updateOnOffState(bit, logAll=logAll)
        return bit

    def _write(self, value):  # Implementation of abstract method.
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
