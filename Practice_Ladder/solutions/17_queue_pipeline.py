"""เฉลยขั้น 17"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check


async def food_pipeline(orders, cooks=2, riders=1, cook_time=0.1, ride_time=0.05):
    kitchen_q = asyncio.Queue()
    delivery_q = asyncio.Queue()
    delivered = []

    async def cook_worker():
        while True:
            order = await kitchen_q.get()
            if order is None:
                kitchen_q.task_done()
                break
            await asyncio.sleep(cook_time)
            await delivery_q.put(order)
            kitchen_q.task_done()

    async def rider_worker():
        while True:
            order = await delivery_q.get()
            if order is None:
                delivery_q.task_done()
                break
            await asyncio.sleep(ride_time)
            delivered.append(f"{order} delivered")
            delivery_q.task_done()

    cook_tasks = [asyncio.create_task(cook_worker()) for _ in range(cooks)]
    rider_tasks = [asyncio.create_task(rider_worker()) for _ in range(riders)]

    for order in orders:
        await kitchen_q.put(order)

    await kitchen_q.join()
    for _ in cook_tasks:
        await kitchen_q.put(None)

    await delivery_q.join()
    for _ in rider_tasks:
        await delivery_q.put(None)

    await asyncio.gather(*cook_tasks, *rider_tasks)
    return delivered


if __name__ == "__main__":
    check(17, globals())
