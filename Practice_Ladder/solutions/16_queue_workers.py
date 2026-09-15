"""เฉลยขั้น 16"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check


async def process_jobs(jobs, n_workers, job_time):
    q = asyncio.Queue()
    done = []
    per_worker = {}

    async def worker(name):
        per_worker[name] = 0
        while True:
            job = await q.get()
            if job is None:
                q.task_done()
                break
            await asyncio.sleep(job_time)
            done.append(job)
            per_worker[name] += 1
            q.task_done()

    for job in jobs:
        await q.put(job)

    workers = [asyncio.create_task(worker(f"W{i}")) for i in range(1, n_workers + 1)]
    await q.join()                     # รองานจริงหมด
    for _ in workers:
        await q.put(None)              # sentinel เท่าจำนวน worker
    await asyncio.gather(*workers)
    return {"done": done, "per_worker": per_worker}


if __name__ == "__main__":
    check(16, globals())
