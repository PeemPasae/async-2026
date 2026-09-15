"""เฉลยขั้น 03"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check


async def add_later(a, b, delay):
    await asyncio.sleep(delay)
    return a + b


if __name__ == "__main__":
    check(3, globals())
