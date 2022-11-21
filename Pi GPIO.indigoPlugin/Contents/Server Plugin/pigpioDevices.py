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
 VERSION:  0.6.1
    DATE:  November 21, 2022


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
                    a device's interface type (I2C, SPI, or None)
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
"""
###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                 DUNDERS, IMPORTS, GLOBALS, and FUNCTIONS                    #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '0.6.1'
__date__ = '11/21/2022'

from abc import ABC, abstractmethod
from datetime import datetime
from logging import getLogger
from time import sleep
import indigo
import pigpio

# Module constants and public data attributes:

LOG = getLogger('Plugin')   # Use the same logger as the Indigo Plugin class.
ON = 1                      # Constant for the on state.
OFF = 0                     # Constant for the off state.
ON_OFF = ('off', 'on')      # Text values for the onOffState.
I2C = 'i2c'                 # Constant for an I2C interface.
SPI = 'spi'                 # Constant for an SPI interface.
GPIO = 'gpio'               # Constant for built-in GPIO.

# Public dictionary of io device data.
# IODEV_DATA[ioDevType] = (ioDevClass, interface):

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

# Public dictionary of io device instance objects.
# ioDevices[dev.id] = <ioDev instance object>:

ioDevices = {}  # Dictionary of io device instances.

# Local module dictionary of trigger times:

_triggerTime = {}  # cls._triggerTime[event] = last trigger time for event.


# Module functions:

def hexStr(byteList):
    """
    Convert a list of byte integers (0 - 255) to a text string of 2-digit
    hex values separated by spaces.  The byteList argument may be either a
    list of normal integers or a bytearray.  For example,
    hexStr([2, 17, 255, 0xFF]) returns '02 11 ff ff'.
    """
    hexString = u''
    for byte in byteList:
        hexString += '%02x ' % byte
    return hexString[:-1]


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
        state and setting the text to red.
    3.  Executing an event trigger to invoke other actions, if any, by the
        indigo server.
    4.  Stopping the io device to disable any future use until it has been
        manually restarted or the plugin has been reloaded.
    """
    LOG.error('"%s" %s error: %s', dev.name, error, errorMessage)
    dev.setErrorStateOnServer('%s err' % error)
    executeEventTrigger('pigpioError', '%sError' % error,
                        limitTriggers=limitTriggers)
    ioDev = ioDevices.get(dev.id)
    if ioDev:
        ioDev.stop()


