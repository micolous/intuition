#!/bin/sh

# create database for storing channel data
# each channel has a maximum of:
#   watt: 50KW current detection
#   wh:   50KW * 24 hours = 1 200 kWh   (reset daily on device at midnight)

rrdtool create $1 --step 60 \
  DS:0_watt:GAUGE:600:U:U \
  DS:0_wh:COUNTER:600:U:U \
  DS:1_watt:GAUGE:600:U:U \
  DS:1_wh:COUNTER:600:U:U \
  DS:2_watt:GAUGE:600:U:U \
  DS:2_wh:COUNTER:600:U:U \
  RRA:AVERAGE:0.5:1:600   \
  RRA:AVERAGE:0.5:6:700   \
  RRA:AVERAGE:0.5:24:775  \
  RRA:AVERAGE:0.5:288:797 \
  RRA:MAX:0.5:1:600       \
  RRA:MAX:0.5:6:700       \
  RRA:MAX:0.5:24:775      \
  RRA:MAX:0.5:444:797
