import asyncio
from abc import ABCMeta, abstractmethod
from aiomeasures.checks import Check
from aiomeasures.events import Event
from aiomeasures.metrics import CountingMetric, GaugeMetric
from aiomeasures.metrics import HistogramMetric, SetMetric, TimingMetric
from time import perf_counter


class Client(metaclass=ABCMeta):

    def incr(self, name, value=None, rate=None, tags=None):
        value = abs(value or 1)
        metric = CountingMetric(name, value, rate=rate, tags=tags)
        return self.register(metric)

    def decr(self, name, value=None, rate=None, tags=None):
        value = -abs(value or 1)
        metric = CountingMetric(name, value, rate=rate, tags=tags)
        return self.register(metric)

    def counter(self, name, value, rate=None, tags=None):
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

    def event(self, title, text, **kwargs):
        event = Event(title, text, **kwargs)
        return self.register(event)

    def check(self, name, status, **kwargs):
        check = Check(name, status, **kwargs)
        return self.register(check)

    @abstractmethod
    def format(self, metric, prefix=None):
        raise NotImplementedError()

    @asyncio.coroutine
    @abstractmethod
    def send(self):
        """Sends key/value pairs via UDP or TCP.
        """
        raise NotImplementedError()

    @abstractmethod
    def register(self, metric):
        raise NotImplementedError()

    @abstractmethod
    def close(self):
        raise NotImplementedError()


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
        value = (perf_counter() - self._started) * 1000
        self.client.timing(self.name, value, rate=self.rate, tags=self.tags)
