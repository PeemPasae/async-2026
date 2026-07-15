# foodcourt_04_wait_for.py

import asyncio
from time import ctime
from food_utils import send_order_to_kitchen


async def main():
    MY_STUDENT_ID = "6710301005"

    print(
        f"{ctime()} | --- [Task 4] Practice using wait_for to handle timeouts ---"
    )

    try:
        # 1. Order a steak (takes 4s) but enforce a strict timeout of 2.0 seconds.
        print(
            f"{ctime()} | [System] Order sent. "
            f"Monitoring 2.0s timeout limit..."
        )

        result = await asyncio.wait_for(
            send_order_to_kitchen(
                MY_STUDENT_ID,
                "steak",
                "T-Bone Steak"
            ),
            timeout=2.0
        )

        print(f"{ctime()} | Success: {result}")

    except asyncio.TimeoutError:
        # 2. Catch the TimeoutError exception when the execution exceeds the limit.
        print(
            f"{ctime()} | Timeout occurred: "
            f"Steak took too long! Leaving the food court now."
        )


if __name__ == "__main__":
    asyncio.run(main())