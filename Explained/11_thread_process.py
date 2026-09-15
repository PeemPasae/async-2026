"""
11 · threading.Thread · multiprocessing.Process · งาน blocking ในโค้ด async
อ้างอิงงานในคลาส: Week1/up02_thread.py, up03_multiprocess.py, ps03_multiprocess.py,
                 Week2/restaurant_01_thread.py, Week10/server.py (run_in_executor)

threading.Thread(target=ฟังก์ชัน, args=(ค่า,), name=None)
    target : ชื่อฟังก์ชัน ไม่ใส่วงเล็บ
    args   : tuple ของอาร์กิวเมนต์ ← ตัวเดียวต้องมีคอมมา (x,)  ถ้าเขียน (x) คือค่าเฉย ๆ ไม่ใช่ tuple
    .start() เริ่มรัน  ·  .join() รอจนจบ
    ทุก thread อยู่ใน process เดียวกัน → PID เดียว แต่ thread id ต่างกัน · แชร์ตัวแปรกันได้

multiprocessing.Process(target=..., args=(...,))
    ใช้ .start() / .join() เหมือนกัน
    แต่ละ process มี PID และหน่วยความจำของตัวเอง → แก้ตัวแปรใน process ลูก main ไม่เห็น
    ส่งค่ากลับต้องใช้ multiprocessing.Queue()
    ต้องอยู่ใต้  if __name__ == "__main__":  เสมอ (Windows จะ import ไฟล์นี้ซ้ำใน process ลูก)

งาน blocking ที่เลี่ยงไม่ได้ในโค้ด async (เช่น input(), ไลบรารีที่ไม่มีแบบ async)
    await asyncio.to_thread(ฟังก์ชัน, arg1, ...)                 (Python 3.9+)
    await loop.run_in_executor(None, ฟังก์ชัน, arg1, ...)        (แบบที่ Week10/server.py ใช้)
    → โยนไปรันใน thread แยก event loop จึงไม่ค้าง

รัน:  python 11_thread_process.py
"""
import asyncio
import multiprocessing
import os
import threading
import time


def make_coffee(customer):
    tid = threading.get_native_id()
    print(f"   [{customer}] PID={os.getpid()} TID={tid} เริ่มชง")
    time.sleep(1)                                   # ใน thread/process ใช้ time.sleep ได้
    print(f"   [{customer}] เสร็จ")


def make_coffee_and_report(customer, result_queue):
    time.sleep(1)
    result_queue.put((customer, os.getpid()))       # ส่งค่ากลับให้ main ผ่านคิว


def demo_thread():
    print("=== 1) threading.Thread: PID เดียวกัน, TID ต่างกัน, ≈1 s ===")
    print(f"   main PID={os.getpid()}")
    start = time.perf_counter()
    threads = []
    for c in ["A", "B", "C"]:
        t = threading.Thread(target=make_coffee, args=(c,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print(f"   รวม {time.perf_counter() - start:.2f} s")


def demo_process():
    print("\n=== 2) multiprocessing.Process: PID ต่างกัน, ส่งค่ากลับผ่าน Queue ===")
    start = time.perf_counter()
    result_queue = multiprocessing.Queue()
    processes = []
    for c in ["A", "B", "C"]:
        p = multiprocessing.Process(target=make_coffee_and_report, args=(c, result_queue))
        processes.append(p)
        p.start()
    results = [result_queue.get() for _ in processes]   # รับค่ากลับให้ครบก่อน join
    for p in processes:
        p.join()
    print(f"   ได้จาก process ลูก: {sorted(results)}")
    print(f"   รวม {time.perf_counter() - start:.2f} s (มีค่าเปิด process เพิ่ม)")


def blocking_io():
    time.sleep(1)            # แทน input() หรือไลบรารีที่บล็อก
    return "ข้อมูลจากงาน blocking"


async def demo_to_thread():
    print("\n=== 3) งาน blocking ในโค้ด async → โยนไป thread ด้วย to_thread ===")
    start = time.perf_counter()

    async def ticker():
        for _ in range(4):
            await asyncio.sleep(0.25)
            print(f"   tick {time.perf_counter() - start:.2f} s  ← loop ยังทำงานได้ระหว่างรอ")

    result, _ = await asyncio.gather(asyncio.to_thread(blocking_io), ticker())
    print(f"   ได้ {result!r} ที่ {time.perf_counter() - start:.2f} s")

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, blocking_io)   # แบบเดียวกัน เขียนอีกทาง
    print(f"   run_in_executor ได้ {result!r}")


if __name__ == "__main__":
    demo_thread()
    demo_process()
    asyncio.run(demo_to_thread())

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • Thread: target=ชื่อฟังก์ชัน, args=(x,) → start() → join()
# • Process: เหมือน Thread แต่ PID แยก หน่วยความจำแยก ต้องมี if __name__ == "__main__"
# • I/O-bound → asyncio หรือ thread · CPU-bound → process
# • ต้องเรียกของที่บล็อกในโค้ด async → asyncio.to_thread / run_in_executor
