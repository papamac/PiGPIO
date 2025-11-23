# coding=utf-8
"""
###############################################################################
#                                                                             #
#                            Pi GPIO Indigo Plugin                            #
#                              MODULE plugin.py                               #
#                                                                             #
###############################################################################

  BUNDLE:  Raspberry Pi General Purpose Input/Output for Indigo
           (Pi GPIO.indigoPlugin)
  MODULE:  plugin.py
   TITLE:  Main Python module in the Pi GPIO.indigoPlugin bundle
FUNCTION:  plugin.py defines the Plugin class, with standard methods that
           interface to the Indigo server and manage Indigo device objects.
   USAGE:  plugin.py is included in the Pi GPIO.indigoPlugin bundle and its
           methods are called by the Indigo server.
  AUTHOR:  papamac
 VERSION:  0.10.3
    DATE:  February 19, 2025

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

For more information, please refer to <https://unlicense.org/>

Pi GPIO PLUGIN BUNDLE DESCRIPTION:

Raspberry Pi is a powerful credit card sized computer with extensive General
Purpose Input/Output (GPIO) capabilities.  The Pi GPIO plugin allows Indigo to
access these capabilities using standard Indigo devices.  Physical analog and
digital input/output devices, hosted on the Pi, are linked to Indigo device
objects, giving Indigo the ability to sense the real world and manage it in
near real time.  One or more Pi's connect to the Indigo host via ethernet.
Each Pi runs a rgpio server daemon (written by joan2937) that manages the
interface between its GPIO hardware and the Pi GPIO plugin.

See the README.md file in the top level PiGPIO folder for more functional
details and operating instructions.  For details on the Raspberry Pi, its GPIO
system, and joan2937's amazing lg library, please refer to:

RPi computers:      <https://www.raspberrypi.com/products/
RPi OS:             <https://www.raspberrypi.com/software/>
RPi official doc's: <https://www.raspberrypi.com/documentation/computers/>
RPi GPIO system :   <https://www.raspberrypi.com/documentation/computers
                     /os.html#gpio-and-the-40-pin-header>
lg archive (rgpio): <https://abyz.me.uk/lg/index.html>
rgpio code:         <https://github.com/joan2937/lg>

The Pi GPIO plugin bundle has two primary Python modules: plugin.py
encapsulates the plugin device behavior in the Plugin class, and this module,
ioDevices.py, encapsulates detailed io device behavior in the IoDevice
class and its six subclasses.  An IoDevice subclass instance is created for
each plugin device started by plugin.py.  The plugin bundle contains two
supporting Python modules: rgpio.pi with classes/methods to access the rgpio
daemon and conditionalLogging.py to provide flexible Indigo logging by message
type and logging level.  It also includes several xml files that define plugin
devices, actions, and events.

MODULE plugin.py DESCRIPTION:

The plugin.py module defines the Plugin class whose methods provide entry
points into the plugin from the Indigo Plugin Host.  These methods, with access
to the Indigo server's object database, manage the definition, validation,
instantiation, and concurrent execution of Pi GPIO device objects.  Plugin
methods instantiate an IoDevice subclass object for each plugin device and
invoke IoDevice subclass methods to perform detailed device functions.

DEPENDENCIES/LIMITATIONS:

The classes and methods in the pigpioDevices module depend on the pigpio Python
library and the corresponding Raspberry Pi pigpio daemon server software.  Both
of these were written by joan2937, et al. and are available on
gitHub.com/joan2937/pigpio.  The current version is v79 released on March 2,
2021.  The pigpio Python library is included in the plugin bundle as the module
pygpio.py.  The pigpio daemon is included in current Raspberry Pi OS
distributions.  There has been no recent change activity in this software, and
it generally works well with the plugin.

CHANGE LOG:

Major changes to the Pi GPIO plugin are described in the CHANGES.md file in the
top level PiGPIO folder.  Changes of lesser importance may be described in
individual module docstrings if appropriate.

Note 2/25/2024: Some of the following descriptions may seem confusing because
the original module used joan2937's pigpio.py library and the pigpio daemon.
These were not upgraded to support the Raspberry Pi 5 and were replaced by
papamac in v0.10.0 with their lg archive equivalents, rgpio.py and the rgpio
daemon.  The historical record both here and in CHANGES.md retain references to
the original pigpio software.

v0.5.0  11/28/2021  Fully functional beta version with minimal documentation.
v0.5.1  11/29/2021  Force device stop/restart on a name change.
v0.5.2   1/19/2022  Use common IODEV_DATA dictionary to unambiguously identify
                    a device's interface type (I2C, SPI, or None)
v0.5.3   3/28/2022  Improve validation for low and high analog limits.
v0.5.7   7/20/2022  Update for Python 3.
v0.5.8   9/11/2022  Add support for Docker Pi Relay devices and 8/10-bit dacs.
v0.5.9  10/12/2022  Add glitch filter option for built-in GPIO inputs.
v0.6.0  11/20/2022  Use properties in pluginProps and pluginPrefs directly
                    without duplicating them in ioDev instance objects.
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
v0.8.1   5/13/2023  (1) Update validation of spi bitRate for MCP320X devices.
                    (2) In the startup method, remove the code that deletes
                    interruptDevices lists from the pluginProps of all plugin
                    devices.
                    (3) Fix a bug in validateDeviceConfigUi in setting the
                    hostId.
                    (4) Add a deviceDeleted method to signal a corresponding
                    method in the PiGPIODevice class to remove interrupt
                    devices that were deleted.
                    (5) Change spi bitRate units from kb/s to Mb/s.
0.9.1    6/23/2023  (1) Refactor pigpioDevices.py and plugin.py to reduce the
                    numbers of global variables shared across modules.  Create
                    new module-level methods in pigpioDevices to log startup
                    and shutdown device status summaries.
                    (2) Move statusInterval validation from
                    validatePrefsConfigUi to validateDeviceConfigUi.
0.9.2    9/10/2023  (1) Remove the deviceDeleted method (not needed).
                    (2) Update the hardware interrupt ConfigUi validation.
                    (3) Move startup functions to __init__.  Simplify
                    conditional logging initialization.
                    (4) Add method docstrings for most methods.
                    (5) Update module docstring in preparation for initial
                    release.
v0.9.3   12/7/2023  Fix pluginPrefs key error when starting the plugin for the
                    first time.
v0.10.0  2/25/2024  (1) Replace pigpio.py with rgpio.py to accommodate changes
                    in Raspberry Pi 5.
                    (2) Update files and wiki.
v0.10.1  3/25/2024  Refactor a key filename to be consistent with the change
                    from pigpio to rgpio: pigpioDevices.py becomes
                    ioDevices.py.
v0.10.3  2/19/2025  Remove bounceFilter and bounceTime checks from method
                    validateDeviceConfigUi.  The bounce filter was replaced by
                    the glitchFilter in v0.5.9.
"""
###############################################################################
#                                                                             #
#                       DUNDERS, IMPORTS, and GLOBALS                         #
#                                                                             #
###############################################################################

