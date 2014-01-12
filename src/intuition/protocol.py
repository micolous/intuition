"""
intuition/protocol.py - Twisted protocol library for OWL Intuition's multicast UDP energy monitoring protocol.
Copyright 2013-2014 Michael Farrell <micolous+git@gmail.com>
Copyright 2013 Johan van den Dorpe <johan.vandendorpe@gmail.com>

This library is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this library.  If not, see <http://www.gnu.org/licenses/>.

"""

from warnings import warn
from twisted.internet.protocol import DatagramProtocol
from lxml import objectify
from decimal import Decimal

MCAST_ADDR = '224.192.32.19'
MCAST_PORT = 22600


class OwlBaseMessage(object):
	@property
	def mac(self):
		"""
		MAC Address of the Network Owl.  This information comes from the
		body of the multicast UDP traffic (not the ethernet headers), so may
		be spoofed.
		"""
		return self._mac

	@property
	def rssi(self):
		"""
		Recieve signal strength (dBm).
		"""
		return self._rssi

	@property
	def lqi(self):
		"""
		Link quality, with 0 being best.
		"""
		return self._lqi


class OwlChannel(object):
	# structure for storing data about electricity channels
	def __init__(self, channel_id, current_w, daily_wh):
		self._channel_id = channel_id
		self._current_w = Decimal(current_w)
		self._daily_wh = Decimal(daily_wh)
	
	@property
	def channel_id(self):
		return self._channel_id

	@property
	def current_w(self):
		return self._current_w

	@property
	def daily_wh(self):
		return self._daily_wh

	def __str__(self):
		return '<OwlChannel: id=%s, current=%s, today=%s>' % (
			self.channel_id,
			self.current_w,
			self.daily_wh
		)

class OwlTemperature(object):
	def __init__(self, zone, current_temp, required_temp):
		self._zone = zone
		self._current_temp = Decimal(current_temp)
		self._required_temp = Decimal(required_temp)

	@property
	def zone_id(self):
		"""
		Unique identifier for the zone.
		"""
		return self._zone

	@property
	def current_temp(self):
		"""
		The current temperature in the zone.  Units are undefined by the
		documentation, but appear to be degrees Celcius.
		"""
		return self._current_temp

	@property
	def required_temp(self):
		"""
		The desired temperature in the zone.  Units are undefined by the
		documentation, but appear to be degrees Celcius.
		"""
		return self._required_temp
	


class OwlHeating(OwlBaseMessage):
	def __init__(self, datagram):
		# TODO: support Network Owl 2.3
		assert (datagram.tag == 'heating'), ('OwlHeating XML must have `heating` root node (got %r).' % datagram.tag)
		
		self._mac = datagram.attrib['id']

		# read signal information for the sensor's 433MHz link
		self._rssi = Decimal(datagram.signal[0].attrib['rssi'])
		self._lqi = Decimal(datagram.signal[0].attrib['lqi'])

		# read battery information from the sensor.
		self._battery_mv = Decimal(datagram.battery[0].attrib['level'][:-2])
		
		self._zones = {}
		for temp in datagram.temperature:
			assert temp.attrib['zone'] not in self._zones
			self._zones[temp.attrib['zone']] = OwlTemperature(temp.attrib['zone'], temp.current[0].text, temp.required[0].text)


	@property
	def battery_mv(self):
		"""
		Voltage level of the battery in the sensor, in millivolts.
		"""
		return self._battery_mv
		
	@property
	def zones(self):
		"""
		Zones defined for managing heating.
		"""
		return self._zones


class OwlElectricity(OwlBaseMessage):
	def __init__(self, datagram):
		assert (datagram.tag == 'electricity'), ('OwlElectricity XML must have `electricity` root node (got %r).' % datagram.tag)
		
		self._mac = datagram.attrib['id']
		
		# read signal information for the sensor's 433MHz link
		self._rssi = Decimal(datagram.signal[0].attrib['rssi'])
		self._lqi = Decimal(datagram.signal[0].attrib['lqi'])
		
		# read battery information from the sensor.
		self._battery_pc = Decimal(datagram.battery[0].attrib['level'][:-1])
		
		# read sensors (channels)
		self._channels = {}
		for channel in datagram.chan:
			assert channel.attrib['id'] not in self._channels, 'Channel duplicate'
			
			assert channel.curr[0].attrib['units'] == 'w', 'Current units must be watts'
			assert channel.day[0].attrib['units'] == 'wh', 'Daily usage must be watthours'
			
			# we're good and done our tests, create a channel
			self._channels[channel.attrib['id']] = OwlChannel(channel.attrib['id'], channel.curr[0].text, channel.day[0].text)

	@property
	def battery_pc(self):
		"""
		Percentage of battery remaining.
		
		Only on OwlElectricity messages.
		"""
		return self._battery_pc
	
	@property
	def battery(self):
		"""
		Deprecated: use OwlElectricity.battery_pc instead.
		"""
		warn('Use OwlElectricity.battery_pc instead.', DeprecationWarning, stacklevel=2)
		return self.battery_pc

	@property
	def channels(self):
		return self._channels

	def __str__(self):
		return '<OwlElectricity: rssi=%s, lqi=%s, battery=%s%%, channels=%s>' % (
			self.rssi,
			self.lqi,
			self.battery,
			', '.join((str(x) for x in self.channels.itervalues()))
		)


def parse_datagram(datagram):
	"""
	Parses a Network Owl datagram.
	"""
	xml = objectify.fromstring(datagram)
	
	if xml.tag == 'electricity':
		msg = OwlElectricity(xml)
	elif xml.tag == 'heating':
		# note: requires network owl 2.2
		# TODO: implement network owl 2.3 support
		msg = OwlHeating(xml)
	else:
		raise NotImplementedError, 'Message type %r not implemented.' % msg.tag

	return msg


class OwlIntuitionProtocol(DatagramProtocol):
	def __init__(self, iface=''):
		"""
		Protocol for Owl Intution (Network Owl) multicast UDP.
		
		:param iface: Name of the interface to use to communicate with the Network Owl.  If not specified, uses the default network connection on the cost.
		:type iface: str
		"""
		self.iface = iface

	def startProtocol(self):
		self.transport.joinGroup(MCAST_ADDR, self.iface)

	def datagramReceived(self, datagram, address):
		msg = parse_datagram(datagram)
		self.owlReceived(address, msg)

	def owlReceived(self, address, msg):
		print '%s: %s' % (address, msg)


if __name__ == '__main__':
	# Simple test program!
	from twisted.internet import reactor
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument('-i', '--iface', dest='iface', default='', help='Network interface to use for getting data.')
	
	options = parser.parse_args()
	
	protocol = OwlIntuitionProtocol(iface=options.iface)
	reactor.listenMulticast(MCAST_PORT, protocol, listenMultiple=True)
	reactor.run()
