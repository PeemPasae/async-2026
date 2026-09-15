"""เฉลยขั้น 11"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check

ping_cancelled = []


async def ping(name, delay):
    try:
        await asyncio.sleep(delay)
        return name
    except asyncio.CancelledError:
        ping_cancelled.append(name)
        raise


async def fastest_server(servers):
    tasks = {asyncio.create_task(ping(n, d)) for n, d in servers.items()}
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    winner = done.pop().result()
    for t in pending:
        t.cancel()
    return winner, len(pending)


if __name__ == "__main__":
    check(11, globals())