__author__ = 'papamac'
__version__ = '0.10.3'
__date__ = '2/19/2025'

import indigo

from logging import NOTSET, getLogger

from conditionalLogging import LD, LI
import rgpio
from ioDevices import getIoDev, getRpiModel, GPIO_CHIP
from ioDevices import logStartupSummary, logShutdownSummary

L = getLogger('Plugin')  # Standard Plugin logger.
ON, OFF = (1, 0)         # on/off states.


###############################################################################
#                                                                             #
#                               CLASS Plugin                                  #
#                                                                             #
###############################################################################

class Plugin(indigo.PluginBase):
    """
    The Plugin class is a collection of standard Indigo plugin methods that are
    needed to manage and run multiple Pi GPIO devices.  It is segmented into
    four parts for readability:

    I   INITIALIZATION, DEVICE START/STOP, AND RUN/SHUTDOWN METHODS,
    II  CONFIG UI VALIDATION METHODS,
    III CONFIG UI CALLBACK METHODS, and
    IV  ACTION CALLBACK METHODS
    """

    ###########################################################################
    #                                                                         #
    #                              CLASS Plugin                               #
    #                                   PART                                  #
    #                                                                         #
    #                                   III                                   #
    #                                    I                                    #
    #                                    I                                    #
    #                                    I                                    #
    #                                    I                                    #
    #                                   III                                   #
    #                                                                         #
    #      INITIALIZATION, DEVICE START/STOP, AND RUN/SHUTDOWN METHODS        #
    #                                                                         #
    # def __init__(self, pluginId, pluginDisplayName, pluginVersion,          #
    #              pluginPrefs):                                              #
    # def didDeviceCommPropertyChange(oldDev, newDev)                         #
    # def deviceStartComm(dev)                                                #
    # def deviceStopComm(dev)                                                 #
    # def runConcurrentThread(self)                                           #
    # def shutdown(self)                                                      #
    #                                                                         #
    ###########################################################################

    def __init__(self, pluginId, pluginDisplayName,
                 pluginVersion, pluginPrefs):
        """
        Call superclass __init__.  Set logging level from pluginPrefs.
        Initialize conditional logging to enable access to pluginPrefs.
        """
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName,
                                   pluginVersion, pluginPrefs)
        self.indigo_log_handler.setLevel(NOTSET)  # Eliminate handler level.
        level = pluginPrefs.get('loggingLevel', 'INFO')
        L.setLevel('THREADDEBUG' if level == 'THREAD' else level)
        L.threaddebug('__init__ called')
        LD.init(self)
        LI.init(self)

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

    @staticmethod
    def deviceStartComm(dev):
        """
        Get the io device object for the current Indigo device.  Create a new
        IO device instance if none exists.  If successful read the io device to
        set its initial states.
        """
        L.threaddebug('deviceStartComm called "%s"', dev.name)
        ioDev = getIoDev(dev, new=True)
        if ioDev:
            ioDev.read(logAll=None)

    @staticmethod
    def deviceStopComm(dev):
        """
        Get the io device object for the current Indigo device.  If successful,
        invoke the io device's stop method.
        """
        L.threaddebug('deviceStopComm called "%s"', dev.name)
        ioDev = getIoDev(dev)
        if ioDev:
            ioDev.stop()

    def runConcurrentThread(self):
        """
        Call pigpioDevices logStartupSummary on entry to provide io device
        startup status.  Then enter a continuous run loop that is repeated
        every runLoopSleepTime seconds.  On each pass through the loop, search
        the Indigo device database for Pi GPIO plugin devices with valid io
        device objects.  Call the poll method for each valid io device.
        """
        L.threaddebug('runConcurrentThread called')
        logStartupSummary()
        while True:
            for dev in indigo.devices.iter('self'):
                if dev.configured and dev.enabled:
                    ioDev = getIoDev(dev)
                    if ioDev:
                        ioDev.poll()
            self.sleep(float(self.pluginPrefs['runLoopSleepTime']))

    @staticmethod
    def shutdown():
        """
        Call pigpioDevices logShutdownSummary to provide io device status at
        shutdown.
        """
        L.threaddebug('shutdown called')
        logShutdownSummary()

    ###########################################################################
    #                                                                         #
    #                              CLASS Plugin                               #
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
        """
        Validate the ConfigUi settings for the Pi GPIO plugin preferences.
        """
        L.threaddebug('validatePrefsConfigUi called')
        errors = indigo.Dict()

        # Set logging level.

        loggingLevel = valuesDict['loggingLevel']
        L.setLevel('THREADDEBUG' if loggingLevel == 'THREAD' else loggingLevel)

        # Validate the run loop sleep time.

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
        """
        Validate the ConfigUi settings for Pi GPIO devices.  Derive new values
        dictionary entries for the device id (devId) and device address
        (address).
        """
        dev = indigo.devices[devId]
        L.threaddebug('validateDeviceConfigUi called "%s"; configured = %s',
                      dev.name, dev.configured)
        errors = indigo.Dict()

        # Determine the interface type.

        ioDevType = valuesDict['ioDevType']
        if ioDevType == 'pigpio':
            interface = 'gpio'
        elif 'S' in ioDevType or ioDevType[:5] in ('MCP32', 'MCP48'):
            interface = 'spi'
        else:
            interface = 'i2c'

        # Validation of common properties for all device types:

        hostAddress = valuesDict['hostAddress']
        try:  # Check portNumber.
            portNumber = int(valuesDict['portNumber'])
        except ValueError:
            errors['portNumber'] = 'Port number must be an integer.'
        else:
            if not 1024 <= portNumber <= 65535:
                errors['portNumber'] = 'Port number must be in range.'
            else:  # Good port number; check connection.
                connection = rgpio.sbc(hostAddress, portNumber)
                if not connection.connected:
                    error = 'Connection failed.'
                    errors['hostAddress'] = errors['portNumber'] = error
                    connection.stop()
                else:  # Good connection; check rpi model.
                    model = getRpiModel(connection)
                    if not model:
                        error = 'rpi model info not found.'
                        errors['hostAddress'] = errors['portNumber'] = error
                        connection.stop()
                    else:  # Good model; look up the gpio chip number.
                        gpioChip = GPIO_CHIP.get(model)
                        if gpioChip is None:
                            error = 'gpio chip number not found.'
                            errors['hostAddress'] = error
                            errors['portNumber'] = error
                            connection.stop()

        try:  # Check pollingInterval.
            pollingInterval = float(valuesDict['pollingInterval'])
        except ValueError:
            error = 'Polling/logging interval must be a number.'
            errors['pollingInterval'] = error
        else:
            if pollingInterval < 0.0:
                error = 'Polling interval must be non-negative.'
                errors['pollingInterval'] = error

        try:  # Check statusInterval.
            statusInterval = float(valuesDict['statusInterval'])
        except ValueError:
            errors['statusInterval'] = 'Status interval must be a number.'
        else:
            if statusInterval < 0.0:
                error = 'Status interval must be non-negative.'
                errors['statusInterval'] = error

        # Validation of properties for SPI devices:

        if interface == 'spi':
            try:  # Check bitRate.
                bitRate = float(valuesDict['bitRate'])
            except ValueError:
                errors['bitRate'] = 'Bit Rate must be a number.'
            else:
                if 0.1 <= bitRate <= 10.0:
                    if ioDevType.startswith('MCP320'):
                        maximumBitRate = 1.8 if ioDevType[-1] == '2' else 2.0
                        if bitRate > maximumBitRate:
                            errors['bitRate'] = ('Maximum SPI Bit Rate is %s '
                                                 'Mb/s.' % maximumBitRate)
                else:
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
                error = 'Low limit must be <= high limit.'
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

        #  Check and set properties for potential hardware interrupt devices.

        if 'hardwareInterrupt' in valuesDict:  # Potential hw interrupt device.
            if valuesDict['hardwareInterrupt']:  # Hardware interrupt.
                if not valuesDict['interruptRelayGPIO']:  # Check for error.
                    error = 'Must select an Interrupt Relay GPIO.'
                    errors['interruptRelayGPIO'] = error
            else:  # No hardware interrupt; reset interruptRelayGPIO.
                valuesDict['interruptRelayGPIO'] = ''

            # Add a priorInterruptRelayGPIO property to valuesDict from the
            # current pluginProps['interruptRelayGPIO'].

            priorInterruptRelayGPIO = dev.pluginProps.get(
                'interruptRelayGPIO', '')
            valuesDict['priorInterruptRelayGPIO'] = priorInterruptRelayGPIO

        # Primary validations complete.  Return if there are errors to be
        # corrected.  If there are no errors, continue with post-validation
        # processing.

        if errors:
            return False, valuesDict, errors
        else:

            # Compute the host id if one is not entered.

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
            if interface == 'gpio':  # gpio device.
                address += '.g' + valuesDict['gpioNumber']
            else:
                if interface == 'i2c':  # i2c device.
                    i2cAddress = valuesDict['i2cAddress8']
                    if ioDevType == 'dkrPiRly':
                        i2cAddress = valuesDict['i2cAddress4']
                    valuesDict['i2cAddress'] = i2cAddress
                    address += '.i' + i2cAddress[2:]

                elif interface == 'spi':  # spi device.
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

            # Validation is complete: all tests passed and the address is
            # unique.  Add the hostId and address properties to the values
            # dictionary before returning.

            valuesDict['hostId'] = hostId
            valuesDict['address'] = address
            L.debug(valuesDict)
            return True, valuesDict

    ###########################################################################
    #                                                                         #
    #                              CLASS Plugin                               #
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
        """
        Select candidate built-in Raspberry Pi gpio devices for the "Interrupt
        Relay GPIO" menu list.
        """
        devices = []
        for dev in indigo.devices.iter('self'):
            if dev.deviceTypeId == 'digitalInput':
                if (dev.pluginProps['ioDevType'] == 'pigpio'
                        and dev.pluginProps['relayInterrupts']):
                    devices.append(dev.name)
        return sorted(devices)

    ###########################################################################
    #                                                                         #
    #                              CLASS Plugin                               #
    #                                   PART                                  #
    #                                                                         #
    #                             III   III     III                           #
    #                              I     I       I                            #
    #                              I      I     I                             #
    #                              I       I   I                              #
    #                              I        I I                               #
    #                             III       III                               #
    #                                                                         #
    #                         ACTION CALLBACK METHODS                         #
    #                                                                         #
    # Internal support methods (functions of an Indigo device object):        #
    #                                                                         #
    # def _read(dev)                                                          #
    # def _write(dev, value)                                                  #
    # def _turnOn(dev)                                                        #
    # def _turnOff(dev)                                                       #
    # def _toggle(dev)                                                        #
    #                                                                         #
    # Plugin action callback methods (functions of a pluginAction object)     #
    #                                                                         #
    # def read(pluginAction)                                                  #
    # def write(pluginAction)                                                 #
    # def turnOn(pluginAction)                                                #
    # def turnOff(pluginAction)                                               #
    # def toggle(self, pluginAction)                                          #
    #                                                                         #
    # Built-in action callback methods (functions of an action enumeration    #
    #                                   object and the device object)         #
    #                                                                         #
    # def actionControlDevice(self, action, dev)                              #
    # def actionControlUniversal(self, action, dev)                           #
    #                                                                         #
    ###########################################################################

    @staticmethod
    def _read(dev):
        """ Lookup the io device and read it if available. """
        ioDev = getIoDev(dev)
        if ioDev:
            ioDev.read()
        else:
            L.warning('"%s" io device not available; read action ignored',
                      dev.name)

    @staticmethod
    def _write(dev, value):
        """ Lookup the io device and write to it if available. """
        ioDev = getIoDev(dev)
        if ioDev:
            ioDev.write(value)
        else:
            L.warning('"%s" io device not available; write action ignored',
                      dev.name)

    def _turnOn(self, dev):
        """
        Get the turn on value for analog output or digital output devices.
        Write the value to the device.
        """
        if dev.deviceTypeId == 'analogOutput':
            turnOnValue = dev.pluginProps['turnOnValue']
            if turnOnValue == 'None':
                L.warning('"%s" turn on sensor value not specified; '
                          'turnOn action ignored.', dev.name)
                return
        elif dev.deviceTypeId == 'digitalOutput':
            turnOnValue = ON
        else:
            L.warning('"%s" attempt to write to an input device; turnOn '
                      'action ignored', dev.name)
            return
        self._write(dev, turnOnValue)

    def _turnOff(self, dev):
        """
        Get the turn off value for analog output or digital output devices.
        Write the value to the device.
        """
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
            L.warning('"%s" attempt to write to an input device; turnOff '
                      'action ignored', dev.name)
            return
        self._write(dev, turnOffValue)

    def _toggle(self, dev):
        """ Turn on or turn off the device depending on the current state. """
        self._turnOff(dev) if dev.states['onOffState'] else self._turnOn(dev)

    def read(self, pluginAction):
        """ Read the device as a result of a Pi GPIO read action request. """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('read called "%s"', dev.name)
        self._read(dev)

    def write(self, pluginAction):
        """
        Write to the device as a result of a Pi GPIO write action request.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('write called "%s"', dev.name)
        if dev.deviceTypeId in ('analogOutput', 'digitalOutput'):
            value = pluginAction.props['value']
            self._write(dev, value)
        else:
            L.warning('"%s" attempt to write to an input device; action '
                      'ignored', dev.name)

    def turnOn(self, pluginAction):
        """
        Turn on the device as a result of a Pi GPIO turnOn action request.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('turnOn called "%s"', dev.name)
        self._turnOn(dev)

    def turnOff(self, pluginAction):
        """
        Turn off the device as a result of a Pi GPIO turnOff action request.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('turnOff called "%s"', dev.name)
        self._turnOff(dev)

    def toggle(self, pluginAction):
        """
        Toggle the device as a result of a Pi GPIO toggle action request.
        """
        dev = indigo.devices[pluginAction.deviceId]
        L.threaddebug('toggle called "%s"', dev.name)
        self._turnOff(dev) if dev.states['onOffState'] else self.turnOn(dev)

    def actionControlDevice(self, action, dev):
        """
        Turn on, turn off, or toggle the device as a result of an Indigo Home
        window action request.
        """
        L.threaddebug('actionControlDevice called "%s"', dev.name)
        if action.deviceAction == indigo.kDeviceAction.TurnOn:
            self._turnOn(dev)
        elif action.deviceAction == indigo.kDeviceAction.TurnOff:
            self._turnOff(dev)
        elif action.deviceAction == indigo.kDeviceAction.Toggle:
            self._toggle(dev)

    def actionControlUniversal(self, action, dev):
        """
        Read the device as a result of an Indigo Home window status request.
        """
        L.threaddebug('actionControlUniversal called "%s"', dev.name)
        if action.deviceAction == indigo.kUniversalAction.RequestStatus:
            self._read(dev)
