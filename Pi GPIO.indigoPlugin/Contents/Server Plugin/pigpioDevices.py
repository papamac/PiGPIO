# coding=utf-8
###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                                                                             #
###############################################################################
"""
 PACKAGE:  Raspberry Pi General Purpose Input/Output for indigo (PiGPIO)
  MODULE:  pigpioDevices.py
   TITLE:  Pi GPIO device management
FUNCTION:  pigpioDevices.py provides classes to define and manage five
           different categories of Pi GPIO devices.  Each class initializes,
           configures, starts, and stops io device objects for each indigo
           device.  Class methods also execute device actions and update
           device states.
   USAGE:  pigpioDevices.py is included by the primary plugin class,
           Plugin.py.  Its methods are called as needed by Plugin.py methods.
  AUTHOR:  papamac
 VERSION:  0.5.2
    DATE:  January 19, 2022


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
top level PiGPIO folder.  Changes of lesser importance may be described in
individual module docstrings if appropriate.

0.5.0  11/28/2021  Fully functional beta version with incomplete documentation.
0.5.2   1/19/2022  Use common IODEV_DATA dictionary to unambiguously identify
                   a device's interface type (I2C, SPI, or None)


"""

###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                 DUNDERS, IMPORTS, GLOBALS, and FUNCTIONS                    #
#                                                                             #
###############################################################################

__author__ = u'papamac'
__version__ = u'1.1.2'
__date__ = u'September 9, 2021'

from logging import getLogger
from time import sleep
import indigo
import pigpio


# Module constants and public data attributes:

LOG = getLogger(u'Plugin')  # Use the same logger as the indigo Plugin class.
ON = 1                      # Constant for the on state.
OFF = 0                     # Constant for the off state.
ON_OFF = (u'off', u'on')    # Text values for the onOffState.
I2C = 0                     # Constant for an I2C interface.
SPI = 1                     # Constant for an SPI interface.

# Public dictionary of io device data.
# IODEV_DATA[ioDevType] = (ioDevClass, ioDevInterface):

IODEV_DATA = {'MCP23008': ('IOExpander', I2C), 'MCP23017': ('IOExpander', I2C),
              'MCP23S08': ('IOExpander', SPI), 'MCP23S17': ('IOExpander', SPI),
              'MCP3204':  ('ADC12',      SPI), 'MCP3208':  ('ADC12',      SPI),
              'MCP3422':  ('ADC18',      I2C), 'MCP3423':  ('ADC18',      I2C),
              'MCP3424':  ('ADC18',      I2C),
              'MCP4821':  ('DAC12',      SPI), 'MCP4822':  ('DAC12',      SPI),
              'pigpio':   ('PiGPIO',     None)}

# Public dictionary of io device instance objects.
# ioDevices[dev.id] = <ioDev instance object>:

ioDevices = {}  # Dictionary of io device instances.


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
        hexString += u'%02x ' % byte
    return hexString[:-1]


def start(dev):
    if ioDevices.get(dev.id):  # Return if already started.
        return

    ioDevType = dev.pluginProps[u'ioDevType']
    ioDevClass = IODEV_DATA[ioDevType][0]

    try:
        ioDev = globals()[ioDevClass](dev)
    except Exception as error:
        LOG.error(u'"%s" start error: %s', dev.name, error)
        dev.setErrorStateOnServer(u'start err')
        ioDev = ioDevices.get(dev.id)
        ioDev.stop()
        return

    LOG.info(u'"%s" started as a %s on %s',
             dev.name, dev.deviceTypeId, dev.address)
    dev.setErrorStateOnServer(None)
    ioDev.read()


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                             CLASS PiGPIODevice                              #
#                                                                             #
###############################################################################

