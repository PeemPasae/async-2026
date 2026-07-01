# Program 6: Creating a Concurrent Task
# Concept: Wrapping a coroutine inside asyncio.create_task() to schedule it to run in the background.
import asyncio
from time import time, ctime

async def cook_spaghetti(customer):
    print(f"{ctime()} -> Starting cooking for Customer {customer} ...")
    await asyncio.sleep(1)  # Simulate a delay in cooking
    print(f"{ctime()} -> Finishing cooking for Customer {customer}!")

async def main():
    start_time = time()

    task_a = asyncio.create_task(cook_spaghetti("A"))

    print(f"{ctime()} -> Main Program can do other thing ...")

    await task_a  # Wait for the cooking task to finish

    print(f"Total Operation time: {time() - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())