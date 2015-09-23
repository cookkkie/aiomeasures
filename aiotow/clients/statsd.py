from .bases import Client
from aiotow.events import Event
from aiotow.metrics import CountingMetric, GaugeMetric
from aiotow.metrics import HistogramMetric, SetMetric, TimingMetric
from datetime import timedelta
from decimal import Decimal
from functools import singledispatch


class StatsD(Client):

    def format(self, obj, prefix=None):
        return format(obj, prefix)


@singledispatch
def format(obj, prefix=None):
    raise ValueError('Cannot consume %r' % obj)


@format.register(Event)
def format_event(event, prefix=None):
    a, b = len(event.title), len(event.text)
    response = '_e{%s,%s}%s|%s' % (a, b, event.title, event.text)
    if event.alert_type:
        response += '|t:%s' % event.alert_type
    if event.aggregation_key:
        response += '|k:%s' % event.aggregation_key
    if event.priority:
        response += '|p:%s' % event.priority
    if event.tags:
        tags = format_tags(event.tags)
        response += '|#%s' % ','.join(tags)
    return response


@format.register(CountingMetric)
def format_counting(metric, prefix=None):
    name, value, suffix = format_metric(metric, prefix)
    return '%s:%s|c%s' % (name, value, suffix)


@format.register(HistogramMetric)
def format_histogram(metric, prefix=None):
    name, value, suffix = format_metric(metric, prefix)
    return '%s:%s|h%s' % (name, value, suffix)


@format.register(GaugeMetric)
def format_gauge(metric, prefix=None):
    name, value, suffix = format_metric(metric, prefix)
    return '%s:%s|g%s' % (name, value, suffix)


@format.register(SetMetric)
def format_set(metric, prefix=None):
    name, value, suffix = format_metric(metric, prefix)
    return '%s:%s|s%s' % (name, value, suffix)


@format.register(TimingMetric)
def format_timing(metric, prefix=None):
    name, value, suffix = format_metric(metric, prefix)
    return '%s:%s|ms%s' % (name, value, suffix)


def format_metric(metric, prefix=None):
    name = format_name(metric.name, prefix)
    value = format_value(metric.value, metric.delta)

    suffix = ''
    if metric.rate is not None:
        suffix += '|%s' % format_rate(metric.rate)

    if metric.tags:
        tags = format_tags(metric.tags)
        suffix += '|#%s' % ','.join(tags)

    return name, value, suffix


def format_rate(obj):
    if isinstance(obj, (float, int, Decimal)):
        return '@%s' % obj
    if isinstance(obj, timedelta):
        interval = float(obj.seconds)
        if obj.microseconds:
            interval += obj.microseconds / 1000000

        if obj.days:
            interval += obj.days * 24 * 3600
        data = '@%.3f' % interval
        data = data.rstrip('0')
        data = data.rstrip('.')
        return data


def format_tags(obj):
    return ['%s:%s' % (k, v) for k, v in obj.items()]


def format_name(name, prefix=None):
    if prefix:
        return '%s.%s' % (name)
    return '%s' % name


def format_value(value, delta=None):
    if delta and value > 0:
        return '+%s' % value
    return '%s' % value
