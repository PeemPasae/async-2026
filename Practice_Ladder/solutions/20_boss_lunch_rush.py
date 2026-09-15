"""เฉลยขั้น 20"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check

COOK_TIME = {"chicken": 0.1, "noodle": 0.2, "steak": 0.5}


class FoodCourt:
    def __init__(self, stock):
        self.stock = dict(stock)
        self.lock = asyncio.Lock()

    async def reserve(self, menu):
        async with self.lock:
            if self.stock.get(menu, 0) <= 0:
                return False
            await asyncio.sleep(0.01)
            self.stock[menu] -= 1
            return True

    async def release(self, menu):
        async with self.lock:
            self.stock[menu] = self.stock.get(menu, 0) + 1

    async def cook(self, menu, timeout):
        try:
            await asyncio.wait_for(asyncio.sleep(COOK_TIME[menu]), timeout=timeout)
            return "READY"
        except asyncio.TimeoutError:
            return "TIMEOUT"

    async def order(self, student, menu, timeout):
        if not await self.reserve(menu):
            return "SOLD_OUT"
        status = await self.cook(menu, timeout)   # ทำอาหาร "นอก" lock เพื่อให้หลายจานทำพร้อมกันได้
        if status == "TIMEOUT":
            await self.release(menu)
        return status


async def lunch_rush(court, orders, n_cooks, timeout):
    q = asyncio.Queue()
    results = {}

    async def cook_worker():
        while True:
            item = await q.get()
            if item is None:
                q.task_done()
                break
            try:
                student, menu = item
                results[item] = await court.order(student, menu, timeout)
            finally:
                q.task_done()

    workers = [asyncio.create_task(cook_worker()) for _ in range(n_cooks)]
    for item in orders:
        await q.put(item)
    await q.join()
    for _ in workers:
        await q.put(None)
    await asyncio.gather(*workers)
    return results


if __name__ == "__main__":
    check(20, globals())
