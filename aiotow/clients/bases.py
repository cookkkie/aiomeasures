import asyncio
import logging
from abc import ABCMeta, abstractmethod
from collections import deque
from aiotow.events import Event
from aiotow.metrics import CountingMetric, GaugeMetric
from aiotow.metrics import HistogramMetric, SetMetric, TimingMetric
from time import perf_counter


class Client(metaclass=ABCMeta):

    def __init__(self, addr, *, prefix=None, loop=None):
        """Sends statistics to the stats daemon over UDP

        Parameters:
            addr (str): the address in the form udp://host:port
            loop (EventLoop): the event loop
        """
        self.addr = parse_addr(addr, proto='udp')
        self.loop = loop or asyncio.get_event_loop()
        self.log = logging.getLogger(__name__)
        self.prefix = prefix
        self.protocol = None
        self.queue = deque([], 5000)

    def incr(self, name, value=None, rate=None, tags=None):
        value = abs(value or 1)
        metric = CountingMetric(name, value, rate=rate, tags=tags)
        return self.register(metric)

    def decr(self, name, value=None, rate=None, tags=None):
        value = -abs(value or 1)
        metric = CountingMetric(name, value, rate=rate, tags=tags)
        return self.register(metric)

    def timing(self, name, value=None, rate=None, tags=None):
        metric = TimingMetric(name, value, rate=rate, tags=tags)
        return self.register(metric)

    def timer(self, name, rate=None, tags=None):
        return Timer(client=self, name=name, rate=rate, tags=tags)

    def gauge(self, name, value, rate=None, delta=False):
        metric = GaugeMetric(name, value, rate=rate, delta=delta)
        return self.register(metric)

    def histogram(self, name, value, rate=None, delta=False):
        metric = HistogramMetric(name, value, rate=rate, delta=delta)
        return self.register(metric)

    def set(self, name, value, rate=None, tags=None):
        metric = SetMetric(name, value, rate=rate, tags=tags)
        return self.register(metric)

    def event(self, title, text, alert_type=None, aggregation_key=None,
              source_type_name=None, date_happened=None, priority=None,
              tags=None, hostname=None):
        event = Event(title, text, alert_type, priority)
        return self.register(event)

    @abstractmethod
    def format(self, metric, prefix=None):
        raise NotImplementedError()

    @asyncio.coroutine
    def send(self):
        """Sends key/value pairs via UDP or TCP.
        """
        if not self.protocol:
            transport, protocol = yield from connect(self.addr, self.loop)
            self.protocol = protocol

        msg = bytearray()
        for metric in self.flush():
            msg += bytes('%s\n' % metric, encoding='utf-8')
        self.protocol.send(msg)

    def register(self, metric):
        self.queue.append(metric)
        self.loop.create_task(self.send)
        return metric

    def flush(self):
        while self.metrics:
            metric = self.metrics.popleft()
            if metric.value is None:
                continue
            try:
                yield self.format(metric, self.prefix)
            except ValueError:
                continue


class UDPProtocol(asyncio.Protocol):

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def send(self, msg):
        self.log.debug('send %s', msg)
        self.transport.sendto(msg)

    def connection_made(self, transport):
        addr = '%s:%s' % transport.get_extra_info('peername')
        self.log.info('connected to %s', addr)
        self.transport = transport

    def datagram_received(self, data, addr):
        self.log.debug('received %s', data.decode())

    def error_received(self, exc):
        addr = '%s:%s' % self.transport.get_extra_info('peername')
        self.log.warning('error received %s %s', addr, exc)

    def connection_lost(self, exc):
        self.log.warning("socket closed")

    def close(self):
        if self.transport:
            self.transport.close()


@asyncio.coroutine
def connect(addr, loop):
    if addr.proto == 'udp':
        transport, protocol = yield from loop.create_datagram_endpoint(
            lambda: UDPProtocol(),
            remote_addr=addr
        )
    else:
        raise NotImplementedError()
    return transport, protocol


class Timer:

    def __init__(self, client, name, rate=None, tags=None):
        self.client = client
        self.name = name
        self.rate = rate
        self.tags = tags

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            try:
                self.start()
                return func(*args, **kwargs)
            finally:
                self.stop()
        return wrapper

    def __enter__(self):
        self.start()

    def __exit__(self, type, value, tb):
        self.stop()

    def start(self):
        self._started = perf_counter()

    def stop(self):
        value = int((perf_counter() - self._started) * 1000)
        self.client.timing(self.name, value, rate=self.rate, tags=self.tags)
