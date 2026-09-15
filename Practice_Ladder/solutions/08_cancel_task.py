"""เฉลยขั้น 08"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check

cleanup_log = []


async def download(filename):
    try:
        await asyncio.sleep(0.3)
        return f"{filename} saved"
    except asyncio.CancelledError:
        cleanup_log.append(filename)
        raise                               # ส่งต่อ ให้ task ถูกนับว่า cancelled


async def start_and_cancel(filename, after):
    task = asyncio.create_task(download(filename))
    await asyncio.sleep(after)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    return task.cancelled()


if __name__ == "__main__":
    check(8, globals())
