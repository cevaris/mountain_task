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
    def format(self, data):
        raise NotImplementedError


class MountainAltFormatter(Formatter):
    def format(self, data):
        return "%s has an altitude of %s meters." % (data[0], data[1])


class Fetch():
    def __init__(self, url=None):
        self.url = url
        self.is_stream = False
        self.request = None

        if self.url:
            self.get(self.url)

    def get(self, url):
        self.url = url
        self.request = requests.get(url, stream=self.is_stream)


class Stream(Fetch):
    def __init__(self, url=None):
        Fetch.__init__(self, url)
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
        DELIM = u','
        NULL = u"null"
        UKNOWN = u'unknown'

        formatter = MountainAltFormatter()

        # Skip header
        stream.next()
        for mountain in stream:
            regex = re.compile(r"%s" % DELIM, re.UNICODE)
            data = regex.split(mountain)

            name = data[1]
            altitude = data[5] if data[5] != NULL else UKNOWN
            sys.stdout.write("%s\n" % formatter.format([name, altitude]))


def header():
    current_time = datetime.datetime.now()
    return current_time.strftime(u"%Y-%m-%d %H:%M:%S (%A)\n")


def main((options, args)):
    print header()

    mountain_stream = Stream(args[0])
    mountains = MountainTask()
    mountains.execute(mountain_stream)

if __name__ == "__main__":
    parser = OptionParser()
    usage = "usage: %prog [options] URL"

    main(parser.parse_args())