class PiGPIODevice:
    """
    $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$  Fix Me  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    PiGPIODevice is an abstract base class used in defining all Pi GPIO device
    classes.  The __init__ method initializes pigpio host access and polling
    status variables.  Additional private methods initialize i2c and spi bus
    access and update the indigo device states for digital and analog devices.
    It has one public method (stop) that terminates the instance's pigpio
    connection.  PiGPIODevice subclasses must include specific device
    initialization in their __init__ methods and public read/write/stop methods
    as appropriate.
    """

    # PiGPIODeviceException:

    class PiGPIODeviceException(Exception):
        pass

    # Class constants:

    I2CBUS = 1  # Primary i2c bus.
    SPIBUS = 0  # Primary spi bus.
    IMAGE_SEL = (indigo.kStateImageSel.SensorOff,  # State image selectors.
                 indigo.kStateImageSel.SensorOn)

    # Public class attributes that can be changed by
    # pigpioDevices.PiGPIODevice.attribute = value.
    # These values are overridden by the indigo plugin class from the
    # plugin.prefs dictionary.

    monitorStatus = True
    statusInterval = 10
    checkSPI = False  # Perform SPI integrity check on each SPI read.

    # Class dictionary for pigpio resource management:

    _resources = {}  # self._resources[resourceId] = (resource, useCount).

    # Internal instance methods:

    def __init__(self, dev):

        # Add io device instance object to the public ioDevices dictionary:

        ioDevices[dev.id] = self

        # Set common internal instance attributes for all sub-classes:

        self._dev = dev
        self._callbackId = None
        self._interfaceId = None
        self._poll = dev.pluginProps[u'polling']
        self._pollCount = 0
        self._lastPoll = self._lastStatus = indigo.server.getTime()

        # Connect to the pigpio daemon.

        hostAddress = dev.pluginProps[u'hostAddress']
        portNumber = dev.pluginProps[u'portNumber']
        self._connectionId = u'%s:%s' % (hostAddress, portNumber)
        self._pi = self._getResource(self._connectionId)

        # Open a handle to access an i2c or spi device:

        ioDevType = dev.pluginProps[u'ioDevType']
        self._interface = IODEV_DATA[ioDevType][1]
        if self._interface is not None:
            if self._interface is I2C:
                i2cAddress = dev.pluginProps[u'i2cAddress']
                self._interfaceId = u'%s:%s' % (self._connectionId,
                                                i2cAddress)
            else:  # interface is SPI.
                spiChannel = dev.pluginProps[u'spiChannel']
                bitRate = dev.pluginProps[u'bitRate']
                self._interfaceId = u'%s:%s:%s' % (self._connectionId,
                                                   spiChannel, bitRate)
            self._handle = self._getResource(self._interfaceId)

        # Set common internal instance attributes by device type id:

        if dev.deviceTypeId == u'analogInput':
            self._sensorValue = dev.states.get(u'sensorValue', 0.0)
            self._scale = float(dev.pluginProps[u'scaling'])
            self._units = dev.pluginProps[u'units']
            self._adcChan = int(dev.pluginProps[u'adcChannel'])
            self._threshold = float(dev.pluginProps[u'changeThreshold'])
            self._lowLimitCheck = dev.pluginProps[u'lowLimitCheck']
            self._lowLimit = float(dev.pluginProps[u'lowLimit'])
            self._highLimitCheck = dev.pluginProps[u'highLimitCheck']
            self._highLimit = float(dev.pluginProps[u'highLimit'])

        elif dev.deviceTypeId == u'digitalInput':
            self._bitValue = dev.states[u'onOffState']
            self._inv = int(dev.pluginProps[u'invert'])

        else:  # dev.deviceTypeId == u'digitalOutput'
            self._bitValue = dev.states[u'onOffState']
            self._inv = 0  # Allow digital outputs to use read methods.
            dev.updateStateImageOnServer(self.IMAGE_SEL[dev.onState])

    def _getResource(self, resourceId):
        """
        Get and return a resource that is allocated by the pigpio daemon to
        access pigpio devices/services.  Resources are managed using a
        resources dictionary that is a class attribute with the following form:

        self._resources[resourceId] = (resource, useCount)

        There are three types of resources with the following resourceIds:

        pigpio connection resource - u'hostAddress:portNumber'
        i2c handle resource - u'hostAddress:portNumber:i2cAddress'
        spi handle resource - u'hostAddress:portNumber:spiChannel:bitRate'

        Because i2c and spi handles are unique only for a specific pigpio
        connection, the connection resource id is included in the i2c and spi
        resource ids to form a unique resource id over multiple connections.
        """
        resource, useCount = self._resources.get(resourceId, (None, 0))
        if resource is not None:
            useCount += 1
            self._resources[resourceId] = (resource, useCount)
        else:
            rIdSplit = resourceId.split(u':')
            rIdLen = len(rIdSplit)  # 2 ==> connection, 3 ==> i2c, 4 ==> spi.
            if rIdLen == 2:  # pigpio connection resource;
                # rIdSplit[0] = hostAddress, rIdSplit[1] = portNumber.
                resource = pigpio.pi(rIdSplit[0], rIdSplit[1])
                if not resource.connected:  # Connection failed.
                    resource.stop()
                    error = u'pigpio connection failed'
                    raise self.PiGPIODeviceException(error)
            elif rIdLen == 3:  # i2c resource; rIdSplit[2] = i2cAddress (hex)
                resource = self._pi.i2c_open(self.I2CBUS, int(rIdSplit[2],
                                                              base=16))
            else:  # rIdLen == 4 - spi resource;
                # rIdSplit[2] = spiChannel, rIdSplit[3] = bitRate (in kb/sec)
                resource = self._pi.spi_open(int(rIdSplit[2]),
                           500 * int(rIdSplit[3]), self.SPIBUS << 8)
            self._resources[resourceId] = resource, 1
        return resource

    def _releaseResource(self, resourceId):
        resource, useCount = self._resources.get(resourceId, (None, 0))
        if resource is not None:
            useCount -= 1
            if useCount > 0:
                self._resources[resourceId] = (resource, useCount)
            else:
                del self._resources[resourceId]
                resIdSplit = resourceId.split(u':')
                splitLen = len(resIdSplit)  # 2 ==> conn, 3 ==> i2c, 4 ==> spi.
                if splitLen == 2:  # pigpio connection resource.
                    resource.stop()
                elif splitLen == 3:  # i2c handle resource.
                    self._pi.i2c_close(resource)
                elif splitLen == 4:  # spi handle resource.
                    self._pi.spi_close(resource)

    def _getUiValue(self, value):
        """
        Generate a format string for the uiValue that shows 3 significant
        digits over a wide range of values.  Return a uiValue based on the
        format string and the object's self.units.
        """
        magnitude = abs(value)
        for i in range(3):
            if magnitude < (1, 10, 100)[i]:
                uiFormat = u'%.' + unicode(3 - i) + u'f %s'
                break
        else:
            uiFormat = u'%i %s'
        return uiFormat % (value, self._units)

    def _updateOnOffState(self, bit, logAll=True):
        """
        Set the onOffState based on the bit value.  If the state has changed,
        update it on the server and log it if logAll is not None.  If there is
        no change, log the unchanged state if logAll is True.
        """
        onOffState = ON_OFF[bit]
        if self._bitValue != bit:
            self._dev.updateStateOnServer(u'onOffState', onOffState,
                                          clearErrorState=False)
            self._dev.updateStateImageOnServer(self.IMAGE_SEL[bit])
            self._bitValue = bit
            if logAll is None:
                return
            LOG.info(u'"%s" update to %s', self._dev.name, onOffState)
        elif logAll:
            LOG.info(u'"%s" is %s', self._dev.name, onOffState)

    def _updateSensorValue(self, voltage, logAll=True):
        """
        Compute the sensor value from the adc voltage snd perform change
        detection and limit checks.  Compute the uiValue and update all device
        states on the server.  Log the sensor value if a change was detected or
        if logAll is True.
        """
        sensorValue = self._scale * voltage

        # Detect a percentage change in the sensor value and update the server
        # change detected state.

        refValue = self._sensorValue if self._sensorValue else 0.001
        percentChange = 100.0 * abs((sensorValue - self._sensorValue)
                                    / refValue)
        changeDetected = percentChange >= self._threshold
        self._dev.updateStateOnServer(u'changeDetected', changeDetected)
        self._sensorValue = sensorValue

        # Perform low and high limit checks and update the limit fault states
        # on the server.

        lowFault = False
        if self._lowLimitCheck:
            lowFault = sensorValue < self._lowLimit
            self._dev.updateStateOnServer(u'lowFault', lowFault)
            if lowFault:
                LOG.warning(u'"%s" low limit fault %.4f %s <  %.4f %s',
                            self._dev.name, sensorValue, self._units,
                            self._lowLimit, self._units)

        highFault = False
        if self._highLimitCheck:
            highFault = sensorValue > self._highLimit
            self._dev.updateStateOnServer(u'highFault', highFault)
            if highFault:
                LOG.warning(u'"%s" high limit fault %.4f %s > %.4f %s',
                            self._dev.name, sensorValue, self._units,
                            self._highLimit, self._units)

        # Update the state image to visually show limit check results and
        # execute any triggers.

        if self._lowLimitCheck or self._highLimitCheck:
            if lowFault or highFault:
                self._dev.updateStateImageOnServer(
                          indigo.kStateImageSel.SensorTripped)

                for trig in indigo.triggers.iter(u'self'):
                    if trig.pluginTypeId == u'limitFault' and trig.enabled:
                        trigName = trig.pluginProps[u'indigoTrigger']
                        if (trigName == u'anyFault'
                                or (trigName == u'lowFault' and lowFault)
                                or (trigName == u'highFault' and highFault)):
                            indigo.trigger.execute(trig.id)

            else:
                self._dev.updateStateImageOnServer(
                          indigo.kStateImageSel.SensorOn)
        else:
            self._dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)

        # Update the sensor value state and the uiValue.  Log the sensor value
        # if a change was detected or if logAll=True.

        uiValue = self._getUiValue(sensorValue)
        self._dev.updateStateOnServer(u'sensorValue', sensorValue,
                                      uiValue=uiValue, clearErrorState=False)
        if changeDetected:
            LOG.info(u'"%s" update to %.4f %s',
                     self._dev.name, sensorValue, self._units)
        elif logAll:
            LOG.info(u'"%s" is %.4f %s',
                     self._dev.name, sensorValue, self._units)

    def _read(self, logAll=True):  # Placeholder; must be overridden.
        pass

    def _write(self, value):  # Placeholder; must be overridden.
        pass

    # Public instance methods:

    def read(self, logAll=True):
        try:
            self._read(logAll=logAll)
        except Exception as error:
            LOG.error(u'"%s" read error: %s', self._dev.name, error)
            self.stop()
            self._dev.setErrorStateOnServer(u'read err')

    def write(self, value):
        try:
            self._write(value)
        except Exception as error:
            LOG.error(u'"%s" write error: %s', self._dev.name, error)
            self.stop()
            self._dev.setErrorStateOnServer(u'write err')

    def poll(self):
        if self._poll:
            now = indigo.server.getTime()
            secsSinceLast = (now - self._lastPoll).total_seconds()
            interval = float(self._dev.pluginProps[u'pollingInterval'])
            if secsSinceLast >= interval:
                logAll = self._dev.pluginProps[u'logAll']
                self.read(logAll=logAll)
                self._pollCount += 1
                self._lastPoll = now
                if self.monitorStatus:
                    secsSinceLast = (now - self._lastStatus).total_seconds()
                    interval = 60 * float(self.statusInterval)
                    if secsSinceLast >= interval:
                        averageInterval = secsSinceLast / self._pollCount
                        averageRate = 1 / averageInterval
                        LOG.info(u'"%s" average polling interval is %4.2f '
                                 u'secs, rate is %4.2f per sec',
                                 self._dev.name, averageInterval, averageRate)
                        self._pollCount = 0
                        self._lastStatus = now

    def stop(self):

        # Remove the io device from the io devices dictionary.

        if self._dev.id in ioDevices:
            del ioDevices[self._dev.id]
            LOG.debug(u'"%s" stopped', self._dev.name)

        try:
            # Cancel the device callback if needed.

            if self._callbackId:
                self._callbackId.cancel()  # Cancel gpio callback.

            # Release interface (i2c or spi), and connection resources.

            if self._interfaceId is not None:
                self._releaseResource(self._interfaceId)
            self._releaseResource(self._connectionId)

        except Exception as error:
            LOG.error(u'"%s" stop error: %s', self._dev.name, error)
            self._dev.setErrorStateOnServer(None)
            self._dev.setErrorStateOnServer(u'stop err')


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                                CLASS ADC12                                  #
#                                                                             #
###############################################################################

