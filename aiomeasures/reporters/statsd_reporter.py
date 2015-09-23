import asyncio
import logging
from aiomeasures.util import parse_addr


class StatsDReporter:

    def __init__(self, addr, *, loop=None):
        """Sends statistics to the stats daemon over UDP

        Parameters:
            addr (str): the address in the form udp://host:port
            loop (EventLoop): the event loop
        """
        self.addr = parse_addr(addr, proto='udp')
        self.loop = loop or asyncio.get_event_loop()
        self.log = logging.getLogger(__name__)
        self.protocol = None
        self._connecting = asyncio.Lock(loop=self.loop)
        self.protocol = None

    @asyncio.coroutine
    def send(self, metrics):
        """Sends key/value pairs via UDP or TCP.
        """
        msg = bytearray()
        for metric in metrics:
            msg += bytes('%s\n' % metric, encoding='utf-8')
        self.protocol.send(msg)

    @asyncio.coroutine
    def connect(self):
        if self.protocol:
            return

        with (yield from self._connecting):
            if not self.protocol:
                transport, protocol = yield from connect(self.addr, self.loop)
                self.protocol = protocol

    def close(self):
        self.protocol.close()


class UDPProtocol(asyncio.Protocol):

    def __init__(self):
        self.log = logging.getLogger(__name__)

    def send(self, msg):
        self.log.debug('send %s', msg)
        self.transport.sendto(msg)

    def connection_made(self, transport):
        addr = '%s:%s' % transport.get_extra_info('peername')
        self.log.info('connected to %s', addr)
        self.transport = transport

    def datagram_received(self, data, addr):
        self.log.debug('received %s', data.decode())

    def error_received(self, exc):
        addr = '%s:%s' % self.transport.get_extra_info('peername')
        self.log.warning('error received %s %s', addr, exc)

    def connection_lost(self, exc):
        self.log.warning("socket closed")

    def close(self):
        if self.transport:
            self.transport.close()


@asyncio.coroutine
def connect(addr, loop):
    if addr.proto == 'udp':
        transport, protocol = yield from loop.create_datagram_endpoint(
            lambda: UDPProtocol(),
            remote_addr=addr
        )
    else:
        raise NotImplementedError()
    return transport, protocol
