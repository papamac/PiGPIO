![](https://raw.githubusercontent.com/papamac/PiGPIO/master/files/raspi4b.png)

# Raspberry Pi General Purpose Input/Output for indigo

Raspberry Pi is a powerful credit card sized computer with extensive General
Purpose Input/Output (GPIO) capabilities that make it an ideal addition to an
Indigo Home Automation System.  Physical analog and digital input/output
devices, hosted on the pi, are linked to Pi GPIO plugin devices. These give
Indigo the ability to sense the real world and manage it in near real time.

The Pi GPIO plugin can poll input devices at a user-specified rate, or it can
utilize interrupts/callbacks if available for that device. One or more pi's
connect to the Indigo host via wired or wireless ethernet. Each pi runs a
**_pigpio_** daemon that performs the physical I/O and manages the interface to the
plugin.

Each Raspberry Pi has 27 built-in GPIO pins that are available for digital I/O
or special functions including Inter-Integrated Circuit (I2C) and Serial
Peripheral Interface (SPI) buses. Excluding pins allocated to these special
functions, there are 17 pins that remain available for user digital inputs and
outputs. See
[GPIO and the 40-pin Header](https://raspberrypi.com/documentation/computers/os.html#gpio-and-the-40-pin-header)
for more details.

In addition to the built-in Raspberry Pi GPIO pins, the Pi GPIO plugin supports
many chip-level devices and add-on boards (HATs). These are connected to the pi
using I2C and SPI busses. They include additional Digital I/O (DIO) pins,
Analog to Digital Converter (ADC) devices, Digital to Analog Converter (DAC)
devices, and Relay (RLY) devices. Please see the latest list of
[supported devices](https://github.com/papamac/PiGPIO/wiki/Supported-Devices)
in the Pi GPIO wiki.

The following table lists the top level requirements for the Pi GPIO plugin:

| Requirement                                 | Description                                                                                                                                     |
|---------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| Indigo                                      | Version 2022.1 or later                                                                                                                         |
| Python Library (API)                        | Official (3.X)                                                                                                                                  |
| Macintosh computer<br/>for pi configuration | Large display preferred<br/>SD card reader                                                                                                      |
| Raspberry Pi                                | 4 model b with 1 GB RAM or more<br/>microSD card with 16 GB or more, U3 / A2 rated<br/>5V / 3A USB-C power adapter                              |
| Local Network                               | Wired network preferred (1000 Mb/sec)<br/>Wireless OK if faster than 50 Mb/sec                                                                  |
| Internet                                    | At least 25 Mb/sec for software downloads                                                                                                       |
| Hardware Interfaces                         | Raspberry Pi GPIO pins<br/>Pi I/O devices and HATs from the [supported devices](https://github.com/papamac/PiGPIO/wiki/Supported-Devices) table |

Please see the [Pi GPIO wiki](https://github.com/papamac/PiGPIO/wiki/Overview)
for details on the design, configuration and use of the plugin and its
Raspberry Pi host.


You can download the latest version of the plugin at the 
[Indigo Plugin Store](https://indigodomo.com/pluginstore).
Your bug reports, comments and suggestions will be greatly appreciated.  Please
post them on papamac's [Pi GPIO user forum](https://forums.indigodomo.com/viewforum.php?f=375).