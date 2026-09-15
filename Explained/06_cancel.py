"""
06 · task.cancel() และ asyncio.CancelledError
อ้างอิงงานในคลาส: Week3/task_03_cancel.py, Week3/smart_courier.py, Week8/05_task_completion_and_join.py

task.cancel()
    - "ส่งคำขอยกเลิก" ไปที่ task (คืน True ถ้าส่งได้ / False ถ้า task จบไปแล้ว)
    - ยังไม่ได้หยุดทันที: รอบถัดไปที่ task ได้รัน จะมี CancelledError โผล่ขึ้นที่บรรทัด await ที่มันค้างอยู่
    - เราต้อง await / sleep ให้ task ได้รันก่อน ถึงจะเห็นผล

ใน task ที่ถูกยกเลิก
    try:
        await ...
    except asyncio.CancelledError:
        ทำความสะอาด (ปิดไฟล์ คืนของ)
        raise              ← ควร raise ต่อ ไม่งั้น task จะถูกนับว่า "จบปกติ"

ฝั่งคนสั่งยกเลิก
    task.cancel()
    try:
        await task         ← await task ที่ถูกยกเลิกจะ raise CancelledError ใส่เรา
    except asyncio.CancelledError:
        pass
    task.cancelled()       ← True ถ้ายกเลิกสำเร็จ

หมายเหตุ: CancelledError เป็น BaseException (ไม่ใช่ Exception) → except Exception จับไม่ได้

รัน:  python 06_cancel.py
"""
import asyncio
import time

_start = time.perf_counter()


def reset_clock():
    global _start
    _start = time.perf_counter()


def log(msg):
    print(f"[{time.perf_counter() - _start:4.2f}s] {msg}")


async def delivery_good(package):
    try:
        log(f"   {package}: เริ่มส่งของ (ใช้ 5 s)")
        await asyncio.sleep(5)
        return f"{package} ส่งถึงแล้ว"
    except asyncio.CancelledError:
        log(f"   {package}: ถูกยกเลิก! คืนของเข้าคลัง")
        raise                                    # ✔ ส่งต่อ


async def delivery_bad(package):
    try:
        log(f"   {package}: เริ่มส่งของ (ใช้ 5 s)")
        await asyncio.sleep(5)
        return f"{package} ส่งถึงแล้ว"
    except asyncio.CancelledError:
        log(f"   {package}: ถูกยกเลิก! (แต่ไม่ raise ต่อ)")
        return "กลืน error ไว้"                 # ✘ task จะนับว่าจบปกติ


async def main():
    print("=== 1) ยกเลิกแบบถูกต้อง ===")
    reset_clock()
    task = asyncio.create_task(delivery_good("P001"))
    await asyncio.sleep(1)
    log(f"main: รอ 1 s แล้ว done()={task.done()} → สั่ง cancel()")
    task.cancel()
    log(f"main: หลังเรียก cancel() ทันที done()={task.done()}  ← ยังไม่หยุด แค่ส่งคำขอ")
    try:
        await task
    except asyncio.CancelledError:
        log("main: await task แล้วได้ CancelledError (จับไว้แล้ว)")
    log(f"main: cancelled()={task.cancelled()}")      # True

    print("\n=== 2) ยกเลิกแต่ในงานไม่ raise ต่อ ===")
    reset_clock()
    task = asyncio.create_task(delivery_bad("P002"))
    await asyncio.sleep(0.5)
    task.cancel()
    result = await task                              # ไม่ raise เพราะงานกลืนไว้
    log(f"main: await ได้ {result!r} · cancelled()={task.cancelled()}  ← False!")

    print("\n=== 3) ยกเลิก worker ที่วนไม่รู้จบ (แบบ Week8/05) ===")
    reset_clock()

    async def ticking():
        while True:
            await asyncio.sleep(0.4)
            log("   worker: tick")

    worker = asyncio.create_task(ticking())
    await asyncio.sleep(1.0)                         # tick ที่ 0.4, 0.8
    worker.cancel()
    try:
        await worker
    except asyncio.CancelledError:
        pass
    log(f"main: worker หยุดแล้ว cancelled()={worker.cancelled()}")


if __name__ == "__main__":
    asyncio.run(main())

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • cancel() = ขอให้หยุด · จะหยุดจริงที่ await ถัดไปของ task นั้น
# • ในงาน: except CancelledError → cleanup → raise
# • คนสั่ง: cancel() → try: await task except CancelledError: pass → cancelled() เป็น True
# • ถ้างานไม่ raise ต่อ cancelled() จะเป็น False (Week3/task_03 เป็นแบบนี้)
