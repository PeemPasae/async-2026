# Program 9: Dynamically Tracking Tasks in a List
# Concept: Managing multiple generated tasks dynamically by appending them into a standard Python list.
import asyncio
from time import time, ctime

async def serve_customer(name):
    print(f"{ctime()} -> Handing customer {name} ...")
    await asyncio.sleep(1)  # Simulate a delay in serving the customer
    print(f"{ctime()} -> Done customer {name}!")

async def main():
    start_time = time()
    customer = ["A", "B", "C", "D"]
    task_list = []

    for name in customer:
        t = asyncio.create_task(serve_customer(name))
        task_list.append(t)

    for t in task_list:
        await t

    print(f"Total Operation time: {time() - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())