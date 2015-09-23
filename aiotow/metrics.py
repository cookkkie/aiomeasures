
__all__ = [
    'Metric', 'CountingMetric', 'GaugeMetric',
    'HistogramMetric', 'SetMetric', 'TimingMetric'
]


class Metric:

    __slots__ = ('name', 'value', 'rate', 'delta', 'tags')

    def __init__(self, name, value, rate=None, delta=False, tags=None):
        """
        Parameters:
            name (str): name of the metric
            value (obj): value of the metric
            rate (float): sample of metric (optional)
        """

        self.name = name
        self.value = value
        self.rate = rate
        self.delta = delta
        self.tags = tags

    def __eq__(self, other):
        if isinstance(other, Metric):
            other = other.__str__()
        return self.__str__() == other

    def __repr__(self):
        args = ['%s=%s' for attr in ()]
        for attr in ('name', 'value', 'rate', 'delta', 'tags'):
            value = getattr(self, attr, None)
            if value is not None:
                args.append('%s=%r' % (attr, value))
        return '<%s(%s)>' % (self.__class__.__name__, ', '.join(args))


class CountingMetric(Metric):
    """Count things.
    """


class GaugeMetric(Metric):
    """Measure the value of a particular thing over time
    """


class HistogramMetric(Metric):
    """Measure the statistical distribution of a set of values.
    """


class SetMetric(Metric):
    """Count the number of unique elements in a group
    """


class TimingMetric(Metric):
    """Measure the statistical distribution of a set of values.
    """
