"""
intuition/protocol.py - Twisted protocol library for OWL Intuition's multicast UDP energy monitoring protocol.
Copyright 2013 Michael Farrell <micolous+git@gmail.com>

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

from twisted.internet.protocol import DatagramProtocol
from lxml import objectify
from decimal import Decimal

MCAST_ADDR = '224.192.32.19'
MCAST_PORT = 22600

class OwlChannel(object):
	# structure for storing data about channels
	def __init__(self, channel_id, current_w, daily_wh):
		self.channel_id = channel_id
		self.current_w = Decimal(current_w)
		self.daily_wh = Decimal(daily_wh)
	
	def __str__(self):
		return '<OwlChannel: id=%s, current=%s, today=%s>' % (
			self.channel_id,
			self.current_w,
			self.daily_wh
		)


class OwlMessage(object):
	def __init__(self, datagram):
		#print "datagram: %r" % (datagram,)
		self.root = objectify.fromstring(datagram)
		
		# there are also weather events -- we don't care about these
		assert (self.root.tag == 'electricity'), ('OwlMessage XML must have `electricity` root node (got %r).' % self.root.tag)
		
		# note that the MAC address is given by the message, not the packet.
		# this can be spoofed
		self.mac = self.root.attrib['id']
		
		# read signal information for the sensor's 433MHz link
		self.rssi = Decimal(self.root.signal[0].attrib['rssi'])
		self.lqi = Decimal(self.root.signal[0].attrib['lqi'])
		
		# read battery information from the sensor.
		self.battery = Decimal(self.root.battery[0].attrib['level'][:-1])
		
		# read sensors (channels)
		self.channels = {}
		for channel in self.root.chan:
			assert channel.attrib['id'] not in self.channels, 'Channel duplicate'
			
			assert channel.curr[0].attrib['units'] == 'w', 'Current units must be watts'
			assert channel.day[0].attrib['units'] == 'wh', 'Daily usage must be watthours'
			
			# we're good and done our tests, create a channel
			self.channels[channel.attrib['id']] = OwlChannel(channel.attrib['id'], channel.curr[0].text, channel.day[0].text)
	
	def __str__(self):
		return '<OwlMessage: rssi=%s, lqi=%s, battery=%s%%, channels=%s>' % (
			self.rssi,
			self.lqi,
			self.battery,
			', '.join((str(x) for x in self.channels.itervalues()))
		)


class OwlIntuitionProtocol(DatagramProtocol):
	def __init__(self, iface=''):
		"""
		Protocol for Owl Intution (Network Owl) multicast UDP.
		
		:param iface: Name of the interface to use to communicate with the Network Owl.  If not specified, uses the default network connection on the cost.
		:type iface: str
		"""
		self.iface = iface
		
		DatagramProtocol.__init__(self)

	def startProtocol(self):
		self.transport.joinGroup(MCAST_ADDR, self.iface)
	
	def datagramReceived(self, datagram, address):
		msg = OwlMessage(datagram)
		self.owlReceived(address, msg)
	
	def owlReceived(self, address, msg):
		print '%s: %s' % (address, msg)


if __name__ == '__main__':
	from twisted.internet import reactor
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument('-i', '--iface', dest='iface', default='', help='Network interface to use for getting data.')
	
	options = parser.parse_args()
	
	protocol = OwlIntuitionProtocol(iface=options.iface)
	reactor.listenMulticast(MCAST_PORT, protocol, listenMultiple=True)
	reactor.run()
