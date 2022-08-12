Raspberry Pi is a powerful credit card sized computer with extensive General
Purpose Input/Output (GPIO) capabilities that make it an ideal addition to an
Indigo Home Automation System.  Physical analog and digital input/output
devices, hosted on the pi, are linked to Pi GPIO plugin devices. These give
Indigo the ability to sense the real world and manage it in near real time.

The Pi GPIO plugin can poll input devices at a user-specified rate, or it can
utilize interrupts/callbacks if available for that device. One or more pi's
connect to the Indigo host via wired or wireless ethernet. Each pi runs a
pigpio daemon that performs the physical I/O and manages the interface to the
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
devices, and Relay (RLY) devices.