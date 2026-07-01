# Program 7: Dual Tasks Concurrency
# Concept: Scheduling two distinct tasks concurrently and awaiting them individually without gather.
import asyncio
from time import time, ctime

async def cook_spaghetti(customer):
    print(f"{ctime()} -> Starting cooking for Customer {customer} ...")
    await asyncio.sleep(1)  # Simulate a delay in cooking
    print(f"{ctime()} -> Finishing cooking for Customer {customer}!")

async def main():
    start_time = time()

    task_a = asyncio.create_task(cook_spaghetti("A"))
    task_b = asyncio.create_task(cook_spaghetti("B"))

    await task_a  # Wait for the first cooking task to finish
    await task_b  # Wait for the second cooking task to finish

    print(f"Total Operation time: {time() - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())