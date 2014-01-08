#!/usr/bin/env python
#!/bin/env python

import os
import sys
import csv
import datetime
import re
import string
import logging
import abc
import time

from optparse import OptionParser
from Queue import Queue
from threading import Thread
import threading


import requests

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("Mountains")

class Worker(Thread):
    """
    Thread executing tasks from a given tasks queue
    """
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()
    
    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try: func(*args, **kargs)
            except Exception, e: print e
            self.tasks.task_done()

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads): Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()


class CSVParser(object):
    """
    Given string of CSV format, maps the header data to the value.
    Result is a dictionary of CSV header name -> column value.
    """

    DELIM = u','
    REGEX = re.compile(r"%s" % DELIM, re.UNICODE)

    def __init__(self):
        self.head = None
        
    def set_header(self, head):
        if head and (type(head) == str):
            self.head = self.REGEX.split(head)

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
    """Base class for creating custom string formats"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def format(self, data):
        """Return formatted string given an array of data"""


class MountainAltFormatter(Formatter):
    def format(self, data):
        return "%s has an altitude of %s meters." % (data[0], data[1])

class Fetch(object):
    """Interface for making HTTP GET commands to a given URL"""
    __metaclass__ = abc.ABCMeta

    def __init__(self, url=None):
        self.url = url

    @abc.abstractmethod
    def get(self, url):
        """Fetch data from provided URL"""


class RequestsFetch(Fetch):
    """Python Requests implementation of Fetch interface"""

    def __init__(self, url=None):
        self.url = url
        self.is_stream = False

    def get(self, url):
        self.url = url
        self.request = requests.get(url, stream=self.is_stream)

        try:
            self.request.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error("HTTP Error [%s] [%s]\n" % (e, self.url))
            raise



class Stream(RequestsFetch):
    """"Stream implementation of RequestsFetch"""

    def __init__(self, url=None):
        self.is_stream = True
        self.get(url)
        self.stream = self.request.iter_lines()


    def __iter__(self):
        """Generator for streaming each line of Requests.GET"""
        for line in self.stream:
            if line:
                yield unicode(line)

    def next(self):
        return self.stream.next()


class Task(object):
    """Base class for modularizing general tasks"""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute(self):
        pass


ALTITUDE = 'Altitude (m)'
NAME = 'Name'
NULL = u"null"
UKNOWN = u'unknown'


class MountainTask(Task):

    def __init__(self, stream):
        self.stream = stream
        self.formatter = MountainAltFormatter()
        self.csv_parser = CSVParser()
        self.execute()
        
    def output(self, batch_messages):

        report = []
        for message in batch_messages:
            data = self.csv_parser.parse_line(message)
            
            name = data[NAME]
            altitude = data[ALTITUDE] if data[ALTITUDE] != NULL else UKNOWN
            # sys.stdout.write("%s\n" % self.formatter.format([name, altitude]))
            # print "%s - %s" % (threading.current_thread().name, self.formatter.format([name, altitude]))
            report.append("%s - %s\n" % (threading.current_thread().name, self.formatter.format([name, altitude])))
        
        sys.stdout.write("".join(report))

    def execute(self):
        
        self.csv_parser.set_header(self.stream.next())
        
        
        thread_pool = ThreadPool(25)        
        max_count = 1000
        batch_count = 0
        batch = []
        for mountain_data in self.stream:
            batch.append(mountain_data)
            
            if len(batch) > max_count:
                thread_pool.add_task(self.output, batch)
                batch = []
            # data = self.csv_parser.parse_line(mountain_data)
        
            # name = data[NAME]
            # altitude = data[ALTITUDE] if data[ALTITUDE] != NULL else UKNOWN
            # sys.stdout.write("%s\n" % self.formatter.format([name, altitude]))

        # Flush out the last of the batched data
        thread_pool.add_task(self.output, batch)
        thread_pool.wait_completion()


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
