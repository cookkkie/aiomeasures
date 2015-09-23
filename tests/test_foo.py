import asyncio
import pytest


def test_sync():
    assert True

@pytest.mark.asyncio
def test_async():
    yield from asyncio.sleep(.1)
    assert True
