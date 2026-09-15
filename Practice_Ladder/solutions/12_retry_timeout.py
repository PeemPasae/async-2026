"""เฉลยขั้น 12"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check


async def fetch_with_retry(fetch, attempts, timeout):
    for attempt in range(1, attempts + 1):
        try:
            result = await asyncio.wait_for(fetch(), timeout=timeout)   # fetch() ใหม่ทุกรอบ
            return result, attempt
        except asyncio.TimeoutError:
            continue
    return None, attempts


if __name__ == "__main__":
    check(12, globals())
