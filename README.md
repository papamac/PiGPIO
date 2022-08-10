![](https://raw.githubusercontent.com/papamac/PiGPIO/master/files/raspi4b.png)

## Raspberry Pi General Purpose Input/Output for indigo ##

Raspberry Pi is a powerful credit card sized computer with extensive General
Purpose Input/Output (GPIO) capabilities that make it an ideal addition to an
Indigo Home Automation System.  Physical analog and digital input/output
devices, hosted on the Pi, are linked to Pi GPIO plugin devices. These give
Indigo the ability to sense the real world and manage it in near real time.

The Pi GPIO plugin can poll input devices at a user-specified rate, or it can
utilize interrupts/callbacks if available for that device. One or more Pi's
connect to the Indigo host via wired or wireless ethernet. Each Pi runs a
pigpio daemon that performs the physical I/O and manages the interface to the
plugin.

Each Raspberry Pi has 27 built-in GPIO pins which are available for digital I/O
or special functions including Inter-Integrated Circuit (I2C) and Serial
Peripheral Interface (SPI) buses. Excluding pins allocated to these special
functions, there are 17 pins that remain available for user digital inputs and
outputs. See [GPIO and the 40-pin Header](https://raspberrypi.com/documentation/computers/os.html#gpio-and-the-40-pin-header)
for more details.

In addition to the built-in Raspberry Pi GPIO pins, the Pi GPIO plugin supports
many chip-level devices and add-on boards (HATs). These are connected to the Pi
using an I2C or SPI bus. They include additional Digital I/O pins (DIO), Analog
to Digital Converters (ADC), Digital to Analog Converters (DAC), and Relays
(RLY).

The following table lists currently supported devices and boards. Live links
take you to web pages providing additional details.

 | Mfgr                 | Functions                                                | Bus                         | Devices                                       | Description                                                                                                                                                             |
 |----------------------------------------------------------|-----------------------------|-----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
 | Microchip Technology | 8-Bit DIO                                                | I2C<br/>SPI                 | MCP23008<br/>MCP23S08                         | [8-Bit IO Expander with Serial Interface](https://ww1.microchip.com/downloads/en/DeviceDoc/21919e.pdf)                                                                  |
 | Microchip Technology | 16-Bit DIO                                               | I2C<br/>SPI                 | MCP23017<br/>MCP23S17                         | [16-Bit IO Expander with Serial Interface](https://ww1.microchip.com/downloads/en/devicedoc/20001952c.pdf)                                                              |
 | Microchip Technology | 12-Bit ADC                                               | SPI                         | MCP3202                                       | [2.7V Dual Channel 12-Bit A/D Converter with SPI Serial Interface](https://ww1.microchip.com/downloads/en/DeviceDoc/21034F.pdf)                                         |
 | Microchip Technology | 12-Bit ADC                                               | SPI                         | MCP3204/8                                     | [2.7V 4/8-Channel 12-Bit A/D Converters with SPI Serial Interface](http://ww1.microchip.com/downloads/en/devicedoc/21298e.pdf)                                          |
 | Microchip Technology | 18-Bit ADC                                               | I2C                         | MCP3422<br/>MCP3423<br/>MCO3424               | [18-Bit, Multi-Channel ΔΣ Analog-to-Digital Converter with I2C Interface and On-Board Reference](http://ww1.microchip.com/downloads/en/devicedoc/22088c.pdf)            |
 | Microchip Technology | 8-Bit DAC<br/>10-Bit DAC<br/>12-Bit DAC                  | SPI                         | MCP4801/2<br/>MCP4811/2<br/>MCP4821/2         | [8/10/12-Bit, 1/2 Channel Voltage Output Digital-to-Analog Converter with Internal VREF and SPI Interface](https://ww1.microchip.com/downloads/en/DeviceDoc/22244B.pdf) |
 | AB Electronics       | 16-Bit DIO<br/>12-Bit ADC / 8<br/>12-Bit DAC / 2<br/>RTC | I2C<br/>SPI<br/>SPI<br/>I2C | MCP23017<br/>MCP3208<br/> MCP4822<br/> DS1307 | [Expander Pi HAT](https://abelectronics.co.uk/p/50/expander-pi)<br/>(RTC not supported)                                                                                 |
 | AB Electronics       | 32-Bit DIO                                               | I2C                         | 2 X MCP23017                                  | [IO Pi Plus HAT](https://abelectronics.co.uk/p/50/expander-pi)                                                                                                          |
 | AB Electronics       | 17-Bit ADC / 8 Single Ended                              | I2C                         | 2 X MCP3424                                   | [ADC Pi HAT](https://abelectronics.co.uk/p/69/adc-pi-raspberry-pi-analogue-to-digital-converter)                                                                        |
 | AB Electronics       | 18-Bit ADC / 8 Differential                              | I2C                         | 2 X MCP3424                                   | [ADC Differential Pi HAT](https://abelectronics.co.uk/p/65/adc-differential-pi-raspberry-pi-analogue-to-digital-converter)                                              |
 | AB Electronics       | 12-Bit ADC / 2<br/>12-Bit DAC / 2                        | SPI                         | MCP3202<br/>MCP4822                           | [ADC-DAC Pi Zero HAT](https://abelectronics.co.uk/p/74/adc-dac-pi-zero-raspberry-pi-adc-and-dac-expansion-board)                                                        |
 | 52Pi                 | RLY / 4                                                  | I2C                         |                                               | [DockerPi 4 Channel Relay HAT](https://wiki.52pi.com/index.php?title=EP-0099)                                                                                           |

The following table lists the top level requirements for the Pi GPIO plugin:

| Requirement                                 | Description                                                                                                                                 |
|---------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| Indigo                                      | Version 2022.1 or later                                                                                                                     |
| Python Library (API)                        | Official (3.X)                                                                                                                              |
| Macintosh computer<br/>for pi configuration | Large display preferred<br/>SD card reader                                                                                                  |
 | Raspberry Pi                                | Model 4b (3b+ will work, but display config must be changed)<br/>1 GB RAM or more<br/>Premium microSD card (16 GB or more, U3 and A2 rated) |
| Local Network                               | Reliable connection between the Mac and the pi<br/>Wired network preferred (1000 Mb/sec)<br/>Wireless OK if faster than 50 Mb/sec           |
| Internet                                    | At least 25 Mb/sec for software downloads                                                                                                   |
| Hardware Interface                          | Raspberry Pi GPIO pins<br/>Pi I/O devices and HATs from above table                                                                         |

Please see the
[Pi GPIO Wiki](https://github.com/papamac/VirtualGarageDoor/wiki)
for details on the design, operation, and use of the plugin.

You can download the latest version of the plugin at the 
[Indigo Plugin Store](https://indigodomo.com/pluginstore).
Your bug reports, comments and suggestions will be greatly appreciated.  Please
post them on papamac's
[Pi GPIO User Forum](https://forums.indigodomo.com/viewforum.php?f=375).