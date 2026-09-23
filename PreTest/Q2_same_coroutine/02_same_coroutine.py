import asyncio


async def print_message(message, delay):
    await asyncio.sleep(delay)
    print(message)


async def main_task():
    task1 = asyncio.create_task(print_message("A", 1.0))
    task2 = asyncio.create_task(print_message("B", 2.0))

    await task1
    await task2


asyncio.run(main_task())
