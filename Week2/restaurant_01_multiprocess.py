from time import  sleep, ctime, time
import multiprocessing

def greet_diners(customer):
    print(f"{ctime()} -> Greeting for Customer {customer}...")
    sleep(1)  # Simulate a delay in greeting
    print(f"{ctime()} -> Greeting for Customer {customer} ...Done!")
    
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
    print(f"{ctime()} ->[ Thread-{customer}] Customer {customer} workflow completed!")
    
if __name__ == "__main__":
    customers = ["A", "B", "C"]
    start_time = time()
    
    for customer in customers:
        greet_diners(customer)
    print(f"{ctime()} -> All customers greeted, now starting their private workflows...")
    
    processes = []
    for customer in customers:
        p = multiprocessing.Process(target=customer_private_workflow, args=(customer,))
        processes.append(p)
        p.start()
        
    for p in processes:
        p.join()  # Wait for all threads to complete
        
    duration = time() - start_time
    print(f"{ctime()} finished Cooking in {duration:.2f} seconds")  # Will be around 4 seconds