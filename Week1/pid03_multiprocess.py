from time import sleep, ctime, time
import multiprocessing
import os
import threading

# ฟังก์ชันจำลองการทำกาแฟให้ลูกค้า 1 คนแบบซิงโครนัส
def make_coffee(customer_name):
    pid = os.getpid()
    thread_id = threading.current_thread().native_id
    thread_name = threading.current_thread().name

    print(f"{ctime()} | [PID: {pid}] [TID: {thread_id}] [Thread Name: {thread_name}] กำลังชงกาแฟให้ลูกค้า {customer_name}...")
    sleep(5)
    print(f"{ctime()} | [PID: {pid}] [TID: {thread_id}] [Thread Name: {thread_name}] ลูกค้า {customer_name}: ได้รับกาแฟแล้ว!")

def main():
    queue = ['A', 'B', 'C']
    main_pid = os.getpid()
    main_tid = threading.current_thread().native_id

    print(f"{ctime()} | [Main PID: {main_pid}] [Main TID: {main_tid}] เริ่มต้นการทำงานของร้านกาแฟ...")
    start_time = time()

    processes = []
    for customer in queue:
        p = multiprocessing.Process(target=make_coffee, args=(customer,))
        processes.append(p)
        p.start()

    # Wait for all processes to complete
    for p in processes:
        p.join()

    duration = time() - start_time
    print(f"{ctime()} | [Main PID: {main_pid}] [Main TID: {main_tid}] ร้านกาแฟปิดทำการแล้ว! ใช้เวลาในการทำงานทั้งหมด: {duration:.2f} วินาที") 

if __name__ == "__main__":
    main()        