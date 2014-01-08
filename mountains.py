#!/usr/bin/env python
#!/bin/env python

import os
import sys
import csv
import datetime
import re
import string
import logging
from optparse import OptionParser

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Mountains")

class CSVParser(object):
    DELIM = u','
    REGEX = re.compile(r"%s" % DELIM, re.UNICODE)

    def __init__(self, head=None):
        if head and (type(head) == str):
            self.head = self.REGEX.split(head)
        else:
            self.head = None

    def parse(self, document):
        raise NotImplementedError

    def parse_line(self, line):
        result = {}
        data = self.REGEX.split(line)

        for index, value in enumerate(data):
            if self.head:
                result[self.head[index]] = value
            else:
                result[str(index)] = value

        return result


class Formatter(object):
    def format(self, data):
        raise NotImplementedError


class MountainAltFormatter(Formatter):
    def format(self, data):
        return "%s has an altitude of %s meters." % (data[0], data[1])

class Fetch(object):
    def __init__(self, url=None):
        self.url = url

    def get(self, url):
        raise NotImplementedError


class RequestsFetch(Fetch):
    def __init__(self, url=None):
        Fetch.__init__(self, url)
        self.is_stream = False
        self.request = None

        if self.url:
            self.get(self.url)

    def get(self, url):
        self.url = url
        self.request = requests.get(url, stream=self.is_stream)

        try:
            self.request.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP Error %s for URL '%s'\n" % (e, self.url))
            raise



class Stream(RequestsFetch):
    def __init__(self, url=None):
        RequestsFetch.__init__(self, url)
        self.is_stream = True
        self.stream = self.request.iter_lines()

    def __iter__(self):
        for line in self.stream:
            if line:
                yield unicode(line)

    def next(self):
        return self.stream.next()


class Task(object):
    def execute(self):
        raise NotImplementedError


class MountainTask(Task):

    def __init__(self, stream):
        self.stream = stream
        self.execute()

    def execute(self):
        
        NULL = u"null"
        UKNOWN = u'unknown'
        ALTITUDE = 'Altitude (m)'
        NAME = 'Name'

        formatter = MountainAltFormatter()
        csv_parser = CSVParser(self.stream.next())
        
        for mountain_data in self.stream:
            data = csv_parser.parse_line(mountain_data)
        
            name = data[NAME]
            altitude = data[ALTITUDE] if data[ALTITUDE] != NULL else UKNOWN
            sys.stdout.write("%s\n" % formatter.format([name, altitude]))


def header():
    current_time = datetime.datetime.now()
    return current_time.strftime(u"%Y-%m-%d %H:%M:%S (%A)\n")


def main((options, args)):
    print header()

    mountain_stream = Stream(args[0])
    mountains = MountainTask(mountain_stream)

if __name__ == "__main__":
    parser = OptionParser()
    usage = "usage: %prog [options] URL"

    main(parser.parse_args())
