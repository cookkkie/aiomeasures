import aiomeasures
import asyncio
import pytest
from datetime import timedelta

simple = [
    (aiomeasures.CountingMetric('foo', 1), 'foo:1|c'),
    (aiomeasures.CountingMetric('foo', -1), 'foo:-1|c'),
    (aiomeasures.GaugeMetric('foo', 1), 'foo:1|g'),
    (aiomeasures.GaugeMetric('foo', -1), 'foo:-1|g'),
    (aiomeasures.HistogramMetric('foo', 42), 'foo:42|h'),
    (aiomeasures.HistogramMetric('foo', -42), 'foo:-42|h'),
    (aiomeasures.SetMetric('foo', 'bar'), 'foo:bar|s'),
    (aiomeasures.TimingMetric('foo', 100), 'foo:100|ms'),
]

one_second = timedelta(seconds=1)
twenty_ms = timedelta(microseconds=20000)

rated = [
    (aiomeasures.CountingMetric('foo', 1, 0.1), 'foo:1|c|@0.1'),
    (aiomeasures.GaugeMetric('foo', 1, 0.1), 'foo:1|g|@0.1'),
    (aiomeasures.SetMetric('foo', 'bar', 0.1), 'foo:bar|s|@0.1'),
    (aiomeasures.TimingMetric('foo', 100, 0.1), 'foo:100|ms|@0.1'),
    (aiomeasures.HistogramMetric('foo', -42, 0.1), 'foo:-42|h|@0.1'),

    (aiomeasures.CountingMetric('foo', 1, one_second), 'foo:1|c|@1'),
    (aiomeasures.GaugeMetric('foo', 1, one_second), 'foo:1|g|@1'),
    (aiomeasures.SetMetric('foo', 'bar', one_second), 'foo:bar|s|@1'),
    (aiomeasures.TimingMetric('foo', 100, one_second), 'foo:100|ms|@1'),
    (aiomeasures.HistogramMetric('foo', -42, one_second), 'foo:-42|h|@1'),

    (aiomeasures.CountingMetric('foo', 1, twenty_ms), 'foo:1|c|@0.02'),
    (aiomeasures.GaugeMetric('foo', 1, twenty_ms), 'foo:1|g|@0.02'),
    (aiomeasures.SetMetric('foo', 'bar', twenty_ms), 'foo:bar|s|@0.02'),
    (aiomeasures.TimingMetric('foo', 100, twenty_ms), 'foo:100|ms|@0.02'),
    (aiomeasures.HistogramMetric('foo', -42, twenty_ms), 'foo:-42|h|@0.02'),
]

tagged = [
    (aiomeasures.CountingMetric('foo', 1, tags={'bar': 'baz'}), 'foo:1|c|#bar:baz'),
    (aiomeasures.CountingMetric('foo', -1, tags={'bar': 'baz'}), 'foo:-1|c|#bar:baz'),
    (aiomeasures.GaugeMetric('foo', 1, tags={'bar': 'baz'}), 'foo:1|g|#bar:baz'),
    (aiomeasures.GaugeMetric('foo', -1, tags={'bar': 'baz'}), 'foo:-1|g|#bar:baz'),
    (aiomeasures.SetMetric('foo', 'bar', tags={'bar': 'baz'}), 'foo:bar|s|#bar:baz'),
    (aiomeasures.TimingMetric('foo', 100, tags={'bar': 'baz'}), 'foo:100|ms|#bar:baz'),
]

whole = simple + rated + tagged

@pytest.mark.parametrize('metric,expected', whole)
def test_formatting(metric, expected):
    handler = aiomeasures.StatsD(':0')
    assert handler.format(metric) == expected


tags = [
    ({}, {}, ''),
    ({'bar': 'baz'}, {}, '|#bar:baz'),
    ({}, {'bar': 'baz'}, '|#bar:baz'),
    ({'bar': 'baz'}, {'bar': 'qux'}, '|#bar:baz,bar:qux'),
]

