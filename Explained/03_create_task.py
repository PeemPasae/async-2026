"""
03 · asyncio.create_task · await task
อ้างอิงงานในคลาส: Week2/asyncio06.py – asyncio10.py, Week1/up04_asyncio.py

task = asyncio.create_task(coro, name=None)
    รับ   : coroutine object เช่น cook("A", 1)   (ต้องมีวงเล็บ เรียกฟังก์ชันแล้ว)
            name= ตั้งชื่อ task (ไม่บังคับ)
    ทำ    : ฝาก coroutine ไว้กับ event loop ให้ "เริ่มรันเบื้องหลัง"
            ตัว task จะเริ่มจริงเมื่อฟังก์ชันปัจจุบันถึง await ครั้งถัดไป
    คืน   : Task object (ใช้เช็คสถานะ ยกเลิก หรือ await เอาผล)
    ต้องอยู่ข้างใน async def (ต้องมี loop ทำงานอยู่)

result = await task
    รอให้ task เสร็จ แล้วได้ค่าที่ coroutine return
    ถ้า task เสร็จไปแล้ว await จะได้ผลทันที

เคล็ดลับจำ: create_task = "สั่งงานให้เริ่ม"   ·   await task = "มารับของ"

รัน:  python 03_create_task.py
"""
import asyncio
import time

_start = time.perf_counter()


def reset_clock():
    global _start
    _start = time.perf_counter()


def log(msg):
    print(f"[{time.perf_counter() - _start:4.2f}s] {msg}")


async def cook(name, seconds):
    log(f"   {name}: เริ่มทำ")
    await asyncio.sleep(seconds)
    log(f"   {name}: เสร็จ")
    return f"{name} พร้อมเสิร์ฟ"


async def main():
    print("=== 1) create_task ยังไม่เริ่มทันที จนกว่าเราจะ await อะไรสักอย่าง ===")
    reset_clock()
    task = asyncio.create_task(cook("ข้าวผัด", 1))
    log("สร้าง task แล้ว — ยังไม่เห็น 'เริ่มทำ' เพราะ main ยังไม่ปล่อยการควบคุม")
    log(f"task.done() = {task.done()}")               # False
    await asyncio.sleep(0)                            # ปล่อยการควบคุม 1 จังหวะ
    log("หลัง await asyncio.sleep(0) — task ได้เริ่มแล้ว")
    result = await task                               # รอรับของ
    log(f"await task ได้ค่า: {result!r}")

    print("\n=== 2) สร้าง task ครบก่อน แล้วค่อย await → ทำพร้อมกัน ≈2 s (ไม่ใช่ 3 s) ===")
    reset_clock()
    t1 = asyncio.create_task(cook("A", 1))
    t2 = asyncio.create_task(cook("B", 2))
    r1 = await t1                                     # ระหว่างรอ A, B ก็ทำไปด้วย
    r2 = await t2                                     # B เหลืออีกแค่ 1 s
    log(f"ได้ {r1!r}, {r2!r}")

    print("\n=== 3) เทียบ: await coroutine ตรง ๆ (ไม่ใช้ task) → ทีละอย่าง ≈3 s ===")
    reset_clock()
    r1 = await cook("A", 1)
    r2 = await cook("B", 2)
    log(f"ได้ {r1!r}, {r2!r}")

    print("\n=== 4) หลายงานด้วย list (แบบ Week2/asyncio09.py) ≈1 s ===")
    reset_clock()
    tasks = []
    for name in ["C", "D", "E"]:
        tasks.append(asyncio.create_task(cook(name, 1), name=f"Task-{name}"))
    results = [await t for t in tasks]                # await ทีละตัว แต่ทุกตัวเริ่มไปแล้ว
    log(f"ได้ {results}")


if __name__ == "__main__":
    asyncio.run(main())

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • อยากให้ทำพร้อมกัน: create_task ให้ครบทุกงานก่อน → ค่อย await
# • create_task แล้ว await ทันทีในบรรทัดเดียวกัน = ไม่ต่างจาก await ตรง ๆ
# • เก็บ task ไว้ในตัวแปร/list เสมอ ถ้าไม่เก็บจะ await เอาผลหรือยกเลิกทีหลังไม่ได้
# • เวลารวมแบบพร้อมกัน = เวลาของงานที่ช้าที่สุด
