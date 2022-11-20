# coding=utf-8
###############################################################################
#                                                                             #
#                             MODULE plugin.py                                #
#                                                                             #
###############################################################################
"""
 PACKAGE:  Raspberry Pi General Purpose Input/Output for Indigo
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
 VERSION:  0.6.0
    DATE:  November 20, 2022


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
v0.5.7   7/20/2022  Update for Python 3.
v0.5.8   9/11/2022  Add support for Docker Pi Relay devices and 8/10-bit dacs.
v0.5.9  10/12/2022  Add glitch filter option for built-in GPIO inputs.
v0.6.0  11/20/2022  Use properties in pluginProps and pluginPrefs directly
                    without duplicating them as ioDev instance objects.
"""
###############################################################################
#                                                                             #
#                             MODULE plugin.py                                #
#                       DUNDERS, IMPORTS, AND GLOBALS                         #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '0.6.0'
__date__ = '11/20/2022'

from logging import getLogger, NOTSET

import indigo
import pigpio
import pigpioDevices

LOG = getLogger('Plugin')  # Standard logger
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
        LOG.threaddebug('__del__ called')
        indigo.PluginBase.__del__(self)

    # Indigo plugin.py standard public instance methods:

    def startup(self):
        self.indigo_log_handler.setLevel(NOTSET)
        level = self.pluginPrefs['loggingLevel']
        LOG.setLevel('THREADDEBUG' if level == 'THREAD' else level)
        LOG.threaddebug('startup called')

    def deviceStartComm(self, dev):
        LOG.threaddebug('deviceStartComm called "%s"', dev.name)
        pigpioDevices.start(self, dev)

    @staticmethod
    def deviceStopComm(dev):
        LOG.threaddebug('deviceStopComm called "%s"', dev.name)
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
        LOG.threaddebug('runConcurrentThread called')
        while True:
            for dev in indigo.devices.iter('self'):
                ioDev = pigpioDevices.ioDevices.get(dev.id)
                if ioDev:
                    ioDev.poll()
            self.sleep(float(self.pluginPrefs['runLoopSleepTime']))

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
        LOG.threaddebug('validatePrefsConfigUi called')
        errors = indigo.Dict()

        # Set logging level.

        loggingLevel = valuesDict['loggingLevel']
        LOG.setLevel('THREADDEBUG' if loggingLevel == 'THREAD'
                     else loggingLevel)

        # Validate status interval and run loop sleep time.

        try:
            statusInterval = float(valuesDict['statusInterval'])
        except ValueError:
            errors['statusInterval'] = 'Status interval must be a number.'
        else:
            if statusInterval < 0.0:
                errors['statusInterval'] = ('Status interval must be '
                                            'non-negative.')
        try:
            runLoopSleepTime = float(valuesDict['runLoopSleepTime'])
        except ValueError:
            errors['runLoopSleepTime'] = ('Run loop sleep time must be a '
                                          'number.')
        else:
            if runLoopSleepTime < 0.0:
                errors['runLoopSleepTime'] = ('Run loop sleep time must be '
                                              'non-negative.')

        # Return with or without errors.

        return not bool(errors), valuesDict, errors

    @staticmethod
    def validateDeviceConfigUi(valuesDict, typeId, devId):
        dev = indigo.devices[devId]
        LOG.threaddebug('validateDeviceConfigUi called "%s"; '
                        'configured = %s', dev.name, dev.configured)
        errors = indigo.Dict()

        ioDevType = valuesDict['ioDevType']
        ioDevInterface = pigpioDevices.IODEV_DATA[ioDevType][1]

        # Validation of common properties for all device types:

        hostAddress = valuesDict['hostAddress']
        try:  # Check portNumber.
            portNumber = int(valuesDict['portNumber'])
        except ValueError:
            errors['portNumber'] = 'Port number must be an integer.'
        else:
            if 1024 <= portNumber <= 65535:
                pi = pigpio.pi(hostAddress, portNumber)
                if not pi.connected:
                    error = 'Connection failed.'
                    errors['hostAddress'] = errors['portNumber'] = error
                pi.stop()
            else:
                errors['portNumber'] = 'Port number must be in range.'

        try:  # Check pollingInterval.
            pollingInterval = float(valuesDict['pollingInterval'])
        except ValueError:
            error = 'Polling/logging interval must be a number.'
            errors['pollingInterval'] = error
        else:
            if pollingInterval < 0.0:
                error = 'Polling interval must be non-negative.'
                errors['pollingInterval'] = error

        # Validation of properties for SPI devices:

        if ioDevInterface is pigpioDevices.SPI:
            try:  # Check bitRate.
                bitRate = float(valuesDict['bitRate'])
            except ValueError:
                errors['bitRate'] = 'Bit Rate must be a number.'
            else:
                if not 100 <= bitRate <= 10000:
                    errors['bitRate'] = 'Bit Rate must be in range.'

        # Validation of properties for specific typeIds:

        if typeId == 'analogInput':

            try:  # Check scaling factor.
                float(valuesDict['scaling'])
            except ValueError:
                errors['scaling'] = 'Scaling Factor must be a number.'

            try:  # Check changeThreshold.
                changeThreshold = float(valuesDict['changeThreshold'])
            except ValueError:
                error = 'Change Threshold must be a number.'
                errors['changeThreshold'] = error
            else:
                if changeThreshold < 0.0:
                    error = 'Change Threshold must be non-negative.'
                    errors['changeThreshold'] = error

            lowLimit = highLimit = None
            try:  # Check lowLimit.
                lowLimit = float(valuesDict['lowLimit'])
            except ValueError:
                errors['lowLimit'] = 'Low Limit must be a number.'

            try:  # Check highLimit.
                highLimit = float(valuesDict['highLimit'])
            except ValueError:
                errors['highLimit'] = 'High Limit must be a number.'

            # When both are specified, check for lowLimit < highLimit.
            if (valuesDict['lowLimitCheck'] and lowLimit
                    and valuesDict['highLimitCheck'] and highLimit
                    and lowLimit > highLimit):
                error = 'Low limit must be less than high limit.'
                errors['lowLimit'] = error
                errors['highLimit'] = error

        elif typeId == 'analogOutput':

            try:  # Check scaling factor.
                float(valuesDict['scaling'])
            except ValueError:
                errors['scaling'] = 'Scaling Factor must be a number.'

        elif typeId == 'digitalInput':

            pullup1 = valuesDict['pullup1']
            pullup2 = valuesDict['pullup2']
            valuesDict['pullup'] = pullup1 if pullup1 != 'off' else pullup2

            if valuesDict['bounceFilter'] and valuesDict['relayInterrupts']:
                error = 'Bounce Filter must be disabled to relay interrupts.'
                errors['bounceFilter'] = error
                errors['relayInterrupts'] = error

            try:  # Check bounceTime.
                bounceTime = float(valuesDict['bounceTime'])
            except ValueError:
                errors['bounceTime'] = 'Bounce Time must be a number.'
            else:
                if bounceTime < 0.0:
                    error = 'Bounce Time must be non-negative.'
                    errors['changeThreshold'] = error

            if (valuesDict['hardwareInterrupt']
                    and not valuesDict['interruptRelayGPIO']):
                error = 'Must select an Interrupt Relay GPIO.'
                errors['interruptRelayGPIO'] = error

        elif typeId == 'digitalOutput':

            try:  # Check turnOffDelay.
                turnOffDelay = float(valuesDict['turnOffDelay'])
            except ValueError:
                error = 'Turn-off Delay must be a number.'
                errors['turnOffDelay'] = error
            else:
                if not 0 <= turnOffDelay <= 10:
                    error = 'Turn-off Delay must be in range.'
                    errors['turnOffDelay'] = error

            try:  # Check frequency.
                frequency = int(valuesDict['frequency'])
            except ValueError:
                errors['frequency'] = 'Frequency must be an integer.'
            else:
                if not 1 <= frequency <= 8000:
                    errors['frequency'] = 'Frequency must be in range.'

            error = 'Duty Cycle must be an integer percentage (0-100%)'
            try:  # # Check dutyCycle.
                dutyCycle = int(valuesDict['dutyCycle'])
            except ValueError:
                errors['dutyCycle'] = error
            else:
                if not 0 <= dutyCycle <= 100:
                    errors['dutyCycle'] = error

        if errors:  # Return if there were errors.
            return False, valuesDict, errors

        else:  # No errors so far; continue processing.

            # Compute the host id.

            hostId = valuesDict['hostId']
            if not hostId:
                split1 = hostAddress.split('.', 1)
                split2 = split1[0].split('-')
                if len(split2) > 1:
                    hostId = split2[-1]
                else:
                    hostId = 'pi'

            # Incrementally build the device address string.

            address = hostId
            if ioDevType == 'pigpio':  # gpio device.
                address += '.g' + valuesDict['gpioNumber']
            else:
                if ioDevInterface is pigpioDevices.I2C:  # i2c device.
                    i2cAddress = valuesDict['i2cAddress8']
                    if ioDevType == 'dkrPiRly':
                        i2cAddress = valuesDict['i2cAddress4']
                    valuesDict['i2cAddress'] = i2cAddress
                    address += '.i' + i2cAddress[2:]

                elif ioDevInterface is pigpioDevices.SPI:  # spi device.
                    address += '.s' + valuesDict['spiChannel']
                    if 'S' in ioDevType:
                        spiDevAddress4 = valuesDict['spiDevAddress4']
                        spiDevAddress8 = valuesDict['spiDevAddress8']
                        spiDevAddress = max(spiDevAddress4, spiDevAddress8)
                        valuesDict['spiDevAddress'] = spiDevAddress
                        address += ':%s' % spiDevAddress[2:]

                if typeId == 'analogInput':
                    adcChannel2 = valuesDict['adcChannel2']
                    adcChannel4 = valuesDict['adcChannel4']
                    adcChannel8 = valuesDict['adcChannel8']
                    adcChannel = max(adcChannel2, adcChannel4, adcChannel8)
                    valuesDict['adcChannel'] = adcChannel
                    address += '.a' + adcChannel

                elif typeId == 'analogOutput':
                    dacChannel1 = valuesDict['dacChannel1']
                    dacChannel2 = valuesDict['dacChannel2']
                    dacChannel = max(dacChannel1, dacChannel2)
                    valuesDict['dacChannel'] = dacChannel
                    address += '.d' + dacChannel

                else:  # digitalInput or digitalOutput
                    if ioDevType == 'dkrPiRly':  # Docker Pi Relay device.
                        address += '.r' + valuesDict['relayNumber']
                    else:
                        address += '.g'
                        if '17' in ioDevType:
                            address += valuesDict['ioPort']
                        address += valuesDict['bitNumber']

            # Check the device address for uniqueness.

            addrProps = ('hostAddress',  'hostId',           'gpioNumber',
                         'i2cAddress4',  'i2cAddress8',
                         'spiChannel2',  'spiDevAddress4',  'spiDevAddress8',
                         'adcChannel2',  'adcChannel4',     'adcChannel8',
                         'dacChannel2',  'ioPort',          'bitNumber',
                         'relayNumber')

            for dev in indigo.devices.iter('self'):
                if dev.id != devId:
                    if dev.address == address:  # address is not unique.
                        error = 'Device address %s not unique.' % address
                        for prop in addrProps:
                            if valuesDict.get(prop):
                                errors[prop] = error
                        return False, valuesDict, errors
            else:
                valuesDict['address'] = address  # address is unique.
                LOG.debug(valuesDict)
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
        for dev in indigo.devices.iter('self'):
            if dev.deviceTypeId == 'digitalInput':
                if (dev.pluginProps['ioDevType'] == 'pigpio'
                        and dev.pluginProps['relayInterrupts']):
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
        LOG.threaddebug('read called "%s"', dev.name)
        ioDev = pigpioDevices.ioDevices.get(dev.id)
        if ioDev:
            ioDev.read()

    @staticmethod
    def write(pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        LOG.threaddebug('write called "%s"', dev.name)
        if dev.deviceTypeId in ('analogOutput', 'digitalOutput'):
            value = pluginAction.props['value']
            ioDev = pigpioDevices.ioDevices.get(dev.id)
            if ioDev:
                ioDev.write(value)

    def actionControlDevice(self, action, dev):
        LOG.threaddebug('actionControlDevice called "%s"', dev.name)
        if dev.deviceTypeId == 'digitalOutput':
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
        LOG.threaddebug('actionControlUniversal called "%s"', dev.name)
        if action.deviceAction == indigo.kUniversalAction.RequestStatus:
            ioDev = pigpioDevices.ioDevices.get(dev.id)
            if ioDev:
                ioDev.read()
