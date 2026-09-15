"""เฉลยขั้น 06"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check


async def cook(name, seconds, finish_order):
    await asyncio.sleep(seconds)
    finish_order.append(name)
    return name


async def cook_all(menu):
    finish_order = []
    results = await asyncio.gather(*(cook(n, s, finish_order) for n, s in menu.items()))
    return list(results), finish_order


if __name__ == "__main__":
    check(6, globals())
