![](https://raw.githubusercontent.com/papamac/PiGPIO/master/files/raspi4bp.png)

## Raspberry Pi General Purpose Input/Output for indigo ##

Raspberry Pi is a powerful credit card sized computer with extensive General
Purpose Input/Output (GPIO) capabilities that make it an ideal addition to an
Indigo Home Automation System.  Physical analog and digital input/output
devices, hosted on the Pi, are linked to Indigo device objects, giving Indigo
the ability to sense the real world and manage it in near real time.  One or
more Pi's connect to the Indigo host via wired or wireless ethernet.  Each Pi
runs a pigpio daemon that manages the interface between
the Pi GPIO's and this Pi GPIO plugin.

The plugin can monitor a wide variety of optional devices that are already
available in Indigo as supported devices or through existing 3rd party plugins.
These include both z-wave devices and custom/wired devices. Device types
include contact sensors, relays, tilt sensors, and multisensors. The garage
door tracking accuracy depends upon the selected devices and the door's
operational cycle.

| Requirement            |                     |
|------------------------|---------------------|
| Minimum Indigo Version | 2022.1              |
| Python Library (API)   | Official            |
| Requires Local Network | No                  |
| Requires Internet      | Yes                 |
| Hardware Interface     | None                |

Please see the
[full documentation](https://www.github.com/papamac/PiGPIO/wiki)
for details on the design, operation, and use of the plugin. Also, you can
download the latest version of the plugin at the 
[Indigo Plugin Store](http://www.indigodomo.com/pluginstore/).