class ADC12(PiGPIODevice):

    # Class constant:

    VREF = 4.096  # Internal reference voltage (volts).

    # Internal instance methods:

    def __init__(self, dev):
        PiGPIODevice.__init__(self, dev)

        inputConfig = int(dev.pluginProps[u'inputConfiguration'])
        self._data = (0x04 | inputConfig << 1 | self._adcChan >> 2,
                      self._adcChan << 6, 0)

    def _read(self, logAll=True):

        nBytes1, bytes1 = self._pi.spi_xfer(self._handle, self._data)
        raw1 = (bytes1[1] & 0x0f) << 8 | bytes1[2]
        voltage1 = self.VREF * raw1 / 4096
        LOG.debug(u'"%s" read %s | %s | %s | %s | %s',
                  self._dev.name, hexStr(self._data), nBytes1,
                  hexStr(bytes1), raw1, voltage1)

        if self.checkSPI:  # Check SPI integrity.
            nBytes2, bytes2 = self._pi.spi_xfer(self._handle, self._data)
            raw2 = (bytes2[1] & 0x0f) << 8 | bytes2[2]
            voltage2 = self.VREF * raw2 / 4096
            LOG.debug(u'"%s" read %s | %s | %s | %s | %s',
                      self._dev.name, hexStr(self._data), nBytes2,
                      hexStr(bytes2), raw2, voltage2)
            refVoltage = voltage1 if voltage1 else 0.001
            percentChange = 100.0 * (abs((voltage1 - voltage2) / refVoltage))
            if percentChange >= self._threshold:
                LOG.warning(u'"%s" spi check different consecutive reads '
                            u'%.4f %.4f', self._dev.name, voltage1, voltage2)
                voltage1 = voltage2

        self._updateSensorValue(voltage1, logAll=logAll)


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                                CLASS ADC18                                  #
#                                                                             #
###############################################################################