def start(plugin, dev):
    if ioDevices.get(dev.id):  # Return if already started.
        return

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

    LOG.info('"%s" started as a %s on %s',
             dev.name, dev.deviceTypeId, dev.address)
    dev.setErrorStateOnServer(None)
    ioDev.read()


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

    # Class constants:

    I2CBUS = 1  # Primary i2c bus.
    SPIBUS = 0  # Primary spi bus.
    IMAGE_SEL = (indigo.kStateImageSel.SensorOff,  # State image selectors.
                 indigo.kStateImageSel.SensorOn)

    # Class dictionary:

    _resources = {}  # self._resources[resourceId] = (resource, useCount).

    # Internal instance methods:

    def __init__(self, plugin, dev):

        # Add io device instance object to the public ioDevices dictionary.

        ioDevices[dev.id] = self

        # Save private references to the indigo plugin and device objects.

        self._plugin = plugin
        self._dev = dev

        # Initialize common internal instance attributes:

        self._pi = None  # pigpio daemon connection object.
        self._handle = None  # pigpio i2c or spi device reference object.
        self._callbackId = None  # gpio callback identification object.
        self._pollCount = 0  # Poll count for polling status monitoring.
        self._lastPoll = self._lastStatus = indigo.server.getTime()

        # Connect to the pigpio daemon and set the connection instance
        # attribute (self._pi).

        self._managePigpioResources('get', 'conn')

        # Define the interface id for this device and set the device reference
        # object (self._handle) for an i2c or spi device.

        self._ioDevType = dev.pluginProps['ioDevType']
        self._interface = IODEV_DATA[self._ioDevType][1]
        self._managePigpioResources('get', self._interface)

        # Set device state image.

        dev.updateStateImageOnServer(self.IMAGE_SEL[dev.onState])

    def _managePigpioResources(self, action, resourceType):
        """
        Manage resources that are allocated and subsequently released/reused by
        pigpio daemons on multiple Raspberry Pi's.  Resources are typically
        assigned to and used by multiple io device objects.  This method
        manages the assignment of resources to io devices to use resources for
        multiple devices when possible and to make them available when io
        devices are stopped.

        Resource objects and use counts for all io devices are saved in an
        internal class dictionary (self._resources) that is indexed by a
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
        # Compute the resource id tuple and get the dictionary entry, if any.

        hostAddress = self._dev.pluginProps['hostAddress']
        portNumber = self._dev.pluginProps['portNumber']
        resourceId = (resourceType, hostAddress, portNumber)
        if resourceType is I2C:
            i2cAddress = self._dev.pluginProps['i2cAddress']
            resourceId += (i2cAddress,)
        elif resourceType is SPI:
            spiChannel = self._dev.pluginProps['spiChannel']
            bitRate = self._dev.pluginProps['bitRate']
            resourceId += (spiChannel, bitRate)
        resource, useCount = self._resources.get(resourceId, (None, 0))

        if action is 'get':

            # Get the resource and assign it to this device by setting the
            # appropriate instance attribute (self._pi or self._handle).
            # Update the resources dictionary.

            if resource is not None:  # Use existing resource.
                if resourceType is 'conn':
                    self._pi = resource
                else:
                    self._handle = resource
                useCount += 1
                self._resources[resourceId] = (resource, useCount)

            else:  # No existing resource; allocate a new one.
                if resourceType == 'conn':  # pigpio connection resource.
                    resource = pigpio.pi(hostAddress, portNumber)
                    if not resource.connected:  # Connection failed.
                        errorMessage = 'pigpio connection failed'
                        raise ConnectionError(errorMessage)
                    self._pi = resource
                elif resourceType == I2C:  # i2c resource.
                    resource = self._pi.i2c_open(self.I2CBUS,
                                                 int(i2cAddress, base=16))
                    self._handle = resource
                elif resourceType == SPI:  # spi resource.
                    resource = self._pi.spi_open(int(spiChannel),
                                                 500 * int(bitRate),
                                                 self.SPIBUS << 8)
                    self._handle = resource
                elif resourceType == GPIO:  # gpio resource.
                    resource = ''  # Dummy resource; used only to count gpio's.
                self._resources[resourceId] = resource, 1
                LOG.debug('"%s" new %s resource allocated %s',
                          self._dev.name, resourceType, resource)

        elif action is 'release' and resource is not None:

            # Decrement the use count and release the resource if it is no
            # longer in use.

            useCount -= 1
            if useCount:  # Additional users; update the dictionary.
                self._resources[resourceId] = (resource, useCount)

            else:  # No additional users; delete the entry and de-allocate.
                del self._resources[resourceId]

                if resourceType is 'conn':
                    resource.stop()
                elif resourceType is I2C:
                    self._pi.i2c_close(resource)
                elif resourceType is SPI:
                    self._pi.spi_close(resource)

                LOG.debug('"%s" %s resource released %s',
                          self._dev.name, resourceType, resource)

    def _getUiValue(self, value):
        """
        Generate a format string for the uiValue that shows 3 significant
        digits over a wide range of values.  Return a uiValue based on the
        format string and the object's units.
        """
        magnitude = abs(value)
        if magnitude < 10:
            uiFormat = '%.2f %s'
        elif magnitude < 100:
            uiFormat = '%.1f %s'
        else:
            uiFormat = '%i %s'

        units = self._dev.pluginProps['units']
        return uiFormat % (value, units)

    def _updateOnOffState(self, onOffState, logAll=True):
        """
        If the onOffState has changed, update it on the server and log it if
        logAll is not None.  If there is no change, log the unchanged state if
        logAll is True.
        """
        if onOffState != self._dev.states['onOffState']:
            self._dev.updateStateOnServer(key='onOffState', value=onOffState,
                                          clearErrorState=False)
            self._dev.updateStateImageOnServer(self.IMAGE_SEL[onOffState])
            if logAll is None:
                return
            LOG.info('"%s" update to %s', self._dev.name, ON_OFF[onOffState])
        elif logAll:
            LOG.info('"%s" is %s', self._dev.name, ON_OFF[onOffState])

    def _updateSensorValueStates(self, voltage, logAll=True):
        """
        Compute the sensor value from the ADC voltage snd perform change
        detection and limit checks.  Compute the uiValue and update all device
        states on the server.  Log the sensor value if a change was detected or
        if logAll is True.
        """
        scalingFactor = float(self._dev.pluginProps['scaling'])
        sensorValue = voltage * scalingFactor

        # Detect a percentage change in the sensor value and update the server
        # change detected state.

        priorSensorValue = self._dev.states['sensorValue']
        percentChange = 100.0 * abs((sensorValue - priorSensorValue)
                        / priorSensorValue if priorSensorValue else 0.001)
        changeThreshold = float(self._dev.pluginProps['changeThreshold'])
        changeDetected = percentChange >= changeThreshold
        self._dev.updateStateOnServer(key='changeDetected',
                                      value=changeDetected)

        # Perform low and high limit checks and update the limit fault states
        # on the server.

        event = None
        units = self._dev.pluginProps['units']
        lowLimitCheck = self._dev.pluginProps['lowLimitCheck']
        if lowLimitCheck:
            lowLimit = float(self._dev.pluginProps['lowLimit'])
            lowFault = sensorValue < lowLimit
            self._dev.updateStateOnServer(key='lowFault', value=lowFault)
            if lowFault:
                event = 'lowFault'
                LOG.warning('"%s" low limit fault %.4f %s <  %.4f %s',
                            self._dev.name, sensorValue, units, lowLimit,
                            units)

        highLimitCheck = self._dev.pluginProps['highLimitCheck']
        if highLimitCheck:
            highLimit = float(self._dev.pluginProps['highLimit'])
            highFault = sensorValue > highLimit
            self._dev.updateStateOnServer(key='highFault', value=highFault)
            if highFault:  # It's OK, lowFault and highFault are exclusive.
                event = 'highFault'
                LOG.warning('"%s" high limit fault %.4f %s > %.4f %s',
                            self._dev.name, sensorValue, units, highLimit,
                            units)

        # Update the state image to visually show limit check results and
        # execute any triggers.

        if lowLimitCheck or highLimitCheck:
            if event:
                executeEventTrigger('limitFault', event)
                self._dev.updateStateImageOnServer(
                          indigo.kStateImageSel.SensorTripped)
            else:
                self._dev.updateStateImageOnServer(
                          indigo.kStateImageSel.SensorOn)
        else:
            self._dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)

        # Update the sensor value state and the uiValue.  Log the sensor value
        # if a change was detected or if logAll=True.

        uiValue = self._getUiValue(sensorValue)
        self._dev.updateStateOnServer(key='sensorValue', value=sensorValue,
                                      uiValue=uiValue, clearErrorState=False)
        if changeDetected:
            LOG.info('"%s" update to %.4f %s',
                     self._dev.name, sensorValue, units)
        elif logAll:
            LOG.info('"%s" is %.4f %s',
                     self._dev.name, sensorValue, units)

    # Abstract methods that must be included in all subclasses.

    @abstractmethod
    def _read(self, logAll=True):
        pass

    @abstractmethod
    def _write(self, value):
        pass

    # Public instance methods:

    def getName(self):
        return self._dev.name

    def read(self, logAll=True):
        try:
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
                        LOG.info('"%s" average polling interval is %4.2f '
                                 'secs, rate is %4.2f per sec',
                                 self._dev.name, averageInterval, averageRate)
                        self._pollCount = 0
                        self._lastStatus = now

    def stop(self):

        # Remove the io device from the io devices dictionary.

        if self._dev.id in ioDevices:
            del ioDevices[self._dev.id]
            LOG.debug('"%s" stopped', self._dev.name)

        # Release pigpiod resources.

        if self._pi:  # Skip if there is no active connection.
            try:
                # Cancel the gpio callback and release i2c, spi, and connection
                # resources.

                if self._callbackId:
                    self._callbackId.cancel()
                self._managePigpioResources('release', self._interface)
                self._managePigpioResources('release', 'conn')

            except Exception as errorMessage:
                pigpioFatalError(self._dev, 'stop', errorMessage)


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
                      adcChannel << 6, 0)
        ioDevType = self._dev.pluginProps['ioDevType']
        if ioDevType == 'MCP3202':
            self._data = (0x01, inputConfiguration << 7 | adcChannel << 6, 0)

    def _read(self, logAll=True):  # Implementation of abstract method.

        referenceVoltage = float(self._dev.pluginProps['referenceVoltage'])
        nBytes1, bytes1 = self._pi.spi_xfer(self._handle, self._data)
        outputCode1 = (bytes1[1] & 0x0f) << 8 | bytes1[2]
        voltage1 = referenceVoltage * outputCode1 / 4096
        LOG.debug('"%s" read %s | %s | %s | %s | %s',
                  self._dev.name, hexStr(self._data), nBytes1,
                  hexStr(bytes1), outputCode1, voltage1)

        if self._plugin.pluginPrefs['checkSPI']:  # Check SPI integrity.
            nBytes2, bytes2 = self._pi.spi_xfer(self._handle, self._data)
            outputCode2 = (bytes2[1] & 0x0f) << 8 | bytes2[2]
            voltage2 = referenceVoltage * outputCode2 / 4096
            LOG.debug('"%s" read %s | %s | %s | %s | %s',
                      self._dev.name, hexStr(self._data), nBytes2,
                      hexStr(bytes2), outputCode2, voltage2)
            percentChange = 100.0 * (abs((voltage1 - voltage2)
                                         / voltage1 if voltage1 else 0.001))
            changeThreshold = float(self._dev.pluginProps['changeThreshold'])
            if percentChange >= changeThreshold:
                LOG.warning('"%s" spi check: different values on consecutive '
                            'reads %.4f %.4f',
                            self._dev.name, voltage1, voltage2)
                voltage1 = voltage2

        self._updateSensorValueStates(voltage1, logAll=logAll)

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
        LOG.debug('"%s" read %s | %s | %s | %s', self._dev.name, numReads,
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
        units = self._dev.pluginProps['units']
        LOG.info('"%s" is %.4f %s', self._dev.name, sensorValue, units)

    def _write(self, value):  # Implementation of abstract method.

        # Check the argument.

        try:
            sensorValue = float(value)
        except ValueError:
            LOG.warning('"%s" invalid output value %s; write ignored;',
                        self._dev.name, value)
            return

        # Convert the sensorValue to a DAC input code and write to the DAC.

        scalingFactor = float(self._dev.pluginProps['scaling'])
        voltage = sensorValue / scalingFactor
        referenceVoltage = 2.048  # Internal reference voltage (volts).
        gain = int(self._dev.pluginProps['gain'])
        inputCode = int(voltage * 4096 / (referenceVoltage * gain))

        if 0 <= inputCode < 4096:
            dacChannel = int(self._dev.pluginProps['dacChannel'])
            data = (dacChannel << 7 | (gain & 1) << 5 | 0x10 | inputCode >> 8,
                    inputCode & 0xff)
            nBytes = self._pi.spi_write(self._handle, data)
            LOG.debug('"%s" xfer %s | %s | %s | %s',
                      self._dev.name, voltage, inputCode, hexStr(data), nBytes)
        else:
            LOG.warning('"%s" converted input code %s is outside of DAC '
                        'range; write ignored', self._dev.name, inputCode)
            return

        # Update and log the sensorValue state.

        uiValue = self._getUiValue(sensorValue)
        self._dev.updateStateOnServer(key='sensorValue', value=sensorValue,
                                      uiValue=uiValue, clearErrorState=False)
        units = self._dev.pluginProps['units']
        LOG.info('"%s" update to %.4f %s', self._dev.name, sensorValue, units)


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
        LOG.info('"%s" is %s', self._dev.name, ON_OFF[onOffState])

    def _write(self, value):  # Implementation of abstract method.
        bit = 99
        try:
            bit = int(value)
        except ValueError:
            pass
        if bit in (ON, OFF):
            relayNumber = int(self._dev.pluginProps['relayNumber'])
            self._pi.i2c_write_byte_data(self._handle, relayNumber, bit)
            LOG.debug('"%s" write %s', self._dev.name, ON_OFF[bit])
            self._updateOnOffState(bit)
            if bit:
                if self._dev.pluginProps['momentary']:
                    sleep(float(self._dev.pluginProps['turnOffDelay']))
                    self._write(OFF)
        else:
            LOG.warning('"%s" invalid output value %s; write ignored',
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
                rioDev = ioDevices.get(relayDev.id)
                if not rioDev:  # Not initialized yet; try starting it.
                    LOG.info('"%s" starting interrupt relay GPIO "%s"',
                             self._dev.name, interruptRelayGPIO)
                    start(self._plugin, relayDev)
                    rioDev = ioDevices.get(relayDev.id)
                    if not rioDev:  # Start failed; raise exception.
                        errorMessage = ('interrupt relay GPIO "%s" not'
                                        ' started' % interruptRelayGPIO)
                        raise Exception(errorMessage)

                # Add this io device object to the relay io device's internal
                # interrupt devices list.

                rioDev.addInterruptDevice(self)

        elif dev.deviceTypeId == 'digitalOutput':
            self._updateRegister('IODIR', self.OUTPUT)

    def _readRegister(self, register):
        registerAddress = self.REG_BASE_ADDR[register] + self._offset

        if self._interface is I2C:  # MCP230XX
            byte = self._pi.i2c_read_byte_data(self._handle, registerAddress)
            LOG.debug('"%s" readRegister %s %02x',
                      self._dev.name, register, byte)

        else:  # MCP23SXX
            spiDevAddress = int(self._dev.pluginProps['spiDevAddress'], 16)
            data = (spiDevAddress << 1 | self.READ, registerAddress, 0)
            nBytes1, bytes1 = self._pi.spi_xfer(self._handle, data)
            byte = bytes1[-1]
            LOG.debug('"%s" readRegister %s %s | %s | %s',
                      self._dev.name, register, hexStr(data), nBytes1,
                      hexStr(bytes1))

            if self._plugin.pluginPrefs['checkSPI']:  # Check SPI integrity.
                nBytes2, bytes2 = self._pi.spi_xfer(self._handle, data)
                byte2 = bytes2[-1]
                LOG.debug('"%s" readRegister %s %s | %s | %s',
                          self._dev.name, register, hexStr(data), nBytes2,
                          hexStr(bytes2))
                if byte != byte2:
                    LOG.warning('"%s" readRegister %s spi check: unequal '
                                'consecutive reads %02x %02x',
                                self._dev.name, register, byte, byte2)
                    byte = byte2
        return byte

    def _writeRegister(self, register, byte):
        registerAddress = self.REG_BASE_ADDR[register] + self._offset

        if self._interface is I2C:  # MCP230XX
            self._pi.i2c_write_byte_data(self._handle, registerAddress, byte)
            LOG.debug('"%s" writeRegister %s %02x',
                      self._dev.name, register, byte)

        else:  # MCP23SXX
            spiDevAddress = int(self._dev.pluginProps['spiDevAddress'], 16)
            data = (spiDevAddress << 1 | self.WRITE, registerAddress, byte)
            nBytes = self._pi.spi_write(self._handle, data)
            LOG.debug('"%s" writeRegister %s %s | %s',
                      self._dev.name, register, hexStr(data), nBytes)

    def _updateRegister(self, register, bit):
        byte = self._readRegister(register)
        updatedByte = byte | self._mask if bit else byte & ~self._mask
        if updatedByte != byte:
            LOG.debug('"%s" updateRegister %s %02x | %s | %02x',
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
        if bit in (ON, OFF):
            self._updateRegister('GPIO', bit)
            self._updateOnOffState(bit)
            if bit:
                if self._dev.pluginProps['momentary']:
                    sleep(float(self._dev.pluginProps['turnOffDelay']))
                    self._write(OFF)
        else:
            LOG.warning('"%s" invalid output value %s; write ignored',
                        self._dev.name, value)

    # Public instance methods:

    def interrupt(self):
        try:
            # Read and check interrupt flag register for interrupt on this
            # device.

            intf = self._readRegister('INTF')
            if not intf & self._mask:
                return  # No match for this device.
            else:

                # Interrupt flag bit matches device bit; read interrupt capture
                # register and update the state.

                intcap = self._readRegister('INTCAP')
                bit = 1 if intcap & self._mask else 0
                LOG.debug('"%s" interrupt %02x | %02x | %s',
                          self._dev.name, intf, intcap, ON_OFF[bit])
                self._updateOnOffState(bit)

                # Check for lost interrupts.

                lostInterrupts = intf ^ self._mask
                if lostInterrupts:  # Any other bits set in interrupt flag reg?
                    LOG.warning('"%s" lost interrupts %02x',
                                self._dev.name, lostInterrupts)
                return True  # Signal an interrupt match.
        except Exception as errorMessage:
            pigpioFatalError(self._dev, 'int', errorMessage)

    def resetInterrupt(self):
        try:
            self._readRegister('GPIO')  # Read port register to clear int.
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
                if dev.pluginProps['relayInterrupts']:

                    # Initialize an internal interrupt devices list to save
                    # the device objects of all io devices whose hardware
                    # interrupt output is connected to this GPIO input.  This
                    # supports the interrupt relay function in the
                    # self._callback method below.

                    self._interruptDevices = []

        elif dev.deviceTypeId == 'digitalOutput':
            self._pi.set_mode(self._gpioNumber, pigpio.OUTPUT)
            if dev.pluginProps['pwm']:
                self._pi.set_PWM_range(self._gpioNumber, 100)
                frequency = int(dev.pluginProps['frequency'])
                self._pi.set_PWM_frequency(self._gpioNumber, frequency)

    def _callback(self, gpioNumber, pinBit, tic):
        dt = pigpio.tickDiff(self._priorTic, tic)
        self._priorTic = tic
        LOG.debug('"%s" callback %s %s %s %s',
                  self._dev.name, gpioNumber, pinBit, tic, dt)
        logAll = True  # Default logging option for state update.
        if pinBit in (ON, OFF):
            bit = pinBit ^ self._dev.pluginProps['invert']

            # Apply the contact bounce filter, if requested.

            if self._dev.pluginProps['bounceFilter']:
                if dt < self._dev.pluginProps['bounceTime']:  # State bouncing.
                    if self._dev.pluginProps['logBounce']:
                        LOG.warning('"%s" %s µs bounce; update to %s ignored',
                                    self._dev.name, dt, ON_OFF[bit])
                    return  # Ignore the bounced state change.

            # Relay interrupts, if requested.

            elif self._dev.pluginProps['relayInterrupts']:
                if bit:  # Interrupt initiated; process it and set watchdog.
                    for ioDev in self._interruptDevices:
                        if ioDev.interrupt():  # Interrupt successful.
                            break  # Only one match allowed per interrupt.
                    else:
                        LOG.warning('"%s" no match in interrupt devices list',
                                    self._dev.name)
                    self._pi.set_watchdog(self._gpioNumber, 200)  # Set wdog.
                else:  # Interrupt reset; log time and clear the watchdog.
                    LOG.debug('"%s" interrupt time is %s ms',
                              self._dev.name, dt / 1000)
                    self._pi.set_watchdog(self._gpioNumber, 0)
                logAll = None  # Suppress logging for interrupt relay GPIO.

            # Update the onOff state.

            self._updateOnOffState(bit, logAll=logAll)

        else:  # Interrupt reset timeout.
            LOG.warning('"%s" interrupt reset timeout', self._dev.name)
            for ioDev in self._interruptDevices:
                ioDev.resetInterrupt()
            self._pi.set_watchdog(self._gpioNumber, 0)  # Clear watchdog.

    def _read(self, logAll=True):  # Implementation of abstract method.
        invert = self._dev.pluginProps.get('invert', False)
        bit = self._pi.read(self._gpioNumber) ^ invert
        LOG.debug('"%s" read %s', self._dev.name, ON_OFF[bit])
        self._updateOnOffState(bit, logAll=logAll)
        return bit

    def _write(self, value):  # Implementation of abstract method.
        bit = 99
        try:
            bit = int(value)
        except ValueError:
            pass
        if bit in (ON, OFF):
            self._pi.write(self._gpioNumber, bit)
            LOG.debug('"%s" write %s', self._dev.name, ON_OFF[bit])
            self._updateOnOffState(bit)
            if bit:
                if self._dev.pluginProps['pwm']:
                    dutyCycle = int(self._dev.pluginProps['dutyCycle'])
                    self._pi.set_PWM_dutycycle(self._gpioNumber, dutyCycle)
                if self._dev.pluginProps['momentary']:
                    sleep(float(self._dev.pluginProps['turnOffDelay']))
                    self._write(OFF)
        else:
            LOG.warning('"%s" invalid output value %s; write ignored',
                        self._dev.name, value)

    # Public instance method:

    def addInterruptDevice(self, ioDev):
        """
        Add interrupt device to the internal interrupt devices list.
        """
        if ioDev not in self._interruptDevices:
            self._interruptDevices.append(ioDev)
        LOG.debug('"%s" added interrupt device "%s"', self._dev.name,
                  ioDev.getName())
