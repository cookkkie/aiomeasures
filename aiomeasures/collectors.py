from collections import deque
from aiomeasures.events import Event


class Collector(deque):
    """Caped list of metrics
    """

    def flush(self, rate=None, formatter=None):
        while True:
            try:
                metric = self.popleft()
                if isinstance(metric, Event):
                    yield formatter(metric)
                    continue
                if metric.value is None:
                    continue
                if rate and metric.rate and rate < metric.rate:
                    continue
                if formatter:
                    try:
                        yield formatter(metric)
                    except ValueError:
                        continue
                else:
                    yield metric
            except IndexError:
                raise StopIteration
