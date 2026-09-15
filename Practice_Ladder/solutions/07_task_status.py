"""เฉลยขั้น 07"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check


async def slow_job():
    await asyncio.sleep(0.1)
    return "OK"


async def task_report():
    task = asyncio.create_task(slow_job(), name="Report-Job")
    done_before = task.done()          # ยังไม่ได้รันเลย → False
    result = await task
    return {
        "name": task.get_name(),
        "done_before": done_before,
        "result": result,
        "done_after": task.done(),
    }


if __name__ == "__main__":
    check(7, globals())
