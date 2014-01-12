#!/usr/bin/env python
"""
intuition/tests.py - Tests for Network Owl protocol parser
Copyright 2013-2014 Michael Farrell <micolous+git@gmail.com>

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
from .protocol import parse_datagram, OwlElectricity, OwlHeating, OwlChannel, OwlTemperature
from decimal import Decimal

def test_electricity():
	packet = """\
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
</electricity>"""

	msg = parse_datagram(packet)

	assert msg.mac == '443719123456'
	assert msg.rssi == -42
	assert msg.lqi == 15
	assert len(msg.channels) == 3
	assert msg.battery == 100
	
	for k, v in msg.channels.iteritems():
		assert msg.channels[k].channel_id == k
		assert isinstance(msg.channels[k].current_w, Decimal)
		assert isinstance(msg.channels[k].daily_wh, Decimal)

	assert msg.channels['0'].current_w == Decimal('257.00')
	assert msg.channels['0'].daily_wh == Decimal('17.13')
	assert msg.channels['1'].current_w == Decimal('96.00')
	assert msg.channels['1'].daily_wh == Decimal('6.40')
	assert msg.channels['2'].current_w == Decimal('32.00')
	assert msg.channels['2'].daily_wh == Decimal('2.13')


def test_heating_22():
	# from official protocol documentation
	packet = """\
<heating id='00A0C914C851'>
 <signal rssi='-61' lqi='48'/>
 <battery level='2730mV'/>
 <temperature until='1359183600' zone='0'>
  <current>22.37</current>
  <required>15.00</required>
 </temperature>
</heating>
"""
	
	msg = parse_datagram(packet)
	
	assert msg.mac == '00A0C914C851'
	assert msg.rssi == -61
	assert msg.lqi == 48
	assert len(msg.zones) == 1
	
	assert msg.zones['0'].zone_id == '0'
	assert msg.zones['0'].current_temp == Decimal('22.37')
	assert msg.zones['0'].required_temp == Decimal('15.00')
