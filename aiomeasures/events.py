
__all__ = ['Event']


class Event:
    """
    You can post events to your Datadog event stream.
    You can tag them, set priority and even aggregate them with other events.

    Parameters:
        title (str): Event title
        text (str): Event text. Supports line breaks

        date_happened (datetime): Assign a timestamp to the event.
                                  Default is now when none.
        hostname (str): Assign a hostname to the event.
        aggregation_key (str): Assign an aggregation key to the event,
                               to group it with some others.
        priority (str): Can be `normal` or `low`. Default to `normal`
        source_type_name (str): Assign a source type to the event.
        alert_type (str): Can be `error`, `warning`, `info` or `success`.
                          default to `info`
        tags (list): An array of tags
    """

    __slots__ = ('title', 'text', 'date_happened', 'hostname', 'alert_type',
                 'aggregation_key', 'priority', 'source_type_name', 'tags')

    def __init__(self,
                 title,
                 text,
                 date_happened=None,
                 hostname=None,
                 alert_type=None,
                 aggregation_key=None,
                 priority=None,
                 source_type_name=None,
                 tags=None):
        self.title = title
        self.text = text
        self.date_happened = date_happened
        self.hostname = hostname
        self.alert_type = alert_type
        self.aggregation_key = aggregation_key
        self.priority = priority
        self.source_type_name = source_type_name
        self.tags = tags

    def __repr__(self):
        args = ['%s=%s' for attr in ()]
        attrs = ('title', 'text', 'alert_type',
                 'aggregation_key', 'priority', 'tags')
        for attr in attrs:
            value = getattr(self, attr, None)
            if value is not None:
                args.append('%s=%r' % (attr, value))
        return '<%s(%s)>' % (self.__class__.__name__, ', '.join(args))
