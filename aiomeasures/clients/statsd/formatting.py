from aiomeasures.checks import Check
from aiomeasures.events import Event
from aiomeasures.metrics import CountingMetric, GaugeMetric
from aiomeasures.metrics import HistogramMetric, SetMetric, TimingMetric
from collections.abc import Mapping
from datetime import datetime, timedelta
from decimal import Decimal
try:
    from functools import singledispatch
except:
    from singledispatch import singledispatch


@singledispatch
def format(obj, prefix=None, tags=None):
    raise ValueError('Cannot consume %r' % obj)


@format.register(Check)
def format_check(check, prefix=None, tags=None):
    response = '_sc|%s' % check.name
    if check.status in (0, 'ok', 'OK'):
        response += '|0'
    if check.status in (1, 'warn', 'warning', 'WARNING'):
        response += '|1'
    if check.status in (2, 'crit', 'critical', 'CRITICAL'):
        response += '|2'
    if check.status in (3, 'unknown', 'UNKNOWN'):
        response += '|3'

    if check.timestamp:
        response += '|d:%s' % format_timestamp(check.timestamp)
    if check.hostname:
        response += '|h:%s' % check.hostname
    if check.tags or tags:
        tags = format_tags(check.tags, tags)
        response += '|#%s' % ','.join(tags)
    if check.message:
        response += '|m:%s' % check.message
    return response


@format.register(Event)
def format_event(event, prefix=None, tags=None):
    a, b = len(event.title), len(event.text)
    response = '_e{%s,%s}%s|%s' % (a, b, event.title, event.text)
    if event.date_happened:
        response += '|d:%s' % format_timestamp(event.date_happened)
    if event.hostname:
        response += '|h:%s' % event.hostname
    if event.aggregation_key:
        response += '|k:%s' % event.aggregation_key
    if event.priority:
        response += '|p:%s' % event.priority
    if event.source_type_name:
        response += '|s:%s' % event.source_type_name
    if event.alert_type:
        response += '|t:%s' % event.alert_type

    if event.tags or tags:
        tags = format_tags(event.tags, tags)
        response += '|#%s' % ','.join(tags)
    return response


@format.register(CountingMetric)
def format_counting(metric, prefix=None, tags=None):
    name, value, suffix = format_metric(metric, prefix, tags)
    return '%s:%s|c%s' % (name, value, suffix)


@format.register(HistogramMetric)
def format_histogram(metric, prefix=None, tags=None):
    name, value, suffix = format_metric(metric, prefix, tags)
    return '%s:%s|h%s' % (name, value, suffix)


@format.register(GaugeMetric)
def format_gauge(metric, prefix=None, tags=None):
    name, value, suffix = format_metric(metric, prefix, tags)
    return '%s:%s|g%s' % (name, value, suffix)


@format.register(SetMetric)
def format_set(metric, prefix=None, tags=None):
    name, value, suffix = format_metric(metric, prefix, tags)
    return '%s:%s|s%s' % (name, value, suffix)


@format.register(TimingMetric)
def format_timing(metric, prefix=None, tags=None):
    name, value, suffix = format_metric(metric, prefix, tags)
    return '%s:%s|ms%s' % (name, value, suffix)


def format_metric(metric, prefix=None, tags=None):
    name = format_name(metric.name, prefix)
    value = format_value(metric.value, metric.delta)

    suffix = ''
    if metric.rate is not None:
        suffix += '|%s' % format_rate(metric.rate)

    if metric.tags or tags:
        tags = format_tags(metric.tags, tags)
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


def format_tags(obj, defaults=None):
    result = set()
    for src in (obj, defaults):
        if isinstance(src, Mapping):
            result.update(['%s:%s' % (k, v) for k, v in src.items()])
        elif isinstance(src, list):
            result.update(src)
        elif isinstance(src, str):
            result.add(src)
    return sorted(result)


def format_name(name, prefix=None):
    if prefix:
        return '%s.%s' % (prefix, name)
    return '%s' % name


def format_value(value, delta=None):
    if delta and value > 0:
        return '+%s' % value
    return '%s' % value


def format_timestamp(value):
    if isinstance(value, datetime):
        return int(value.timestamp())
    if isinstance(value, float):
        return int(value)
    return value
