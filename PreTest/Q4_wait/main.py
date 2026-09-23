import asyncio


async def fetch_db_record(table_name: str, latency: float):
    """
    Coroutine ดึงข้อมูลจากฐานข้อมูลสมมติ:
    1. await asyncio.sleep(latency)
    2. return f"RowData_{table_name}"
    """
    await asyncio.sleep(latency)
    return f"RowData_{table_name}"


async def main_fetch_wait():
    tasks = [
        asyncio.create_task(fetch_db_record("users", 1.0)),
        asyncio.create_task(fetch_db_record("orders", 1.5)),
        asyncio.create_task(fetch_db_record("products", 0.5)),
    ]

    done, pending = await asyncio.wait(tasks)

    return {task.result() for task in done}


if __name__ == "__main__":
    print(asyncio.run(main_fetch_wait()))
