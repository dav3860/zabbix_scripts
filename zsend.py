#!/usr/bin/env python
# Copyright 2013 Rob Cherry <zsend(at)lxrb(dot)com>
# Based on work by Enrico Troeger <enrico(dot)troeger(at)uvena(dot)de>
# License: GNU GPLv2

import socket
import struct
import json
import os
import time
import sys
import re

ZABBIX_SERVER="127.0.0.1"
ZABBIX_PORT=10051

class ZSend:
   def __init__(self, server=ZABBIX_SERVER, port=ZABBIX_PORT, verbose=False):
      self.zserver = server
      self.zport = port
      self.verbose = verbose
      self.list = []
      self.inittime = int(round(time.time()))
      self.header = '''ZBXD\1%s%s'''
      self.datastruct = '''
{ "host":"%s",
  "key":"%s",
  "value":"%s",
  "clock":%s }'''

   def add_data(self,host,key,value,evt_time=None):
      if evt_time is None:
         evt_time = self.inittime
      self.list.append((host,key,value,evt_time))

   def print_vals(self):
      for (h,k,v,t) in self.list:
         print "Host: %s, Key: %s, Value: %s, Event: %s" % (h,k,v,t)

   def build_all(self):
      tmpdata = "{\"request\":\"sender data\",\"data\":["
      count = 0
      for (h,k,v,t) in self.list:
         tmpdata = tmpdata + self.datastruct % (h,k,v,t)
         count += 1
         if count < len(self.list):
            tmpdata = tmpdata + ","
      tmpdata = tmpdata + "], \"clock\":%s}" % self.inittime
      return (tmpdata)

   def build_single(self,dataset):
      tmpdata = "{\"request\":\"sender data\",\"data\":["
      (h,k,v,t) = dataset
      tmpdata = tmpdata + self.datastruct % (h,k,v,t)
      tmpdata = tmpdata + "], \"clock\":%s}" % self.inittime
      return (tmpdata)

   def send(self,mydata):
      socket.setdefaulttimeout(5)
      data_length = len(mydata)
      data_header = struct.pack('i', data_length) + '\0\0\0\0'
      data_to_send = self.header % (data_header, mydata)
      err = ""
      try:
         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         sock.connect((self.zserver,self.zport))
         sock.send(data_to_send)
      except Exception as err:
         sys.stderr.write("Error talking to server: %s\n" % err)
         return (255,err)

      response_header = sock.recv(5)
      if not response_header == 'ZBXD\1':
         sys.stderr.write("Invalid response from server." + \
                          "Malformed data?\n---\n%s\n---\n" % mydata)
         return (254,err)
      response_data_header = sock.recv(8)
      response_data_header = response_data_header[:4]
      response_len = struct.unpack('i', response_data_header)[0]
      response_raw = sock.recv(response_len)
      sock.close()
      response = json.loads(response_raw)
      match = re.match("^.*failed\s(\d+);\s.*$",str(response))
      if match is None:
         sys.stderr.write("Unable to parse server response - " + \
                          "\n%s\n" % response)
      else:
         fails = int(match.group(1))
         if fails > 0:
            if self.verbose is True:
               sys.stderr.write("Failures reported by zabbix when sending:" + \
                                "\n%s\n" % mydata)
            return (1,response)
      return (0,response)

   def bulk_send(self):
      data = self.build_all()
      result = self.send(data)
      return result

   def iter_send(self):
      retarray = []
      for i in self.list:
         (retcode,retstring) = self.send(self.build_single(i))
         retarray.append((retcode,i))
      return retarray


#####################################
# --- Examples of usage ---
#####################################
#
# Initiating a Zsend object -
# z = ZSend() # Defaults to using ZABBIX_SERVER,ZABBIX_PORT
# z = ZSend(verbose=True) # Prints all sending failures to stderr
# z = ZSend(server="172.0.0.100",verbose=True)
# z = ZSend(server="zabbix-server",port="10051")
# z = ZSend("zabbix-server","10051")
#

# --- Adding data to send later ---
# Host, Key, Value are all necessary
# z.add_data("host","cpu.ready","12")
#
# Optionally you can provide a specific timestamp for the sample
# z.add_data("host","cpu.ready","13","1365787627")
#
# If you provide no timestamp, the initialization time of the class
# is used.

# --- Printing values ---
# Not that useful, but if you would like to see your data in tuple form
# with assumed timestamps
# z.print_vals()

# --- Building well formatted data to send ---
# You can send all of the data in one batch -
# z.build_all() will return a string of packaged data ready to send
# z.build_single((host,key,value,timestamp)) will return a packaged single

# --- Sending data manually ---
# Typical example 1 - build all the data and send it in one batch -
#
# z.send(z.build_all())
#
# Alternate example - build the data individually and send it one by one
# so that we can see errors for anything that doesnt send properly -
#
# for i in z.list:
#    (code,ret) = z.send(z.build_single(i))
#    if code == 1:
#       print "Problem during send!\n%s" % ret
#    elif code == 0:
#       print ret
#
# --- Sending data with built in functions ---
#
# Sending everything at once, with no concern about
# individual item failure -
#
# (retcode,retstring) = z.bulk_send()
# print "Result: %s -> %s" % (str(retcode),retstring)
#
# Sending every item individually so that we can capture
# success or failure
#
# results = z.iter_send()
# for (code,data) in results:
#   (h,k,v,t) = data
#   if code == 1:
#      print "Failed to update key: %s for host: %s" % (k,h)
#
#
#####################################
# Mini example of a working program #
#####################################
#
# import sys
# sys.path.append("/path/to/Zsend.py")
# from ZSend import ZSend
#
# z = ZSend() # Defaults to using ZABBIX_SERVER,ZABBIX_PORT
# z.add_data("host1","cpu.ready","12")
# z.add_data("host1","cpu.ready","13",1366033479)
# z.print_vals()
#
# results = z.iter_send()
# for (code,data) in results:
#   (h,k,v,t) = data
#   if code == 1:
#      print "Failed to update key: %s for host: %s" % (k,h)
#
#####################################
