"""
07 · asyncio.wait_for (จำกัดเวลา)
อ้างอิงงานในคลาส: Week3/task_09_wait_for.py, Week4/foodcourt_04_wait_for.py, foodcourt_05_mix_concepts.py

result = await asyncio.wait_for(aw, timeout=วินาที)
    รับ   : awaitable 1 ตัว (coroutine หรือ task) และเวลาสูงสุด
    ทันเวลา  → คืนค่าผลลัพธ์ตามปกติ
    ไม่ทัน   → 1) ยกเลิกงานข้างในให้อัตโนมัติ (งานนั้นจะได้ CancelledError)
               2) raise asyncio.TimeoutError ใส่คนที่ await
    timeout=None → รอไม่จำกัด

แบบแผนที่ใช้บ่อย
    try:
        data = await asyncio.wait_for(fetch(), timeout=2.0)
    except asyncio.TimeoutError:
        data = ค่าสำรอง

(Python 3.11+ มีอีกแบบ:  async with asyncio.timeout(2.0): ...  ทำงานคล้ายกัน)
(ตั้งแต่ 3.11  asyncio.TimeoutError คือตัวเดียวกับ TimeoutError ของ Python)

รัน:  python 07_wait_for.py
"""
import asyncio
import time

_start = time.perf_counter()


def reset_clock():
    global _start
    _start = time.perf_counter()


def log(msg):
    print(f"[{time.perf_counter() - _start:4.2f}s] {msg}")


async def cook(menu, seconds):
    try:
        log(f"   ครัว: เริ่มทำ {menu} ({seconds} s)")
        await asyncio.sleep(seconds)
        log(f"   ครัว: {menu} เสร็จ")
        return f"{menu} พร้อม"
    except asyncio.CancelledError:
        log(f"   ครัว: {menu} ถูกยกเลิกกลางคัน")    # เห็นบรรทัดนี้เมื่อ timeout
        raise


async def main():
    print("=== 1) ทันเวลา → ได้ผลปกติ ===")
    reset_clock()
    result = await asyncio.wait_for(cook("ข้าวมันไก่", 0.8), timeout=2.0)
    log(f"ได้ {result!r}")

    print("\n=== 2) ไม่ทัน → งานข้างในถูกยกเลิก + TimeoutError ===")
    reset_clock()
    try:
        result = await asyncio.wait_for(cook("สเต็ก", 4.0), timeout=1.0)
        log(f"ได้ {result!r}")                    # ไม่ถึงบรรทัดนี้
    except asyncio.TimeoutError:
        log("TimeoutError ที่ 1.00 s — ไม่ต้องรอสเต็กครบ 4 s")

    print("\n=== 3) ใช้กับหลายงานพร้อมกัน: แต่ละงานมี timeout ของตัวเอง ===")
    reset_clock()

    async def order(menu, seconds, limit):
        try:
            return await asyncio.wait_for(cook(menu, seconds), timeout=limit)
        except asyncio.TimeoutError:
            return f"{menu}: หมดเวลา"

    results = await asyncio.gather(
        order("ก๋วยเตี๋ยว", 0.5, limit=1.0),
        order("สเต็ก", 3.0, limit=1.0),
    )
    log(f"ได้ {results}   ← รวม ≈1 s")

    print("\n=== 4) wait_for ครอบแค่งานที่ใส่ไป (แบบ foodcourt_05) ===")
    reset_clock()
    noodle = asyncio.create_task(cook("ก๋วยเตี๋ยว", 1.5))                      # ไม่มี timeout
    chicken = asyncio.create_task(asyncio.wait_for(cook("ข้าวมันไก่", 0.8), 1.0))  # timeout 1 s
    results = await asyncio.gather(noodle, chicken)
    log(f"ได้ {results}   ← ข้าวมันไก่ 0.8 s ไม่เกิน 1 s จึงไม่ timeout · รวม ≈1.5 s")


if __name__ == "__main__":
    asyncio.run(main())

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • wait_for = งานเดียว + เวลาสูงสุด
# • หมดเวลา → raise TimeoutError และยกเลิกงานข้างในให้เอง
# • ต้องครอบด้วย try/except asyncio.TimeoutError เสมอ
# • timeout ใช้กับงานที่อยู่ใน wait_for เท่านั้น ไม่เกี่ยวกับงานอื่นใน gather เดียวกัน