class ADC18(PiGPIODevice):

    # Class constants:

    VREF = 2.048  # Internal reference voltage (volts).
    CONVERSION_MODE = 0  # One-shot conversion mode.
    NOT_READY = 0x80  # Not-ready bit.

    # Internal instance methods:

    def __init__(self, dev):
        PiGPIODevice.__init__(self, dev)

        self._res = int(dev.pluginProps[u'resolution'])
        resIndex = (self._res - 12) / 2
        gain = dev.pluginProps[u'gain']
        gainIndex = u'1248'.find(gain)
        self._config = (self.NOT_READY | self._adcChan << 5
                        | self.CONVERSION_MODE << 4
                        | resIndex << 2 | gainIndex)
        self._pga = float(gain)

    def _read(self, logAll=True):

        # Start the conversion in the single shot mode.

        self._pi.i2c_write_byte(self._handle, self._config)
        config = self._config & (~ self.NOT_READY)  # Clear the not-ready bit.
        numToRead = 3 if self._res < 18 else 4  # Number of bytes to read.

        # Read the conversion register until the not-ready bit is cleared in
        # the returned config byte (last byte received).

        numReads = 0
        while True:
            numBytes, bytes_ = self._pi.i2c_read_i2c_block_data(self._handle,
                                                                config,
                                                                numToRead)
            numReads += 1
            if not (bytes_[-1] & self.NOT_READY):
                break

        # Pack bytes from the returned bytearray into a single integer.

        raw = 0
        for byte in bytes_[:-1]:
            raw = raw << 8 | byte

        # Convert limited precision two's complement value to a full integer.

        msb = 1 << (self._res - 1)  # msb (sign bit) equal to (2 ** (res - 1)).
        if raw & msb:  # raw is negative.
            mask = (msb << 1) - 1  # Integer mask equal to (2 ** res - 1).
            raw = (~ raw + 1) & mask  # Magnitude of negative two's complement.
            raw = - 1 * raw  # Make it negative.

        voltage = self.VREF * raw / (msb * self._pga)
        LOG.debug(u'"%s" read %s | %s | %s | %s',
                  self._dev.name, numReads, hexStr(bytes_), raw, voltage)
        self._updateSensorValue(voltage, logAll=logAll)


