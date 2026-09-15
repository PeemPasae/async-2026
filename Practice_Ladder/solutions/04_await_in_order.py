"""เฉลยขั้น 04"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check


async def make_coffee(name, delay=0.2):
    await asyncio.sleep(delay)
    return f"coffee for {name}"


async def serve_in_order(names, delay=0.2):
    results = []
    for name in names:
        results.append(await make_coffee(name, delay))   # รอคนนี้เสร็จก่อน ค่อยไปคนถัดไป
    return results


if __name__ == "__main__":
    check(4, globals())
