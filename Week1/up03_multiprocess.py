from time import sleep, ctime, time
import multiprocessing

def update_cup_number(customer_name):
    print(f"{ctime()} | LCD: Processing for customer {customer_name}...")
    sleep(1.0)
    print(f"{ctime()} | LCD: Done for customer {customer_name}.")
    pass

def make_coffee(customer_name):
    print(f"{ctime()} | Making coffee for {customer_name}...")
    sleep(1.0)
    print(f"{ctime()} | Coffee ready for {customer_name}!")
    update_cup_number(customer_name)
    pass

def main():
    queue = ['A', 'B', 'C']

    print(f"{ctime()} | === Multi-processing Coffee Machine ===")
    start_time = time()

    processes = []
    for customer in queue:
        p = multiprocessing.Process(target=make_coffee, args=(customer,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    duration = time() - start_time
    print(f"{ctime()} | Total time: {duration:.2f} seconds")
    pass

if __name__ == "__main__":
    main()