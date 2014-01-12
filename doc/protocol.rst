Protocol notes for Owl Intuition (Network Owl)
==============================================

Events are broadcast on LAN via Multicast UDP address ``224.192.32.19:22600``.  Events are transmitted in XML.

These events are from the OWL Intuition-lc.  There may be some more events with the OWL Intuition-pv, however I don't know anything about it (as I do not own the unit nor have a PV generator).

Official protocol documentation:

* `Multicast UDP (PDF)`_
* `API Documentation`_

.. _Multicast UDP (PDF): https://theowl.zendesk.com/hc/en-gb/article_attachments/200344663/Network_OWL_Multicast.pdf
.. _API Documentation: https://theowl.zendesk.com/hc/en-gb/articles/201284603-Multicast-UDP-API-Information



.. highlight:: xml

electricity event
-----------------

These events are sent once every minute, and contain the live monitoring data from units connected to the Network Owl.

Example::

	<electricity id='443719123456'>
	  <signal rssi='-42' lqi='15'/>
	  <battery level='100%'/>
	  <chan id='0'>
	    <curr units='w'>257.00</curr>
	    <day units='wh'>17.13</day>
	  </chan>
	  <chan id='1'>
	    <curr units='w'>96.00</curr>
	    <day units='wh'>6.40</day>
	  </chan>
	  <chan id='2'>
	    <curr units='w'>32.00</curr>
	    <day units='wh'>2.13</day>
	  </chan>
	</electricity>

electricity.id
	MAC address of the device
	
electricity.signal
	Metadata about the link quality between the sensor and the network reciever device.

electricity.battery
	Battery level in the sensor.

electricity.chan
	Channel information for each channel attached to the sensor.
	
weather event
-------------

These show local weather information, not anything in the device.  It is retrieved from a web service that the Network Owl connects to.  There isn't any sensor in the Network Owl that gives this information.

As a result, this library ignores these messages.

Example::

	<weather id='443719123456' code='116'>
	  <temperature>11.00</temperature>
	  <text>Partly Cloudy</text>
	</weather>

weather.id
	MAC address of device

weather.temperature
	Temperature, in degrees Celcius.

weather.text
	Description of local weather conditions.
