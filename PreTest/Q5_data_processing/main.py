import asyncio


async def fetch_task_a():
    await asyncio.sleep(1.0)
    return [42, 12, 88]


async def fetch_task_b():
    await asyncio.sleep(1.5)
    return [5, 67, 23]


async def process_and_sort():
    result_a, result_b = await asyncio.gather(fetch_task_a(), fetch_task_b())

    combined = result_a + result_b

    return sorted(combined)


if __name__ == "__main__":
    print(asyncio.run(process_and_sort()))
