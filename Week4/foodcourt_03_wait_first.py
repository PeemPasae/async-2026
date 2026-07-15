# foodcourt_03_wait_first.py

import asyncio
from time import time, ctime
from food_utils import send_order_to_kitchen


async def main():
    MY_STUDENT_ID = "6710301005"

    print(f"{ctime()} | --- [Task 3] Practice using wait (FIRST_COMPLETED) ---")
    start_time = time()

    # 1. Send 3 orders to compete against each other.
    orders = {
        asyncio.create_task(
            send_order_to_kitchen(
                MY_STUDENT_ID,
                "steak",
                "Beef Steak"
            )
        ),
        asyncio.create_task(
            send_order_to_kitchen(
                MY_STUDENT_ID,
                "noodle",
                "Clear Soup Noodles"
            )
        ),
        asyncio.create_task(
            send_order_to_kitchen(
                MY_STUDENT_ID,
                "hainanese_chicken",
                "Chicken Rice Thigh"
            )
        )
    }

    # 2. Use asyncio.wait with FIRST_COMPLETED
    done, pending = await asyncio.wait(
        orders,
        return_when=asyncio.FIRST_COMPLETED
    )

    # 3. Get the result of the fastest dish that completed first.
    fastest_dish = list(done)[0].result()

    print(
        f"{ctime()} | Winner served dish: "
        f"Shop: {fastest_dish['shop']} | "
        f"Menu: {fastest_dish['menu']}"
    )

    # 4. Cancel the remaining pending tasks to save network resources.
    print(
        f"{ctime()} | Cleaning up: "
        f"Canceling {len(pending)} remaining pending orders..."
    )

    for t in pending:
        t.cancel()

    print(
        f"{ctime()} | Total waiting time for the first dish: "
        f"{time() - start_time:.2f} seconds."
    )


if __name__ == "__main__":
    asyncio.run(main())