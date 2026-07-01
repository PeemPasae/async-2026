# Program 8: Task Interleaving (Context Switching)
# Concept: Watching a single thread switch back and forth between two different workflows using create_task.
import asyncio
from time import time, ctime, sleep

def greet_diner(customer):
    print(f"{ctime()} -> greeting for customer {customer} ...")
    sleep(1)  # Simulate a delay in greeting
    print(f"{ctime()} -> finish greeting customer {customer} ...")

def take_order(customer):
    print(f"{ctime()} -> Take order for customer {customer} ...")
    sleep(1)  # Simulate a delay in taking the order
    print(f"{ctime()} -> finish take order for customer {customer}!")

def cooking(customer):
    print(f"{ctime()} -> go to cooking for customer {customer} ...")
    sleep(1)  # Simulate a delay in cooking
    print(f"{ctime()} -> finish cooking for customer {customer}!")

def minibar(customer):
    print(f"{ctime()} -> go to minibar for customer {customer} ...")
    sleep(1)  # Simulate a delay in preparing the drink
    print(f"{ctime()} -> finish minibar for customer {customer}!")

if __name__ == "__main__":
    customers = ["A", "B", "C"]

    start_time = time()

    for customer in customers:
        greet_diner(customer)
        take_order(customer)
        cooking(customer)
        minibar(customer)

    duration = time() - start_time
    print(f"{ctime()} finish cooking in {duration:.2f} seconds")