# intuition #

Python/Twisted library for receiving multicast UDP (local) messages from the Network Owl (OWL Intution) home energy monitor.

This library does not interface with the Owl Intuition website, and requires that it be run on the same LAN segment as the Network Owl.  It has been tested primarily with the OWL Intuition-lc.

Copyright 2013-2014 Michael Farrell.  Licensed under the GNU LGPL3+.  For more details see `COPYING` and `COPYING.LESSER`.

## requirements ##

- Python 2.7 (2.6 should also work)
- Twisted
- lxml

## protocol support ##

This only supports receiving information from a Network Owl over multicast UDP.

It supports the following packet types:

- Electricity usage monitoring (not solar)
- Heating (on v2.2 and older firmware)

Other packet types are unsupported and ignored, but patches to implement it are welcome.

## some batteries ##

You can use the `intuition.rrd` module to graph electricity usage information with `rrdtool`.
