"""เฉลยขั้น 10"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check

SHOP_TIME = {"chicken": 0.1, "noodle": 0.3, "steak": 0.8}


async def cook(shop):
    await asyncio.sleep(SHOP_TIME[shop])
    return f"{shop} ready"


async def order_with_timeout(shop, timeout):
    try:
        return await asyncio.wait_for(cook(shop), timeout=timeout)
    except asyncio.TimeoutError:
        return f"{shop}: timeout"


async def order_many(shops, timeout):
    return list(await asyncio.gather(*(order_with_timeout(s, timeout) for s in shops)))


if __name__ == "__main__":
    check(10, globals())
