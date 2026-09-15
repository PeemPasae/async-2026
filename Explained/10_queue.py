"""
10 · asyncio.Queue
อ้างอิงงานในคลาส: Week8/02 – 08

q = asyncio.Queue(maxsize=0)
    maxsize=0 (ค่าเริ่มต้น) = ไม่จำกัดขนาด · maxsize=N = จุได้ N ชิ้น (bounded queue)
    FIFO: ใส่ก่อน ได้ออกก่อน

┌──────────────────────┬───────────────────────────────────────────────────────────┐
│ await q.put(item)    │ ใส่ของ · ถ้าคิวเต็ม → รอจนมีที่ว่าง (backpressure)              │
│ await q.get()        │ เอาของออก · ถ้าคิวว่าง → รอจนมีของ (ไม่บล็อก loop)               │
│ q.put_nowait(item)   │ ใส่ทันที ไม่รอ · คิวเต็ม → raise QueueFull                       │
│ q.get_nowait()       │ เอาออกทันที ไม่รอ · คิวว่าง → raise QueueEmpty                   │
│ q.qsize()            │ จำนวนของในคิวตอนนี้                                            │
│ q.empty() / q.full() │ ว่างไหม / เต็มไหม                                              │
│ q.task_done()        │ แจ้งว่า "ของ 1 ชิ้นที่ get ไปทำเสร็จแล้ว"                          │
│ await q.join()       │ รอจนทุกชิ้นที่เคย put ถูก task_done() ครบ                         │
└──────────────────────┴───────────────────────────────────────────────────────────┘

กลไก join/task_done: คิวมีตัวนับ "งานค้าง"
    put() → ตัวนับ +1     task_done() → ตัวนับ -1     join() รอจนตัวนับ = 0
    ถ้าลืม task_done แม้แต่ครั้งเดียว join() จะค้างตลอดไป

sentinel: ใส่ค่าพิเศษ (มักใช้ None) เพื่อบอก consumer ว่า "หมดงานแล้ว ออกจากลูปได้"
    consumer N ตัว → ต้องใส่ None N ครั้ง

รัน:  python 10_queue.py
"""
import asyncio
import time

_start = time.perf_counter()


def reset_clock():
    global _start
    _start = time.perf_counter()


def log(msg):
    print(f"[{time.perf_counter() - _start:4.2f}s] {msg}")


async def main():
    print("=== 1) put / get เรียงแบบ FIFO ===")
    q = asyncio.Queue()
    for item in ["Order#1", "Order#2", "Order#3"]:
        await q.put(item)
    print("   qsize() =", q.qsize())                          # 3
    print("   get ->", await q.get(), "|", await q.get(), "|", await q.get())
    print("   empty() =", q.empty())                          # True

    print("\n=== 2) get() ตอนคิวว่าง จะรอโดยไม่ทำให้โปรแกรมค้าง ===")
    reset_clock()
    q = asyncio.Queue()

    async def eager_consumer():
        log("   consumer: ขอ get() ทั้งที่คิวว่าง...")
        data = await q.get()
        log(f"   consumer: ได้ {data!r}")

    async def slow_producer():
        await asyncio.sleep(1)
        log("   producer: put('Data-Alpha')")
        await q.put("Data-Alpha")

    await asyncio.gather(eager_consumer(), slow_producer())

    print("\n=== 3) Queue(maxsize=2): put() รอเมื่อคิวเต็ม (backpressure) ===")
    reset_clock()
    q = asyncio.Queue(maxsize=2)

    async def fast_producer():
        for i in range(1, 5):
            log(f"   producer: จะใส่ #{i} (ในคิวมี {q.qsize()})")
            await q.put(f"#{i}")
            log(f"   producer: ใส่ #{i} สำเร็จ")

    async def slow_consumer():
        await asyncio.sleep(1)
        for _ in range(4):
            item = await q.get()
            log(f"      consumer: ดึง {item}")
            await asyncio.sleep(0.5)

    await asyncio.gather(fast_producer(), slow_consumer())
    # สังเกต: #1 #2 ใส่ทันที · #3 ต้องรอถึง 1.00 s ตอน consumer ดึงออก

    print("\n=== 4) worker หลายตัว + task_done + join + sentinel ===")
    reset_clock()
    q = asyncio.Queue()

    async def worker(name):
        count = 0
        while True:
            job = await q.get()
            if job is None:               # เจอ sentinel → เลิกงาน
                q.task_done()             # sentinel ก็นับเป็นของ 1 ชิ้น ต้อง task_done ด้วย
                break
            log(f"   {name}: ทำ {job}")
            await asyncio.sleep(0.5)
            count += 1
            q.task_done()                 # แจ้งว่าชิ้นนี้เสร็จ
        log(f"   {name}: เลิกงาน ทำไป {count} ชิ้น")
        return count

    for i in range(1, 6):
        await q.put(f"Job#{i}")

    workers = [asyncio.create_task(worker(f"W{i}")) for i in (1, 2)]
    await q.join()                        # 1) รอจนงานจริงถูก task_done ครบ 5 ชิ้น
    log("main: q.join() ผ่านแล้ว งานหมด")
    for _ in workers:
        await q.put(None)                 # 2) sentinel เท่าจำนวน worker
    counts = await asyncio.gather(*workers)   # 3) รอ worker ออกจากลูปครบ
    log(f"main: worker ทำไป {counts} ชิ้น รวม {sum(counts)}")


if __name__ == "__main__":
    asyncio.run(main())

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • put/get ต้อง await · คิวเต็ม put รอ · คิวว่าง get รอ
# • get 1 ครั้ง = task_done 1 ครั้ง (รวมตอนได้ sentinel)
# • ลำดับปิดระบบ: ผลิตครบ → await q.join() → ใส่ None เท่าจำนวน worker → gather(workers)
# • อีกทางปิด worker: หลัง join() ให้ cancel() worker ทุกตัว (Week8/05)
