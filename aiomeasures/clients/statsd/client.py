import asyncio
import logging
from . import formatting
from aiomeasures.clients.bases import Client
from aiomeasures.collectors import Collector
from aiomeasures.reporters import StatsDReporter
from random import random


class StatsD(Client):

    def __init__(self, addr, *, prefix=None, loop=None):
        """Sends statistics to the stats daemon over UDP

        Parameters:
            addr (str): the address in the form udp://host:port
            loop (EventLoop): the event loop
        """
        self.loop = loop or asyncio.get_event_loop()
        self.log = logging.getLogger(__name__)
        self.prefix = prefix
        self.collector = Collector([], 5000)
        self.reporter = StatsDReporter(addr, loop=self.loop)

    def register(self, metric):
        self.log.debug('register %s', metric)
        self.collector.append(metric)
        self.loop.create_task(self.send())
        return metric

    def format(self, obj):
        return formatting.format(obj, self.prefix)

    @asyncio.coroutine
    def send(self):
        """Sends key/value pairs to StatsD Server.
        """
        yield from self.reporter.connect()
        rate = random()
        formatter = self.format
        metrics = self.collector.flush(rate=rate, formatter=formatter)
        yield from self.reporter.send(metrics)

    def close(self):
        self.reporter.close()
