"""เฉลยขั้น 05"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check


async def make_coffee(name, delay=0.2):
    await asyncio.sleep(delay)
    return f"coffee for {name}"


async def serve_together(names, delay=0.2):
    # แบบ 1: สร้าง task ครบก่อน แล้ววน await
    tasks = [asyncio.create_task(make_coffee(n, delay)) for n in names]
    results = []
    for t in tasks:
        results.append(await t)
    return results

    # แบบ 2 (สั้นกว่า):
    # return list(await asyncio.gather(*(make_coffee(n, delay) for n in names)))


if __name__ == "__main__":
    check(5, globals())
