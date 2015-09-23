from .bases import Client
from datetime import timedelta
from decimal import Decimal


class Datadog(Client):

    def format(self, obj, prefix=None):
        raise NotImplementedError()


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
