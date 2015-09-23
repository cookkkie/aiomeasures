
__all__ = ['Event']


class Event:

    def __init__(self,
                 title,
                 text,
                 alert_type=None,
                 aggregation_key=None,
                 priority=None,
                 tags=None):
        self.title = title
        self.text = text
        self.alert_type = alert_type
        self.aggregation_key = aggregation_key
        self.priority = priority
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
