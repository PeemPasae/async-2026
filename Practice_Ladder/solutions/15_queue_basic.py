"""เฉลยขั้น 15"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check


async def producer(q, items):
    for item in items:
        await q.put(item)
        await asyncio.sleep(0.01)
    await q.put(None)


async def consumer(q):
    got = []
    while True:
        item = await q.get()
        if item is None:
            break
        got.append(item)
    return got


async def pipeline(items):
    q = asyncio.Queue()
    _, got = await asyncio.gather(producer(q, items), consumer(q))
    return got


if __name__ == "__main__":
    check(15, globals())
