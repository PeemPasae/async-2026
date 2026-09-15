"""เฉลยขั้น 09"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check


async def divide(a, b):
    await asyncio.sleep(0.1)
    return a / b


async def divide_all(pairs):
    results = await asyncio.gather(*(divide(a, b) for a, b in pairs),
                                   return_exceptions=True)
    return [f"error: {type(r).__name__}" if isinstance(r, Exception) else r
            for r in results]


if __name__ == "__main__":
    check(9, globals())
