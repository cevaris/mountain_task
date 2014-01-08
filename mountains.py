#!/usr/bin/env python
#!/bin/env python

import os
import sys
import csv
import datetime
import re
import string
from optparse import OptionParser

import requests



class Formatter():
  def format(self,data):
    raise NotImplementedError

class MountainAltFormatter(Formatter):
  def format(self,data):
    return "%s has an altitude of %s meters." % (data[0], data[1])


class Fetch():
  def __init__(self, url=None):
    self.url       = url
    self.is_stream = False
    self.request   = None

    if self.url:
      self.get(self.url)

  def get(self, url):
    self.request = requests.get(url, data={'track': 'requests'}, stream=self.is_stream)
  
class Stream(Fetch):
  def __init__(self, url=None):
    Fetch.__init__(self,url)
    self.is_stream = True
    self.stream = self.request.iter_lines()

  def __iter__(self):
    for line in self.stream:
      if line:
        yield unicode(line)
  
  def next(self):
    self.stream.next()




class MountainTask():
  

  def execute(self, stream):
    DELIM  = u','
    NULL   = u"null"
    UKNOWN = u'unknown'

    formatter = MountainAltFormatter()


    stream.next() # Skip header
    for mountain in stream:
      regex = re.compile( r"%s" % DELIM, re.UNICODE )
      data = regex.split(mountain)

      name     = data[1]
      altitude = data[5] if data[5] != NULL else UKNOWN
      sys.stdout.write("%s\n" % formatter.format([name,altitude]))
    




def header():
  current_time = datetime.datetime.now()
  return current_time.strftime(u"%Y-%m-%d %H:%M:%S (%A)\n")


def execute((options, args)):

  print header()

  mountain_stream = Stream(args[0])
  mountains = MountainTask()
  mountains.execute(mountain_stream)









# Set the CL options 
parser = OptionParser()
usage = "usage: %prog [options] URL"

# parser.add_option("-m", "--month", type="string",
#                   help="select month from  01|02|...|12",
#                   dest="mon")

# parser.add_option("-u", "--user", type="string",
#                   help="name of the user",
#                   dest="vos")





execute(parser.parse_args())

# if options.mon and options.vos:
#     thisMonth = abbrMonth(options.mon)
#     print "I'm '%s' and this month is '%s'" % (options.vos, thisMonth)
#     sys.exit(0)

# if not options.mon and not options.vos:
#     options.mon = strftime("%m")

# if options.mon:
#     thisMonth = abbrMonth(options.mon)
#     print "The month is: %s" % thisMonth

# if options.vos:
#     print "My name is: %s" % options.vos