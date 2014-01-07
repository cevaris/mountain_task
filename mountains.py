#!/usr/bin/env python
#!/bin/env python

import os
import sys
import csv
import datetime
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
      self.request = self.get(self.url)

  def get(self, url):
    return requests.get(url, data={'track': 'requests'}, stream=self.is_stream)

  
class Stream(Fetch):
  def __init__(self, url=None):
    Fetch.__init__(self,url)
    self.is_stream = True

  def __iter__(self):
    for line in self.request.iter_lines():
      if line:
        yield line


class MountainAltStream():

  def __init__(self):
    csv_reader = csv.reader()
    
    


def header():
  current_time = datetime.datetime.now()
  return current_time.strftime("%Y-%m-%d %H:%M:%S (%A)\n")


def execute((options, args)):

  f = MountainAltFormatter()
  print f.format(["test",'2423'])
  print f.format(["1test",'uknown'])

  print header()

  m_stream = Stream(args[0])
  for m in m_stream:
    print m

  # https://s3.amazonaws.com/miscs.random/mountains-1.csv

  # writer = csv.writer(sys.stdout, delimiter=',')
  # for mountain in fetch_csv(args[0]):
  #   writer.writerows(mountain)















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