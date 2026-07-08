import asyncio
from time import ctime


async def fetch_stock_price(server_name, delay):
    await asyncio.sleep(delay)
    return f"[{server_name}] Price: 150 USD"


async def main():
    tasks = {
        asyncio.create_task(fetch_stock_price("Alpha", 3.0)),
        asyncio.create_task(fetch_stock_price("Beta", 0.8)),
        asyncio.create_task(fetch_stock_price("Gamma", 1.5)),
    }

    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED
    )

    for winner in done:
        print(f"{ctime()} Winner Result: {winner.result()}")

    print(f"{ctime()} Cleaning up {len(pending)} pending tasks...")

    for task in pending:
        task.cancel()


asyncio.run(main())