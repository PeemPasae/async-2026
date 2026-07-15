# foodcourt_02_gather.py
import asyncio
from time import time, ctime
from food_utils import send_order_to_kitchen


async def main():
    MY_STUDENT_ID = "6710301005"

    print(f"{ctime()} | --- [Task 2] Practice using gather to wait for all group orders ---")
    start_time = time()

    # 1. Spawn 3 concurrent tasks to order food from different shops.
    t1 = asyncio.create_task(
        send_order_to_kitchen(
            MY_STUDENT_ID, "hainanese_chicken", "Chicken Rice"
        )
    )
    t2 = asyncio.create_task(
        send_order_to_kitchen(
            MY_STUDENT_ID, "noodle", "Wonton Noodles"
        )
    )
    t3 = asyncio.create_task(
        send_order_to_kitchen(
            MY_STUDENT_ID, "steak", "Sizzling Steak"
        )
    )

    # 2. Use asyncio.gather to wait for all dishes to be prepared concurrently.
    results = await asyncio.gather(t1, t2, t3)

    for dish in results:
        print(
            f"{ctime()} | [Pickup] Shop: {dish['shop']} | "
            f"Menu: {dish['menu']} is ready!"
        )

    print(
        f"{ctime()} | Total time: {time() - start_time:.2f} "
        "seconds (Equals to the slowest dish)."
    )


if __name__ == "__main__":
    asyncio.run(main())