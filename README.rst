AIO Measures
============

This library allows you to send metrics to your StatsD server.
This works on Python >= 3.3 and relies or asyncio.


Installation::

    python -m pip install aiomeasures


Usage::

    from aiomeasures import StatsD

    client = StatsD('udp://127.0.0.1:6789')
    client.incr('foo')
    client.decr('bar', tags={'one': 'two'})
    with client.timer('baz'):
        # long process
        pass


The client will send metrics to server as possible.
