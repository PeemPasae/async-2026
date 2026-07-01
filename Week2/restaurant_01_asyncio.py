import asyncio
from time import time, ctime, sleep
import threading

def greet_diner(customer):
    print(f"{ctime()} -> greeting for customer {customer} ...")
    sleep(1)  # Simulate a delay in greeting
    print(f"{ctime()} -> greeting for customer {customer} ...Done! ")

def customer_private_workflow(customer):
    print(f"{ctime()} ->[Thread-{customer}] Taking Order...")
    sleep(1)  # Simulate a delay in private work
    print(f"{ctime()} ->[Thread-{customer}] Taking Order ...Done!")
    
    print(f"{ctime()} ->[Thread-{customer}] Cooking...")
    sleep(1)  # Simulate a delay in cooking
    print(f"{ctime()} ->[Thread-{customer}] Cooking ...Done!")
    
    print(f"{ctime()} ->[Thread-{customer}] Mini Bar...")
    sleep(1)  # Simulate a delay in preparing mini bar
    print(f"{ctime()} ->[Thread-{customer}] Mini Bar ...Done!")
    print(f"{ctime()} ->[Thread-{customer}] Customer {customer} workflow completed!")
    

if __name__ == "__main__":
    customers = ["A", "B", "C"]

    start_time = time()

    for customer in customers:
        greet_diner(customer)
    print(f"{ctime()} -> All customers greeted, now starting their private workflows...")
    
    customer_threads = []
    for customer in customers:
        thread = threading.Thread(target=customer_private_workflow, args=(customer,))
        customer_threads.append(thread)
        thread.start()
        
    for thread in customer_threads:
        thread.join()  # Wait for all threads to complete
        
    duration = time() - start_time
    print(f"{ctime()} finished Cooking in {duration:.2f} seconds")  # Will be around 4 seconds