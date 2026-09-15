"""
02 · await · asyncio.sleep เทียบกับ time.sleep
อ้างอิงงานในคลาส: Week2/asyncio04.py, asyncio05.py, Week8/01_synchronous_vs_asynchronous.py

await x
    - ใช้ได้เฉพาะข้างใน async def
    - แปลว่า "หยุดฟังก์ชันนี้ไว้ตรงนี้จนกว่า x จะเสร็จ แล้วค่อยทำบรรทัดถัดไป"
    - ระหว่างที่หยุด event loop เอาเวลาไปรันงานอื่นได้ ← นี่คือหัวใจของ asyncio

await asyncio.sleep(วินาที)
    - รอแบบ "ไม่บล็อก": คืนการควบคุมให้ event loop ระหว่างรอ
    - คืนค่า None

time.sleep(วินาที)
    - รอแบบ "บล็อก": ทั้ง thread หยุดนิ่ง event loop ก็หยุดไปด้วย งานอื่นทำอะไรไม่ได้
    - ห้ามใช้ใน async def

ไฟล์นี้ใช้ asyncio.gather ช่วยรันสองงานพร้อมกัน (อธิบายละเอียดในไฟล์ 04)

รัน:  python 02_await_and_sleep.py
"""
import asyncio
import time

_start = time.perf_counter()


def reset_clock():
    global _start
    _start = time.perf_counter()


def log(msg):
    print(f"[{time.perf_counter() - _start:4.2f}s] {msg}")


async def polite_worker(name):
    log(f"{name} เริ่ม  (await asyncio.sleep)")
    await asyncio.sleep(1)        # "ฉันรอ 1 วิ ระหว่างนี้ loop ไปทำงานอื่นก่อนได้"
    log(f"{name} เสร็จ")


async def blocking_worker(name):
    log(f"{name} เริ่ม  (time.sleep)")
    time.sleep(1)                 # บล็อกทั้ง thread — loop สลับไปหาใครไม่ได้เลย
    log(f"{name} เสร็จ")


async def main():
    print("=== A) await ต่อกันสองบรรทัด → ทำทีละอย่าง ≈2 s ===")
    reset_clock()
    await polite_worker("A1")     # รอ A1 จบก่อน
    await polite_worker("A2")     # ค่อยเริ่ม A2
    # ผล: A1 เริ่ม 0.00 → เสร็จ 1.00 → A2 เริ่ม 1.00 → เสร็จ 2.00

    print("\n=== B) รันพร้อมกัน แต่ข้างในใช้ time.sleep → ยังคง ≈2 s ===")
    reset_clock()
    await asyncio.gather(blocking_worker("B1"), blocking_worker("B2"))
    # ผล: B2 เริ่มที่ 1.00 เพราะ B1 บล็อก loop ไว้ ไม่มีจุดให้สลับ

    print("\n=== C) รันพร้อมกัน และใช้ asyncio.sleep → ≈1 s ===")
    reset_clock()
    await asyncio.gather(polite_worker("C1"), polite_worker("C2"))
    # ผล: C1 กับ C2 เริ่ม 0.00 ทั้งคู่ และเสร็จ 1.00 ทั้งคู่

    print("\n=== D) ลืม await ===")
    reset_clock()
    polite_worker("D1")           # ได้แค่ coroutine object ทิ้งไว้ → ไม่รัน
    await asyncio.sleep(0.1)
    log("ไม่เห็น 'D1 เริ่ม' เลย (Python จะเตือน RuntimeWarning: coroutine ... was never awaited)")


if __name__ == "__main__":
    asyncio.run(main())

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • await = จุดที่ "ยอมให้งานอื่นแทรก" ถ้าไม่มี await ก็ไม่มีการสลับงาน
# • await ต่อกันหลายบรรทัด = ทีละอย่าง (sequential) ไม่ได้เร็วขึ้น
# • ใน async def ใช้ asyncio.sleep เสมอ  time.sleep ทำให้ทุกอย่างช้าเหมือนเขียนแบบ sync
# • ลืม await → ฟังก์ชันไม่ทำงาน และมีคำเตือน "was never awaited"
