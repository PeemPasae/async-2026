from time import time, ctime, sleep
import threading

def greet_dinner(customer):
    print(f"{ctime()} -> greeting for customer {customer} ...")
    sleep(1)  # Simulate a delay in greeting
    print(f"{ctime()} -> finish greeting customer {customer} ...")

def customer_private_workflow(customer):
    print(f"{ctime()}  [Thread-{customer}] Taking order")
    sleep(1)  # Simulate a delay in taking the order
    print(f"{ctime()}  [Thread-{customer}] Finish taking order")

    print(f"{ctime()}  [Thread-{customer}] Cooking")
    sleep(1)  # Simulate a delay in cooking
    print(f"{ctime()}  [Thread-{customer}] Finish cooking")

    print(f"{ctime()}  [Thread-{customer}] Minibar")
    sleep(1)  # Simulate a delay in preparing the drink
    print(f"{ctime()}  [Thread-{customer}] Finish minibar")
    print(f"{ctime()}  [Thread-{customer}] Finish workflow")

if __name__ == "__main__":
    customers = ["A", "B", "C"]
    start_time = time()

    for customer in customers:
        greet_dinner(customer)
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