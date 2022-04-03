# coding=utf-8
###############################################################################
#                                                                             #
#                             MODULE plugin.py                                #
#                                                                             #
###############################################################################
"""
 PACKAGE:  Raspberry Pi General Purpose Input/Output for Indigo (Pi GPIO)
  MODULE:  plugin.py
   TITLE:  primary Python module in the Pi GPIO.indigoPlugin bundle
FUNCTION:  plugin.py defines the Plugin class, with standard methods that
           interface to the Indigo server and manage Indigo device objects.
           It instantiates a pigpioDevices object for each Indigo device object
           and invokes pigpioDevices object methods to perform detailed device
           functions.
   USAGE:  plugin.py is included in the Pi GPIO.indigoPlugin bundle and its
           methods are called by the Indigo server.
  AUTHOR:  papamac
 VERSION:  0.5.3
    DATE:  March 28, 2022


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


plugin.py DESCRIPTION:

plugin.py is the primary Python module in the Pi GPIO.indigoPlugin bundle.  It
defines the Plugin class whose methods provide entry points into the plugin
from the Indigo Plugin Host.  These methods, with access to the Indigo Server's
object database, manage the definition, validation, instantiation, and state
maintenance of Pi GPIO device objects.  For more details see the Plugin class
docstring (below) and the following Indigo documentation link:

<https://wiki.indigodomo.com/doku.php?id=indigo_2021.1_documentation:plugin_guide>


DEPENDENCIES/LIMITATIONS:

Some issues have been reported using the pigpio daemon running on a Raspberry
Pi 4 Model B (raspi4b).  The Pi GPIO plugin has been tested using several
raspi4b's with no problems except a minor issue with the spi clock rate. The
issue has been resolved with a (perhaps temporary) work-around that is
described in the pigpioDevices module docstring.


CHANGE LOG:

Major changes to the Pi GPIO plugin are described in the CHANGES.md file in the
top level PiGPIO folder.  Changes of lesser importance may be described in
individual module docstrings if appropriate.

v0.5.0  11/28/2021  Fully functional beta version with minimal documentation.
v0.5.1  11/29/2021  Force device stop/restart on a name change.
v0.5.2   1/19/2022  Use common IODEV_DATA dictionary to unambiguously identify
                    a device's interface type (I2C, SPI, or None)
v0.5.3   3/28/2022  Improve validation for low and high analog limits.

"""
###############################################################################
#                                                                             #
#                             MODULE plugin.py                                #
#                       DUNDERS, IMPORTS, AND GLOBALS                         #
#                                                                             #
###############################################################################

__author__ = u'papamac'
__version__ = u'0.5.3'
__date__ = u'3/28/2022'

from logging import getLogger, NOTSET

import indigo
import pigpio
import pigpioDevices

LOG = getLogger(u'Plugin')  # Standard logger
ON = 1   # Constant for the on state.
OFF = 0  # Constant for the off state.


###############################################################################
#                                                                             #
#                             MODULE plugin.py                                #
#                               CLASS Plugin                                  #
#                                                                             #
###############################################################################

