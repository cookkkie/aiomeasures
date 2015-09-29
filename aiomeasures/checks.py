__all__ = ['Check']


class Check:

    __slots__ = ('name', 'status', 'timestamp', 'hostname', 'tags', 'message')

    def __init__(self, name, status, timestamp=None,
                 hostname=None, tags=None, message=None):
        self.name = name
        self.status = status
        self.timestamp = timestamp
        self.hostname = hostname
        self.tags = tags
        self.message = message

    def __repr__(self):
        args = ['%s=%s' for attr in ()]
        attrs = ('name', 'status', 'tags')
        for attr in attrs:
            value = getattr(self, attr, None)
            if value is not None:
                args.append('%s=%r' % (attr, value))
        return '<%s(%s)>' % (self.__class__.__name__, ', '.join(args))
