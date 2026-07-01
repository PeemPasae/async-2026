from time import ctime, time
import asyncio

# --- Derived from restaurant_01_thread.py / restaurant_01_multiprocess.py ---
# Same 2-phase pattern:
#   Phase 1: Greeting -> sequential (only ONE front-desk worker)
#   Phase 2: Private workflow -> concurrent (start all tasks first, await later)
# Threading used threading.Thread + start()/join()
# Multiprocessing used multiprocessing.Process + start()/join()
# Asyncio replaces both with create_task() + await asyncio.gather()


async def greet_diners(customer):
    print(f"{ctime()} Greeting for Customer-{customer} ...")
    await asyncio.sleep(1)  # non-blocking delay (was: sleep(1))
    print(f"{ctime()} Greeting for Customer-{customer} ...Done!")


async def customer_private_workflow(customer):
    print(f"{ctime()}   [Task-{customer}] Taking Order ...")
    await asyncio.sleep(1)  # Simulate a delay in taking order
    print(f"{ctime()}   [Task-{customer}] Taking Order ...Done!")

    print(f"{ctime()}   [Task-{customer}] Cooking Spaghetti ...")
    await asyncio.sleep(1)  # Simulate a delay in cooking
    print(f"{ctime()}   [Task-{customer}] Cooking Spaghetti ...Done!")

    print(f"{ctime()}   [Task-{customer}] Manage Bar for Drink ...")
    await asyncio.sleep(1)  # Simulate a delay in preparing the drink
    print(f"{ctime()}   [Task-{customer}] Manage Bar for Drink ...Done!")
    print(f"{ctime()}   [Task-{customer}] All served!\n")


async def main():
    customers = ["A", "B", "C"]
    start_time = time()

    # --- Phase 1: Sequential greeting (same as thread/multiprocess version) ---
    for customer in customers:
        await greet_diners(customer)

    print(f"\n{ctime()} --- All customers greeted. Scheduling independent Async Tasks! ---\n")

    # --- Phase 2: Concurrent workflow ---
    # create_task() FIRST for every customer (like thread.start() / process.start())
    tasks = [asyncio.create_task(customer_private_workflow(c)) for c in customers]

    # then await ALL of them together (like thread.join() / process.join())
    await asyncio.gather(*tasks)

    duration = time() - start_time
    print(f"{ctime()} Finished Entire Restaurant Operation in {duration:.2f} seconds.")


if __name__ == "__main__":
    asyncio.run(main())