class Plugin(indigo.PluginBase):
    """
    **************************** needs work ***********************************
    """

    ###########################################################################
    #                                                                         #
    #                               CLASS Plugin                              #
    #                                   PART                                  #
    #                                                                         #
    #                                   III                                   #
    #                                    I                                    #
    #                                    I                                    #
    #                                    I                                    #
    #                                    I                                    #
    #                                   III                                   #
    #                                                                         #
    #           INITIALIZATION, DEVICE START/STOP, AND RUN METHODS            #
    #                                                                         #
    # def __init__(self, pluginId, pluginDisplayName, pluginVersion,          #
    #              pluginPrefs):                                              #
    # def __del__(self)                                                       #
    # def startup(self)                                                       #
    # def deviceStartComm(dev)                                                #
    # def deviceStopComm(dev)                                                 #
    # def didDeviceCommPropertyChange(oldDev, newDev)                         #
    # def runConcurrentThread(self)                                           #
    #                                                                         #
    ###########################################################################

    # Internal methods:

    def __init__(self, pluginId, pluginDisplayName,
                 pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)

    def __del__(self):
        LOG.threaddebug(u'__del__ called')
        indigo.PluginBase.__del__(self)

    # Indigo plugin.py standard public instance methods:

    def startup(self):
        self.indigo_log_handler.setLevel(NOTSET)
        level = self.pluginPrefs[u'loggingLevel']
        LOG.setLevel(u'THREADDEBUG' if level == u'THREAD' else level)
        LOG.threaddebug(u'startup called')

        # Set pigpioDevices.PiGPIODevice class attributes from pluginPrefs.

        pigpioDevices.PiGPIODevice.monitorStatus = \
            self.pluginPrefs[u'monitorStatus']
        pigpioDevices.PiGPIODevice.statusInterval = \
            self.pluginPrefs[u'statusInterval']
        pigpioDevices.PiGPIODevice.checkSPI = self.pluginPrefs[u'checkSPI']

    @staticmethod
    def deviceStartComm(dev):
        LOG.threaddebug(u'deviceStartComm called "%s"', dev.name)
        pigpioDevices.start(dev)

    @staticmethod
    def deviceStopComm(dev):
        LOG.threaddebug(u'deviceStopComm called "%s"', dev.name)
        ioDev = pigpioDevices.ioDevices.get(dev.id)
        if ioDev:
            ioDev.stop()

    @staticmethod
    def didDeviceCommPropertyChange(oldDev, newDev):
        """
        By default, changing a device's plugin properties causes the Indigo
        server to stop the device and then restart it.  This method forces a
        stop/restart when either the pluginProps or the device name changes.
        Stopping/restarting on a name change avoids complications in the
        pigpioDevices PiGPIODevice class which uses the device name at the
        time of initialization.
        """
        devChanged = (oldDev.pluginProps != newDev.pluginProps
                      or oldDev.name != newDev.name)
        return devChanged

    def runConcurrentThread(self):
        LOG.threaddebug(u'runConcurrentThread called')
        while True:
            for dev in indigo.devices.iter(u'self'):
                ioDev = pigpioDevices.ioDevices.get(dev.id)
                if ioDev:
                    ioDev.poll()
            self.sleep(float(self.pluginPrefs[u'runLoopSleepTime']))

    ###########################################################################
    #                                                                         #
    #                               CLASS Plugin                              #
    #                                   PART                                  #
    #                                                                         #
    #                                III   III                                #
    #                                 I     I                                 #
    #                                 I     I                                 #
    #                                 I     I                                 #
    #                                 I     I                                 #
    #                                III   III                                #
    #                                                                         #
    #                      CONFIG UI VALIDATION METHODS                       #
    #                                                                         #
    # def validatePrefsConfigUi(self, valuesDict)                             #
    # def validateDeviceConfigUi(self, valuesDict, typeId, devId)             #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def validatePrefsConfigUi(valuesDict):
        LOG.threaddebug(u'validatePrefsConfigUi called')
        errors = indigo.Dict()

        # Set logging level.

        level = valuesDict[u'loggingLevel']
        LOG.setLevel(u'THREADDEBUG' if level == u'THREAD' else level)

        # Validate status interval and run loop sleep time.

        try:
            status = float(valuesDict[u'statusInterval'])
        except ValueError:
            errors[u'statusInterval'] = u'Status interval must be a number.'
        else:
            if status < 0.0:
                errors[u'pollingInterval'] = (u'Status interval must be '
                                              u'non-negative.')
        try:
            sleep = float(valuesDict[u'runLoopSleepTime'])
        except ValueError:
            errors[u'runLoopSleepTime'] = (u'Run loop sleep time must be a '
                                           u'number.')
        else:
            if sleep < 0.0:
                errors[u'runLoopSleepTime'] = (u'Run loop sleep time must be '
                                               u'non-negative.')

        if errors:
            return False, valuesDict, errors  # Return with errors.

        else:

            # No errors; update pigpioDevices.PiGPIODevice class attributes
            # from the valuesDict.

            pigpioDevices.PiGPIODevice.monitorStatus = \
                valuesDict[u'monitorStatus']
            pigpioDevices.PiGPIODevice.statusInterval = \
                valuesDict[u'statusInterval']
            pigpioDevices.PiGPIODevice.checkSPI = valuesDict[u'checkSPI']

            return True, valuesDict  # Return without errors.

    @staticmethod
    def validateDeviceConfigUi(valuesDict, typeId, devId):
        dev = indigo.devices[devId]
        LOG.threaddebug(u'validateDeviceConfigUi called "%s"; '
                        u'configured = %s', dev.name, dev.configured)
        errors = indigo.Dict()

        ioDevType = valuesDict[u'ioDevType']
        interface = pigpioDevices.IODEV_DATA[ioDevType][1]

        # Validation of common properties for all device types:

        hostAddress = valuesDict[u'hostAddress']
        try:  # Check portNumber.
            port = int(valuesDict[u'portNumber'])
        except ValueError:
            errors[u'portNumber'] = u'Port number must be an integer.'
        else:
            if 1024 <= port <= 65535:
                pi = pigpio.pi(hostAddress, port)
                if not pi.connected:
                    error = u'Connection failed.'
                    errors[u'hostAddress'] = errors[u'portNumber'] = error
                pi.stop()
            else:
                errors[u'portNumber'] = u'Port number must be in range.'

        pollingInterval = valuesDict.get(u'pollingInterval')
        if pollingInterval:  # Skip if pollingInterval not in ConfigUi.
            try:  # Check pollingInterval.
                poll = float(pollingInterval)
            except ValueError:
                error = u'Polling interval must be a number.'
                errors[u'pollingInterval'] = error
            else:
                if poll < 0.0:
                    error = u'Polling interval must be non-negative.'
                    errors[u'pollingInterval'] = error

        # Validation of properties for SPI devices:

        if interface is pigpioDevices.SPI:
            try:  # Check bitRate.
                rate = float(valuesDict[u'bitRate'])
            except ValueError:
                errors[u'bitRate'] = u'Bit Rate must be a number.'
            else:
                if not 100 <= rate <= 10000:
                    errors[u'bitRate'] = u'Bit Rate must be in range.'

        # Validation of properties for specific typeIds:

        if typeId == u'analogInput':

            try:  # Check scaling.
                float(valuesDict[u'scaling'])
            except ValueError:
                errors[u'scaling'] = u'Scaling Factor must be a number.'

            try:  # Check changeThreshold.
                threshold = float(valuesDict[u'changeThreshold'])
            except ValueError:
                error = u'Change Threshold must be a number.'
                errors[u'changeThreshold'] = error
            else:
                if threshold < 0.0:
                    error = u'Change Threshold must be non-negative.'
                    errors[u'changeThreshold'] = error

            lowLimit = highLimit = None
            try:  # Check lowLimit.
                lowLimit = float(valuesDict[u'lowLimit'])
            except ValueError:
                errors[u'lowLimit'] = u'Low Limit must be a number.'

            try:  # Check highLimit.
                highLimit = float(valuesDict[u'highLimit'])
            except ValueError:
                errors[u'highLimit'] = u'High Limit must be a number.'

            # When both are specified, check for lowLimit < highLimit.
            if (valuesDict[u'lowLimitCheck'] and lowLimit
                    and valuesDict[u'highLimitCheck'] and highLimit
                    and lowLimit > highLimit):
                error = u'Low limit must be less than high limit.'
                errors[u'lowLimit'] = error
                errors[u'highLimit'] = error

        elif typeId == u'analogOutput':

            try:  # Check scaling.
                float(valuesDict[u'scaling'])
            except ValueError:
                errors[u'scaling'] = u'Scaling Factor must be a number.'

        elif typeId == u'digitalInput':

            pullup1 = valuesDict[u'pullup1']
            pullup2 = valuesDict[u'pullup2']
            valuesDict[u'pullup'] = pullup1 if pullup1 != u'off' else pullup2

            if valuesDict[u'bounceFilter'] and valuesDict[u'relayInterrupts']:
                error = u'Bounce Filter must be disabled to relay interrupts.'
                errors[u'bounceFilter'] = error
                errors[u'relayInterrupts'] = error

            try:  # Check bounceTime.
                bounceTime = float(valuesDict[u'bounceTime'])
            except ValueError:
                errors[u'bounceTime'] = u'Bounce Time must be a number.'
            else:
                if bounceTime < 0.0:
                    error = u'Bounce Time must be non-negative.'
                    errors[u'changeThreshold'] = error

            if (valuesDict[u'hardwareInterrupt']
                    and not valuesDict[u'interruptRelayGPIO']):
                error = u'Must select an Interrupt Relay GPIO.'
                errors[u'interruptRelayGPIO'] = error

        elif typeId == u'digitalOutput':

            try:  # Check turnOffDelay.
                delay = float(valuesDict[u'turnOffDelay'])
            except ValueError:
                error = u'Turn-off Delay must be a number.'
                errors[u'turnOffDelay'] = error
            else:
                if not 0 <= delay <= 10:
                    error = u'Turn-off Delay must be in range.'
                    errors[u'turnOffDelay'] = error

            try:  # Check frequency.
                freq = int(valuesDict[u'frequency'])
            except ValueError:
                errors[u'frequency'] = u'Frequency must be an integer.'
            else:
                if not 1 <= freq <= 8000:
                    errors[u'frequency'] = u'Frequency must be in range.'

            error = u'Duty Cycle must be an integer percentage (0-100%)'
            try:  # # Check dutyCycle.
                duty = int(valuesDict[u'dutyCycle'])
            except ValueError:
                errors[u'dutyCycle'] = error
            else:
                if not 0 <= duty <= 100:
                    errors[u'dutyCycle'] = error

        if errors:  # Return if there were errors.
            return False, valuesDict, errors

        else:  # No errors so far; continue processing.

            # Compute the host id.

            hostId = valuesDict[u'hostId']
            if not hostId:
                split1 = hostAddress.split(u'.', 1)
                split2 = split1[0].split(u'-')
                if len(split2) > 1:
                    hostId = split2[-1]
                else:
                    hostId = u'pi'

            # Incrementally build the device address string.

            address = hostId
            if ioDevType == u'pigpio':  # gpio device.
                address += u'.g' + valuesDict[u'gpioNumber']
            else:
                if interface is pigpioDevices.I2C:  # i2c device.
                    address += u'.i' + valuesDict[u'i2cAddress'][2:]

                elif interface is pigpioDevices.SPI:  # spi device.
                    address += u'.s' + valuesDict[u'spiChannel']
                    if u'S' in ioDevType:
                        spiDevAddress4 = valuesDict[u'spiDevAddress4']
                        spiDevAddress8 = valuesDict[u'spiDevAddress8']
                        spiDevAddress = max(spiDevAddress4, spiDevAddress8)
                        valuesDict[u'spiDevAddress'] = spiDevAddress
                        address += u':%s' % spiDevAddress[2:]

                if typeId == u'analogInput':
                    adcChannel2 = valuesDict[u'adcChannel2']
                    adcChannel4 = valuesDict[u'adcChannel4']
                    adcChannel8 = valuesDict[u'adcChannel8']
                    adcChannel = max(adcChannel2, adcChannel4, adcChannel8)
                    valuesDict[u'adcChannel'] = adcChannel
                    address += u'.a' + adcChannel

                elif typeId == u'analogOutput':
                    dacChannel = valuesDict[u'dacChannel']
                    dacChannel2 = valuesDict[u'dacChannel2']
                    dacChannel = max(dacChannel, dacChannel2)
                    valuesDict[u'dacChannel'] = dacChannel
                    address += u'.d' + dacChannel

                else:  # digitalInput or digitalOutput
                    address += u'.g'
                    if u'17' in ioDevType:
                        address += valuesDict[u'ioPort']
                    address += valuesDict[u'bitNumber']

            # Check the device address for uniqueness.

            addrProps = (u'hostAddress', u'hostId',         u'gpioNumber',
                         u'spiChannel',  u'spiDevAddress4', u'spiDevAddress8',
                         u'i2cAddress',  u'adcChannel2',    u'adcChannel4'
                         u'adcChannel8', u'dacChannel2',    u'ioPort',
                         u'bitNumber')

            for dev in indigo.devices.iter(u'self'):
                if dev.id != devId:
                    if dev.address == address:  # address is not unique.
                        error = u'Device address %s not unique.'
                        for prop in addrProps:
                            if valuesDict.get(prop):
                                errors[prop] = error
                        return False, valuesDict, errors
            else:
                valuesDict[u'address'] = address  # address is unique.
                return True, valuesDict

    ###########################################################################
    #                                                                         #
    #                               CLASS Plugin                              #
    #                                   PART                                  #
    #                                                                         #
    #                             III   III   III                             #
    #                              I     I     I                              #
    #                              I     I     I                              #
    #                              I     I     I                              #
    #                              I     I     I                              #
    #                             III   III   III                             #
    #                                                                         #
    #                       CONFIG UI CALLBACK METHOD                         #
    #                                                                         #
    # def getGPIORelayDevices(*args)                                          #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def getGPIORelayDevices(*args):
        devices = []
        for dev in indigo.devices.iter(u'self'):
            if dev.deviceTypeId == u'digitalInput':
                if (dev.pluginProps[u'ioDevType'] == u'pigpio'
                        and dev.pluginProps[u'relayInterrupts']):
                    devices.append(dev.name)
        return sorted(devices)

    ###########################################################################
    #                                                                         #
    #                               CLASS Plugin                              #
    #                                   PART                                  #
    #                                                                         #
    #                             III   III      III                          #
    #                              I     I       I                            #
    #                              I      I     I                             #
    #                              I       I   I                              #
    #                              I        I I                               #
    #                             III       III                               #
    #                                                                         #
    #                         ACTION CALLBACK METHODS                         #
    #                                                                         #
    # def read(pluginAction)                                                  #
    # def write(pluginAction)                                                 #
    # def actionControlDevice(self, action, dev)                              #
    # def actionControlUniversal(self, action, dev)                           #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def read(pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        LOG.threaddebug(u'read called "%s"', dev.name)
        ioDev = pigpioDevices.ioDevices.get(dev.id)
        if ioDev:
            ioDev.read()

    @staticmethod
    def write(pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        LOG.threaddebug(u'write called "%s"', dev.name)
        if dev.deviceTypeId in (u'analogOutput', u'digitalOutput'):
            value = pluginAction.props[u'value']
            ioDev = pigpioDevices.ioDevices.get(dev.id)
            if ioDev:
                ioDev.write(value)

    def actionControlDevice(self, action, dev):
        LOG.threaddebug(u'actionControlDevice called "%s"', dev.name)
        if dev.deviceTypeId == u'digitalOutput':
            if action.deviceAction == indigo.kDeviceAction.TurnOn:
                bit = ON
            elif action.deviceAction == indigo.kDeviceAction.TurnOff:
                bit = OFF
            elif action.deviceAction == indigo.kDeviceAction.Toggle:
                bit = OFF if dev.onState else ON
            else:
                return
            ioDev = pigpioDevices.ioDevices.get(dev.id)
            if ioDev:
                ioDev.write(bit)

    def actionControlUniversal(self, action, dev):
        LOG.threaddebug(u'actionControlUniversal called "%s"', dev.name)
        if action.deviceAction == indigo.kUniversalAction.RequestStatus:
            ioDev = pigpioDevices.ioDevices.get(dev.id)
            if ioDev:
                ioDev.read()
