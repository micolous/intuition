"""
intuition/rrd.py - rrdtool integration support for OWL Intuition.
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

from __future__ import absolute_import
from .protocol import OwlIntuitionProtocol, MCAST_PORT, OwlElectricity
from twisted.internet import reactor
from argparse import ArgumentParser
import rrdtool


class RrdOwlProtocol(OwlIntuitionProtocol):
	def __init__(self, src, rrd, *args, **kwargs):
		self.src = src
		self.rrd = rrd
		OwlIntuitionProtocol.__init__(self, *args, **kwargs)

	def owlReceived(self, address, msg):
		ip, port = address
		
		if ip != self.src:
			# drop out, bad source
			raise ValueError, 'Source address does not match for packet'
		
		assert isinstance(msg, OwlElectricity), 'This only supports electricity messages.'

		# we are good.
		print msg
		
		# iterate channels sorted by channel name, and get their data
		chan_names = msg.channels.keys()
		chan_names.sort()
		
		o = ['N']
		for channel in chan_names:
			o.append(str(msg.channels[channel].current_w.to_integral_value()))
			o.append(str(msg.channels[channel].daily_wh.to_integral_value()))
		
		o = ':'.join(o)
		
		# update database
		res = rrdtool.update(self.rrd, o)
		
		if res:
			print rrdtool.error()

if __name__ == '__main__':
	parser = ArgumentParser()
	
	parser.add_argument('-s', '--src', dest='src', help='Source address to accept data from.  This is the IP of your OWL Intuition.')
	
	parser.add_argument('-i', '--iface', dest='iface', default='', help='Network interface to use for getting data.')
	
	parser.add_argument('-r', '--rrd', dest='rrd', help='Path to RRD database')
	
	options = parser.parse_args()
	
	protocol = RrdOwlProtocol(src=options.src, rrd=options.rrd, iface=options.iface)
	
	reactor.listenMulticast(MCAST_PORT, protocol, listenMultiple=True)
	reactor.run()
