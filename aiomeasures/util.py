__all__ = ['parse_addr']


class Address(tuple):
    """Defines what is a net address.
    """
    def __new__(cls, proto, host, port):
        return super().__new__(cls, (host, port))

    def __init__(self, proto, host, port):
        self.proto = proto
        self.host = host
        self.port = port

    def __hash__(self):
        return id((self.proto, self.host, self.port))

    def __eq__(self, other):
        return other == (self.proto, self.host, self.port)

    def __str__(self):
        return '%s://%s:%s' % (self.proto, self.host, self.port)


def parse_addr(addr, *, proto=None, host=None):
    """Parses an address;

    Returns:
        Address: the parsed address
    """
    port = None

    if isinstance(addr, Address):
        return addr

    elif isinstance(addr, str):
        if addr.startswith('udp://'):
            proto, addr = 'udp', addr[6:]
        elif addr.startswith('tcp://'):
            proto, addr = 'tcp', addr[6:]
        elif addr.startswith('unix://'):
            proto, addr = 'unix', addr[7:]
        a, _, b = addr.partition(':')
        host = a or host
        port = b or port

    elif isinstance(addr, (tuple, list)):
        # list is not good
        a, b = addr
        host = a or host
        port = b or port

    elif isinstance(addr, int):
        port = addr

    else:
        raise ValueError('bad value')

    if port is not None:
        port = int(port)
    return Address(proto, host, port)
