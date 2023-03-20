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
 VERSION:  0.8.0
    DATE:  March 20, 2023


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
v0.7.0   2/14/2023  (1) Update the device ConfigUi validation for new/changed
                    fields in Devices.xml.
                    (2) Implement display state selection for analog input and
                    analog output devices.
                    (3) Add callback methods for analog output turnOn/turnOff
                    actions.
v0.7.2    3/5/2023  (1) Refactor and simplify code for pigpio resource
                    management, exception management, and interrupt processing.
                    (2) Add conditional logging by message type.
v0.8.0   3/20/2023  (1) Change the device types for analog input and analog
                    output devices from custom types back to sensor and relay
                    types respectively.  Remove code to change the display
                    state id for custom devices.
                    (2) Add a callback method for the analog/digital output
                    toggle actions.
                    (3) Refactor/simplify all the action callback methods.

"""
###############################################################################
#                                                                             #
#                             MODULE plugin.py                                #
#                   DUNDERS, IMPORTS, and GLOBAL Constants                    #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '0.8.0'
__date__ = '3/20/2023'

from logging import NOTSET, getLogger

import indigo

import conditionalLogging
from conditionalLogging import LI
import pigpio
from pigpioDevices import I2C, SPI, IODEV_DATA
from pigpioDevices import ioDevices, ioDevCounts, resources, start

L = getLogger('Plugin')    # Standard logger
ON, OFF = (1, 0)           # on/off states.


###############################################################################
#                                                                             #
#                             MODULE plugin.py                                #
#                               CLASS Plugin                                  #
#                                                                             #
###############################################################################

class Plugin(indigo.PluginBase):
    """
    The Plugin class is a collection of standard Indigo plugin methods that are
    needed to manage multiple door opener devices.  It is segmented into four
    parts for readability:

    I   STANDARD INDIGO INITIALIZATION, STARTUP, AND RUN/STOP METHODS,
    II  CONFIG UI VALIDATION METHODS,
    III CONFIG UI CALLBACK METHODS, and
    IV  ACTION CALLBACK METHODS
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
    # def didDeviceCommPropertyChange(oldDev, newDev)                         #
    # def deviceStartComm(dev)                                                #
    # def deviceStopComm(dev)                                                 #
    # def runConcurrentThread(self)                                           #
    #                                                                         #
    ###########################################################################

    def __init__(self, pluginId, pluginDisplayName,
                 pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)

    def __del__(self):
        L.threaddebug('__del__ called')
        indigo.PluginBase.__del__(self)

    def startup(self):

        # Set logging level.

        self.indigo_log_handler.setLevel(NOTSET)
        level = self.pluginPrefs['loggingLevel']
        L.setLevel('THREADDEBUG' if level == 'THREAD' else level)
        L.threaddebug('startup called')

        # Set the LOGGING_MESSAGE_TYPES list in the conditionalLogging module.

        lmt =  [item for item in self.pluginPrefs['loggingMessageTypes']]
        conditionalLogging.LOGGING_MESSAGE_TYPES = lmt

        # Delete interrupt devices list in pluginProps.

        for dev in indigo.devices.iter('self'):
            if dev.pluginProps.get('interruptDevices'):
                props = dev.pluginProps
                del props['interruptDevices']
                dev.replacePluginPropsOnServer(props)

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

    def deviceStartComm(self, dev):
        L.threaddebug('deviceStartComm called "%s"', dev.name)
        start(self, dev)

    @staticmethod
    def deviceStopComm(dev):
        L.threaddebug('deviceStopComm called "%s"', dev.name)
        ioDev = ioDevices.get(dev.id)
        if ioDev:
            ioDev.stop()

    def runConcurrentThread(self):
        L.threaddebug('runConcurrentThread called')

        # Summarize and log the numbers of pigpio devices started.

        LI.startStop('')
        LI.startStop('pigpio device startup summary:')
        LI.startStop('raspi host  total  gpio  i2c   spi')
        allPi = 3 * [0]
        for piId in ioDevCounts:
            piTot = sum(ioDevCounts[piId])
            LI.startStop('%10s   %3i   %3i   %3i   %3i', piId, piTot,
                         *ioDevCounts[piId])
            allPi = list(map(sum, zip(allPi, ioDevCounts[piId], strict=True)))
        allTot = sum(allPi)
        LI.startStop('%10s   %3i   %3i   %3i   %3i', 'totals', allTot, *allPi)
        LI.startStop('')

        # Commence io device polling.

        while True:
            for dev in indigo.devices.iter('self'):
                ioDev = ioDevices.get(dev.id)
                if ioDev:
                    ioDev.poll()
            self.sleep(float(self.pluginPrefs['runLoopSleepTime']))

    @staticmethod
    def shutdown():
        L.threaddebug('shutdown called')

        # Log shutdown status of pigpio devices.

        if ioDevices:
            L.warning('%s pigpio devices still active at shutdown',
                      len(ioDevices))
        else:
            LI.startStop('All pigpio devices stopped')

        # Log shutdown status of pigpiod resources.

        if resources:
            L.warning('%s pigpiod resources still assigned/open at shutdown',
                      len(resources))
        else:
            LI.startStop('All pigpiod resources stopped/closed')

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
        L.threaddebug('validatePrefsConfigUi called')
        errors = indigo.Dict()

        # Set logging level.

        loggingLevel = valuesDict['loggingLevel']
        L.setLevel('THREADDEBUG' if loggingLevel == 'THREAD' else loggingLevel)

        # Set the LOGGING_MESSAGE_TYPES list in the conditionalLogging module.

        lmt = [item for item in valuesDict['loggingMessageTypes']]
        conditionalLogging.LOGGING_MESSAGE_TYPES = lmt

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
        L.threaddebug('validateDeviceConfigUi called "%s"; configured = %s',
                      dev.name, dev.configured)
        errors = indigo.Dict()

        ioDevType = valuesDict['ioDevType']
        interface = IODEV_DATA[ioDevType][1]

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

        if interface is SPI:
            try:  # Check bitRate.
                bitRate = float(valuesDict['bitRate'])
            except ValueError:
                errors['bitRate'] = 'Bit Rate must be a number.'
            else:
                if not 100 <= bitRate <= 10000:
                    errors['bitRate'] = 'Bit Rate must be in range.'

        # Validation of properties for specific typeIds:

        if typeId in ('analogInput', 'analogOutput'):

            try:  # Check scaling factor.
                float(valuesDict['scalingFactor'])
            except ValueError:
                errors['scalingFactor'] = 'Scaling factor must be a number.'

            textField = valuesDict['changeThreshold']  # Check changeThreshold.
            if textField != 'None':
                try:
                    changeThreshold = float(textField)
                except ValueError:
                    error = 'Change Threshold must be a number or None.'
                    errors['changeThreshold'] = error
                else:
                    if changeThreshold < 0.0:
                        error = 'Change Threshold must be non-negative.'
                        errors['changeThreshold'] = error

            textField = valuesDict['onThreshold']  # Check onThreshold.
            if textField != 'None':
                try:
                    float(textField)
                except ValueError:
                    errors['onThreshold'] = ('On threshold must be a number '
                                             'or None.')

            lowLimit = highLimit = None
            textField = valuesDict['lowLimit']  # Check lowLimit.
            if textField != 'None':
                try:
                    lowLimit = float(textField)
                except ValueError:
                    errors['lowLimit'] = 'Low Limit must be a number or None.'

            textField = valuesDict['highLimit']  # Check highLimit.
            if textField != 'None':
                try:  # Check highLimit.
                    highLimit = float(textField)
                except ValueError:
                    errors['highLimit'] = ('High Limit must be a number or '
                                           'None.')

            if lowLimit and highLimit and lowLimit > highLimit:
                error = 'Low limit must be less than high limit.'
                errors['lowLimit'] = error
                errors['highLimit'] = error

        elif typeId == 'analogOutput':

            textField = valuesDict['turnOnValue']  # Check turnOnValue.
            if textField != 'None':
                try:
                    float(textField)
                except ValueError:
                    errors['turnOnValue'] = ('Turn on value must be a number '
                                             'or None.')

            textField = valuesDict['turnOffValue']  # Check turnOffValue.
            if textField != 'None':
                try:
                    float(textField)
                except ValueError:
                    errors['turnOffValue'] = ('Turn off value must be a '
                                              'number or None.')

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

            # Compute the host id if one is not entered.

            hostId = valuesDict['hostId']
            if not hostId:
                split1 = hostAddress.split('.', 1)
                split2 = split1[0].split('-')
                if len(split2) > 1:
                    hostId = split2[-1]
                else:
                    hostId = 'pi'
                valuesDict['hostId'] = hostId

            # Incrementally build the device address string.

            address = hostId
            if ioDevType == 'pigpio':  # gpio device.
                address += '.g' + valuesDict['gpioNumber']
            else:
                if interface is I2C:  # i2c device.
                    i2cAddress = valuesDict['i2cAddress8']
                    if ioDevType == 'dkrPiRly':
                        i2cAddress = valuesDict['i2cAddress4']
                    valuesDict['i2cAddress'] = i2cAddress
                    address += '.i' + i2cAddress[2:]

                elif interface is SPI:  # spi device.
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
                L.debug(valuesDict)
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
    # def turnOn(pluginAction)                                                #
    # def turnOff(pluginAction)                                               #
    # def toggle(self, pluginAction)                                          #
    # def write(pluginAction)                                                 #
    # def actionControlDevice(self, action, dev)                              #
    # def actionControlUniversal(self, action, dev)                           #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def read(pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('read called "%s"', dev.name)
        ioDev = ioDevices.get(dev.id)
        if ioDev:
            ioDev.read()

    @staticmethod
    def turnOn(pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('turnOn called "%s"', dev.name)

        if dev.deviceTypeId == 'analogOutput':
            turnOnValue = dev.pluginProps['turnOnValue']
            if turnOnValue == 'None':
                L.warning('"%s" turn on sensor value not specified; '
                          'turnOn action ignored.', dev.name)
                return
        elif dev.deviceTypeId == 'digitalOutput':
            turnOnValue = ON
        else:
            L.warning('"%s" attempt to write to an input device; action '
                      'ignored', dev.name)
            return

        ioDev = ioDevices.get(dev.id)
        if ioDev:
            ioDev.write(turnOnValue)

    @staticmethod
    def turnOff(pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('turnOff called "%s"', dev.name)

        if dev.deviceTypeId == 'analogOutput':
            turnOffValue = dev.pluginProps['turnOffValue']
            if turnOffValue == 'None':
                L.warning('"%s" turn off sensor value not specified; '
                          'turnOff action ignored.', dev.name)
                return
            turnOffValue = float(turnOffValue)
        elif dev.deviceTypeId == 'digitalOutput':
            turnOffValue = OFF
        else:
            L.warning('"%s" attempt to write to an input device; action '
                      'ignored', dev.name)
            return

        ioDev = ioDevices.get(dev.id)
        if ioDev:
            ioDev.write(turnOffValue)

    def toggle(self, pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('toggle called "%s"', dev.name)
        (self.turnOff(pluginAction) if dev.states['onOffState']
         else self.turnOn(pluginAction))

    @staticmethod
    def write(pluginAction):
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('write called "%s"', dev.name)

        if dev.deviceTypeId in ('analogOutput', 'digitalOutput'):
            value = pluginAction.props['value']

            ioDev = ioDevices.get(dev.id)
            if ioDev:
                ioDev.write(value)
        else:
            L.warning('"%s" attempt to write to an input device; action '
                      'ignored', dev.name)

    def actionControlDevice(self, action, dev):
        L.threaddebug('actionControlDevice called "%s"', dev.name)

        class pluginAction:
            deviceId = dev.id

        if action.deviceAction == indigo.kDeviceAction.TurnOn:
            self.turnOn(pluginAction)
        elif action.deviceAction == indigo.kDeviceAction.TurnOff:
            self.turnOff(pluginAction)
        elif action.deviceAction == indigo.kDeviceAction.Toggle:
            self.toggle(pluginAction)

    def actionControlUniversal(self, action, dev):
        L.threaddebug('actionControlUniversal called "%s"', dev.name)
        if action.deviceAction == indigo.kUniversalAction.RequestStatus:

            class pluginAction:
                deviceId = dev.id

            self.read(pluginAction)