@pytest.mark.parametrize('tags,defaults,expected', tags)
def test_tags(tags, defaults, expected):
    metric = aiomeasures.CountingMetric('foo', 1, tags=tags)
    handler = aiomeasures.StatsD(':0', tags=defaults)
    assert handler.format(metric) == 'foo:1|c%s' % expected


def test_events():
    event = aiomeasures.Event('Man down!', 'This server needs assistance.')
    handler = aiomeasures.StatsD(':0')
    assert handler.format(event) == '_e{9,29}Man down!|This server needs assistance.'

checks = [
    (aiomeasures.Check('srv', 'OK'), '_sc|srv|0'),
    (aiomeasures.Check('srv', 'warning'), '_sc|srv|1'),
    (aiomeasures.Check('srv', 'crit'), '_sc|srv|2'),
    (aiomeasures.Check('srv', 'UNKNOWN'), '_sc|srv|3'),
    (aiomeasures.Check('srv', 'OK', tags={'foo': 'bar'}, message='baz'), '_sc|srv|0|#foo:bar|m:baz'),
]

@pytest.mark.parametrize('check,expected', checks)
def test_checks(check,expected):
    handler = aiomeasures.StatsD(':0')
    assert handler.format(check) == expected


@asyncio.coroutine
def fake_server(event_loop, port=None):
    port = port or 0
    class Protocol:

        msg = []

        def connection_made(self, transport):
            self.transport = transport

        def datagram_received(self, data, addr):
            message = data.decode().strip()
            self.msg.extend(message.split())

        def connection_lost(self, *args):
            pass

    transport, protocol = yield from event_loop.create_datagram_endpoint(
        lambda: Protocol(),
        local_addr=('0.0.0.0', port)
    )
    if port == 0:
        _, port = transport.get_extra_info('sockname')
    return transport, protocol, port


@pytest.mark.asyncio
def test_client_event(event_loop):
    transport, protocol, port = yield from fake_server(event_loop)
    client = aiomeasures.StatsD('udp://127.0.0.1:%s' % port)
    asyncio.sleep(.4)
    client.event('title', 'text')
    yield from asyncio.sleep(.1)
    assert '_e{5,4}title|text' in protocol.msg
    transport.close()
    client.close()


@pytest.mark.asyncio
def test_client(event_loop):
    transport, protocol, port = yield from fake_server(event_loop)
    client = aiomeasures.StatsD('udp://127.0.0.1:%s' % port)
    asyncio.sleep(.4)
    client.incr('example.a')
    client.timing('example.b', 500)
    client.gauge('example.c', 1)
    client.set('example.d', 'bar')
    client.decr('example.e')
    client.counter('example.f', 42)
    client.histogram('example.g', 13)
    yield from asyncio.sleep(.1)
    assert 'example.a:1|c' in protocol.msg
    assert 'example.b:500|ms' in protocol.msg
    assert 'example.c:1|g' in protocol.msg
    assert 'example.d:bar|s' in protocol.msg
    assert 'example.e:-1|c' in protocol.msg
    assert 'example.f:42|c' in protocol.msg
    assert 'example.g:13|h' in protocol.msg
    transport.close()
    client.close()


@pytest.mark.asyncio
def test_reliablility(event_loop):
    transport, protocol, port = yield from fake_server(event_loop)
    client = aiomeasures.StatsD('udp://127.0.0.1:%s' % port)
    asyncio.sleep(.4)
    client.incr('example.a')
    yield from asyncio.sleep(.1)
    assert 'example.a:1|c' in protocol.msg
    transport.close()

    client.incr('example.b')
    yield from asyncio.sleep(.1)
    assert 'example.b:1|c' not in protocol.msg

    transport, protocol, port = yield from fake_server(event_loop, port)
    client.incr('example.c')
    yield from asyncio.sleep(.1)
    assert 'example.c:1|c' in protocol.msg
    transport.close()

    client.close()
