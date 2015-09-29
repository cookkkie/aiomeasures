"""
    We’ll walk through the types of metrics supported by DogStatsD in Python,
    but the principles are easily translated into other languages.
"""

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

    Counters track how many times something happened per second,
    like the number of database requests or page views.
    """


class GaugeMetric(Metric):
    """Measure the value of a particular thing over time.

    Gauges measure the value of a particular thing at a particular time,
    like the amount of fuel in a car’s gas tank or the number of users
    connected to a system.
    """


class HistogramMetric(Metric):
    """Measure the statistical distribution of a set of values.

    Histograms track the statistical distribution of a set of values,
    like the duration of a number of database queries or the size of files
    uploaded by users.
    """


class SetMetric(Metric):
    """Count the number of unique elements in a group.

    Sets are used to count the number of unique elements in a group.
    If you want to track the number of unique visitor to your site,
    sets are a great way to do that.
    """


class TimingMetric(Metric):
    """Measure the statistical distribution of a set of values.

    StatsD only supports histograms for timing, not generic values (like
    the size of uploaded files or the number of rows returned from a query).
    Timers are essentially a special case of histograms, so they are treated
    in the same manner by DogStatsD for backwards compatibility.
    """
