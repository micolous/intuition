Protocol notes for Owl Intuition (Network Owl)
==============================================

Events are broadcast on LAN via Multicast UDP address ``224.192.32.19:22600``.

Events are transmitted in XML.

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