###############################################################################
#                                                                             #
#                          MODULE pigpioDevices.py                            #
#                                CLASS DAC12                                  #
#                                                                             #
###############################################################################

class DAC12(PiGPIODevice):

    # Class constant:

    VREF = 2.048  # Internal reference voltage (volts).

    # Internal instance methods:

    def __init__(self, dev):
        PiGPIODevice.__init__(self, dev)

        self._sensorValue = dev.states.get(u'sensorValue', 0.0)
        self._scale = float(dev.pluginProps[u'scaling'])
        self._units = dev.pluginProps[u'units']
        self._dacChan = int(dev.pluginProps[u'dacChannel'])
        self._gain = int(dev.pluginProps[u'gain'])
        self._uiValue = None

    def _read(self, logAll=True):
        LOG.info(u'"%s" is %.4f %s', self._dev.name, self._sensorValue,
                 self._units)

    def _write(self, value):
        try:  # Check the write argument.
            sensorValue = float(value)
        except ValueError:
            LOG.warning(u'"%s" write argument %s is not a number; '
                        u'write ignored', self._dev.name, value)
            return

        # Convert the sensorValue to dac raw counts and write to the dac.

        voltage = sensorValue / self._scale
        raw = int(voltage * 4096 / (self.VREF * self._gain))
        if 0 <= raw < 4096:
            data = (self._dacChan << 7 | (self._gain & 1) << 5
                    | 0x10 | raw >> 8, raw & 0xff)
            nBytes = self._pi.spi_write(self._handle, data)
            LOG.debug(u'"%s" xfer %s | %s | %s | %s',
                      self._dev.name, voltage, raw, hexStr(data), nBytes)

        # Update and log the sensorValue state.

        uiValue = self._getUiValue(sensorValue)
        if sensorValue != self._sensorValue or uiValue != self._uiValue:
            self._sensorValue = sensorValue
            self._uiValue = uiValue
            self._dev.updateStateOnServer(u'sensorValue', sensorValue,
                                          uiValue=uiValue,
                                          clearErrorState=False)
            LOG.info(u'"%s" update to %.4f %s',
                     self._dev.name, sensorValue, self._units)
        else:
            LOG.info(u'"%s" is %.4f %s',
                     self._dev.name, sensorValue, self._units)


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

    PUD = {u'off': pigpio.PUD_OFF,  # GPIO pullup parameter definitions.
           u'up': pigpio.PUD_UP,
           u'down': pigpio.PUD_DOWN}

    # Internal instance methods:

    def __init__(self, dev):
        PiGPIODevice.__init__(self, dev)

        # Set internal instance attributes and configure gpio device.

        self._gpioNum = int(dev.pluginProps[u'gpioNumber'])
        self._callbackId = None

        if dev.deviceTypeId == u'digitalInput':
            self._pi.set_mode(self._gpioNum, pigpio.INPUT)
            pullup = dev.pluginProps[u'pullup']
            self._pi.set_pull_up_down(self._gpioNum, self.PUD[pullup])
            if dev.pluginProps[u'callback']:
                self._callbackId = self._pi.callback(self._gpioNum,
                                                     pigpio.EITHER_EDGE,
                                                     self._callback)
                self._priorTic = self._pi.get_current_tick()
                self._bounceFilter = dev.pluginProps[u'bounceFilter']
                self._bounceTime = int(dev.pluginProps[u'bounceTime'])
                self._logBounce = dev.pluginProps[u'logBounce']
                self._relayInterrupts = dev.pluginProps[u'relayInterrupts']
                if self._relayInterrupts:

                    # Initialize public instance attribute to collect
                    # interrupt device id's.  This list is populated by
                    # the __init__ methods of devices whose hardware
                    # interrupt output is connected to this GPIO input.

                    self.interruptDevices = []

        elif dev.deviceTypeId == u'digitalOutput':
            self._pi.set_mode(self._gpioNum, pigpio.OUTPUT)
            self._momentary = dev.pluginProps[u'momentary']
            self._delay = float(dev.pluginProps[u'turnOffDelay'])
            self._pwm = dev.pluginProps[u'pwm']
            if self._pwm:
                self._pi.set_PWM_range(self._gpioNum, 100)
                freq = int(dev.pluginProps[u'frequency'])
                self._pi.set_PWM_frequency(self._gpioNum, freq)
                self._duty = int(dev.pluginProps[u'dutyCycle'])

    def _callback(self, gpioNum, pinBit, tic):
        LOG.debug(u'"%s" callback %s %s %s µs',
                 self._dev.name, gpioNum, pinBit, tic)
        if pinBit in (ON, OFF):
            bit = pinBit ^ self._inv
            dt = pigpio.tickDiff(self._priorTic, tic)
            self._priorTic = tic

            # Apply the contact bounce filter, if requested.

            if self._bounceFilter:
                if dt < self._bounceTime:  # State is bouncing.
                    if self._logBounce:
                        LOG.warning(u'"%s" %s µs bounce; update to %s ignored',
                                    self._dev.name, dt, ON_OFF[bit])
                        return  # Ignore the bounced state change.

            logAll = True  # Default logging option for state update.

            # Relay interrupts, if requested.

            if self._relayInterrupts:
                if bit:  # Interrupt initiated; process it and set watchdog.
                    for devId in self.interruptDevices:
                        ioDev = ioDevices.get(devId)
                        if ioDev and ioDev.interrupt():  # ioDev interrupt.
                            break  # Only one match allowed per interrupt.
                    else:
                        LOG.warning(u'"%s" no match in interrupt devices list',
                                    self._dev.name)
                    self._pi.set_watchdog(self._gpioNum, 200)  # Set watchdog.
                else:  # Interrupt reset; log time and clear the watchdog.
                    LOG.debug(u'"%s" interrupt time is %s ms',
                              self._dev.name, dt / 1000)
                    self._pi.set_watchdog(self._gpioNum, 0)

                logAll = None  # Suppress logging for interrupt relay GPIO.

            # Update the onOff state.

            self._updateOnOffState(bit, logAll=logAll)

        else:  # Interrupt reset timeout.
            LOG.warning(u'"%s" interrupt reset timeout', self._dev.name)
            for ioDev in self.interruptDevices:
                ioDev.resetInterrupt()
            self._pi.set_watchdog(self._gpioNum, 0)  # Clear the watchdog timer

    def _read(self, logAll=True):
        bit = self._pi.read(self._gpioNum) ^ self._inv
        LOG.debug(u'"%s" read %s', self._dev.name, ON_OFF[bit])
        self._updateOnOffState(bit, logAll=logAll)
        return bit

    def _write(self, value):
        bit = int(value)
        if bit in (ON, OFF):
            self._pi.write(self._gpioNum, bit)
            LOG.debug(u'"%s" write %s', self._dev.name, ON_OFF[bit])
            self._updateOnOffState(bit)
            if bit:
                if self._pwm:
                    self._pi.set_PWM_dutycycle(self._gpioNum, self._duty)
                if self._momentary:
                    sleep(self._delay)
                    self._write(OFF)
        else:
            LOG.warning(u'"%s" invalid output value %s; write ignored',
                        self._dev.name, bit)


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

    REG_BASE_ADDR = {u'IODIR':   0x00,  # I/O Direction Register.
                     u'IPOL':    0x01,  # Input Polarity Register.
                     u'GPINTEN': 0x02,  # Interrupt-on-change Control Register.
                     u'DEFVAL':  0x03,  # Default Value Register.
                     u'INTCON':  0x04,  # Interrupt-on-Change Control Register.
                     u'IOCON':   0x05,  # I/O Configuration Register.
                     u'GPPU':    0x06,  # Pullup Resistor Config Register.
                     u'INTF':    0x07,  # Interrupt Flag Register.
                     u'INTCAP':  0x08,  # Interrupt Capture Register.
                     u'GPIO':    0x09,  # Port Register.
                     u'OLAT':    0x0a,  # Output Latch Register.
                     u'IOCONB0': 0x0b}  # IOCON register for port B in the
    #                                     BANK 0 mapping.

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

    def __init__(self, dev):
        PiGPIODevice.__init__(self, dev)

        # Define internal attributes.

        ioPort = dev.pluginProps[u'ioPort']
        self._offset = 0x10 if ioPort == u'b' else 0x00
        bitNum = int(dev.pluginProps[u'bitNumber'])
        self._mask = 1 << bitNum

        if self._interface is SPI:
            self._spiDevAddr = int(dev.pluginProps[u'spiDevAddress'], 16)

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

        self._writeRegister(u'IOCONB0', iocon)
        self._writeRegister(u'IOCON', iocon)

        # Configure the IODIR, IPOL, GPPU, DEFVAL, INTCON, and GPINTEN
        # registers by setting the specific bit for this device
        # (self._bitNum) in each register.  Leave all other bits unchanged.
        # These configuration changes use the self._updateRegister method
        # to read the register, change the appropriate bit, and then write
        # it back.

        if dev.deviceTypeId == u'digitalInput':
            self._updateRegister(u'IODIR', self.INPUT)
            self._updateRegister(u'IPOL', self._inv)  # Set input polarity.
            pullup = int(dev.pluginProps[u'pullup'] == u'up')
            self._updateRegister(u'GPPU', pullup)  # Set pullup option.
            self._updateRegister(u'DEFVAL', OFF)  # Clear default bit.
            self._updateRegister(u'INTCON', OFF)  # Interrupt on change.
            hwInt = int(dev.pluginProps[u'hardwareInterrupt'])
            if hwInt:

                # Setup the hardware interrupt relay as follows:
                # Get the interrupt relay io device object and append the
                # device id of this device to the object's interrupt
                # devices list.  If the interrupt relay io device is
                # missing, try starting it.  If it fails to start raise a
                # start exception for the this device.

                relayGPIO = dev.pluginProps[u'interruptRelayGPIO']
                relayDev = indigo.devices[relayGPIO]
                rioDev = ioDevices.get(relayDev.id)
                if not rioDev:
                    LOG.info(u'"%s" starting interrupt relay GPIO "%s"',
                             self._dev.name, relayGPIO)
                    start(relayDev)
                    rioDev = ioDevices.get(relayDev.id)
                    if not rioDev:
                        error = (u'interrupt relay GPIO "%s" not started'
                                 % relayGPIO)
                        raise self.PiGPIODeviceException(error)

                if self._dev.id not in rioDev.interruptDevices:
                    rioDev.interruptDevices.append(self._dev.id)
                for intDevId in rioDev.interruptDevices:
                    intDev = indigo.devices[intDevId]
                    LOG.debug(u'"%s" %s', intDev.name, intDevId)

            self._updateRegister(u'GPINTEN', hwInt)

        elif dev.deviceTypeId == u'digitalOutput':
            self._updateRegister(u'IODIR', self.OUTPUT)
            self._momentary = dev.pluginProps[u'momentary']
            self._delay = float(dev.pluginProps[u'turnOffDelay'])

    def _readRegister(self, register):
        registerAddress = self.REG_BASE_ADDR[register] + self._offset

        if self._interface is I2C:  # MCP230XX
            byte = self._pi.i2c_read_byte_data(self._handle, registerAddress)
            LOG.debug(u'"%s" readRegister %s %02x',
                      self._dev.name, register, byte)

        else:  # MCP23SXX
            data = (self._spiDevAddr << 1 | self.READ, registerAddress, 0)
            nBytes1, bytes1 = self._pi.spi_xfer(self._handle, data)
            byte = bytes1[-1]
            LOG.debug(u'"%s" readRegister %s %s | %s | %s',
                      self._dev.name, register, hexStr(data), nBytes1,
                      hexStr(bytes1))

            if self.checkSPI:  # Check SPI integrity.
                nBytes2, bytes2 = self._pi.spi_xfer(self._handle, data)
                byte2 = bytes2[-1]
                LOG.debug(u'"%s" readRegister %s %s | %s | %s',
                          self._dev.name, register, hexStr(data), nBytes2,
                          hexStr(bytes2))
                if byte != byte2:
                    LOG.warning(u'"%s" readRegister %s spi check unequal '
                                u'consecutive reads %02x %02x',
                                self._dev.name, register, byte, byte2)
                    byte = byte2
        return byte

    def _writeRegister(self, register, byte):
        registerAddress = self.REG_BASE_ADDR[register] + self._offset

        if self._interface is I2C:  # MCP230XX
            self._pi.i2c_write_byte_data(self._handle, registerAddress, byte)
            LOG.debug(u'"%s" writeRegister %s %02x',
                      self._dev.name, register, byte)

        else:  # MCP23SXX
            data = (self._spiDevAddr << 1 | self.WRITE, registerAddress, byte)
            nBytes = self._pi.spi_write(self._handle, data)
            LOG.debug(u'"%s" writeRegister %s %s | %s',
                      self._dev.name, register, hexStr(data), nBytes)

    def _updateRegister(self, register, bit):
        byte = self._readRegister(register)
        updatedByte = byte | self._mask if bit else byte & ~self._mask
        if updatedByte != byte:
            LOG.debug(u'"%s" updateRegister %s %02x | %s | %02x',
                      self._dev.name, register, byte, bit, updatedByte)
            self._writeRegister(register, updatedByte)

    def _read(self, logAll=True):
        byte = self._readRegister(u'GPIO')
        bit = 1 if byte & self._mask else 0
        self._updateOnOffState(bit, logAll=logAll)
        return bit

    def _write(self, value):
        bit = int(value)
        if bit in (ON, OFF):
            self._updateRegister(u'GPIO', bit)
            self._updateOnOffState(bit)
            if bit and self._momentary:
                sleep(self._delay)
                self._write(OFF)
        else:
            LOG.warning(u'"%s" invalid output value %s; write ignored',
                        self._dev.name, bit)

    # Public instance methods:

    def interrupt(self):

        try:
            # Read and check interrupt flag register for interrupt on this
            # device.

            intf = self._readRegister(u'INTF')
            if not intf & self._mask:
                return  # No match for this device.
            else:

                # Interrupt flag bit matches device bit; read interrupt capture
                # register and update the state.

                intcap = self._readRegister(u'INTCAP')
                bit = 1 if intcap & self._mask else 0
                LOG.debug(u'"%s" interrupt %02x | %02x | %s',
                          self._dev.name, intf, intcap, ON_OFF[bit])
                self._updateOnOffState(bit)

                # Check for lost interrupts.

                lostInterrupts = intf ^ self._mask
                if lostInterrupts:  # Any other bits set in interrupt flag reg?
                    LOG.warning(u'"%s" lost interrupts %02x',
                                self._dev.name, lostInterrupts)
                return True  # Signal an interrupt match.

        except Exception as error:
            self.stop()
            LOG.error(u'"%s" interrupt error: %s',
                      self._dev.name, error)
            self._dev.setErrorStateOnServer(None)
            self._dev.setErrorStateOnServer(u'int err')

    def resetInterrupt(self):
        try:
            self._readRegister(u'GPIO')  # Read port register to clear int.
        except Exception as error:
            self.stop()
            LOG.error(u'"%s" reset interrupt error: %s',
                      self._dev.name, error)
            self._dev.setErrorStateOnServer(None)
            self._dev.setErrorStateOnServer(u'int err')
