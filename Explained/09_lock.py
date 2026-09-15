"""
09 · Race condition และ asyncio.Lock
อ้างอิงงานในคลาส: Week7/server_vulnerable.py → Week7/server.py

ทำไม asyncio (thread เดียว) ยังเกิด race ได้?
    ทุก "await" คือจุดที่งานอื่นแทรกเข้ามาได้
    ถ้าเขียน  อ่านค่าที่แชร์กัน → await → เขียนค่ากลับ
    งานอื่นอาจแทรกตรง await แล้วอ่านค่า "ตัวเดิม" ไปใช้ด้วย

lock = asyncio.Lock()
    - กุญแจ 1 ดอก ใครถืออยู่คนเดียวถึงเข้า critical section ได้ ที่เหลือต่อคิวรอ
    - สร้าง "ครั้งเดียว" แล้วใช้ร่วมกัน (ระดับไฟล์ หรือใน __init__)
      ถ้าสร้างใหม่ทุกครั้งที่เรียกฟังก์ชัน = ต่างคนต่างมีกุญแจ ไม่ได้กันอะไรเลย

async with lock:
    ...critical section...
    - ขอกุญแจ (ถ้ามีคนถืออยู่ → await รอคิว)
    - ออกจากบล็อกเมื่อไร คืนกุญแจอัตโนมัติ แม้จะ return หรือ raise ข้างใน
    - เทียบเท่า  await lock.acquire()  try: ...  finally: lock.release()

lock.locked() → True ถ้ามีคนถือกุญแจอยู่
ใช้ asyncio.Lock กับโค้ด async · threading.Lock ใช้กับ thread (ห้ามสลับกัน)

รัน:  python 09_lock.py
"""
import asyncio

# ------------------------------------------------------------------ ไม่มี Lock
coupons = ["C01", "C02", "C03", "C04", "C05"]
next_index = 0


async def claim_unsafe(user):
    global next_index
    if next_index < len(coupons):
        idx = next_index                 # 1) อ่านค่าที่แชร์กัน
        await asyncio.sleep(0.1)         # 2) await → คนอื่นแทรกตรงนี้ แล้วอ่าน idx ตัวเดียวกัน!
        next_index = idx + 1             # 3) เขียนกลับ
        return f"{user} ได้ {coupons[idx]}"
    return f"{user} คูปองหมด"


# ------------------------------------------------------------------ มี Lock
lock = asyncio.Lock()                    # สร้างครั้งเดียว ใช้ร่วมกันทุก request
safe_index = 0


async def claim_safe(user):
    global safe_index
    async with lock:                     # เช็ค + อ่าน + เขียน อยู่ในล็อกเดียวกันทั้งก้อน
        if safe_index < len(coupons):
            idx = safe_index
            await asyncio.sleep(0.1)     # หลับได้ปลอดภัย เพราะยังถือกุญแจ คนอื่นรอที่ async with
            safe_index = idx + 1
            return f"{user} ได้ {coupons[idx]}"
        return f"{user} คูปองหมด"


async def main():
    users = ["ต้น", "ฝน", "เก่ง"]

    print("=== 1) ไม่มี Lock: 3 คนกดพร้อมกัน ===")
    results = await asyncio.gather(*(claim_unsafe(u) for u in users))
    for r in results:
        print("  ", r)
    print(f"   next_index = {next_index}  ← แจกไป 3 ครั้ง แต่ตัวชี้ขยับแค่ 1 · ทุกคนได้ C01 ซ้ำกัน")

    print("\n=== 2) มี Lock: 3 คนกดพร้อมกัน ===")
    results = await asyncio.gather(*(claim_safe(u) for u in users))
    for r in results:
        print("  ", r)
    print(f"   safe_index = {safe_index}  ← ถูกต้อง ไม่มีใครได้ซ้ำ (แลกกับการต่อคิว ≈0.3 s)")

    print("\n=== 3) lock.locked() ===")

    async def hold():
        async with lock:
            await asyncio.sleep(0.2)

    t = asyncio.create_task(hold())
    await asyncio.sleep(0.05)
    print("   ระหว่างมีคนถือ :", lock.locked())    # True
    await t
    print("   หลังคืนกุญแจ   :", lock.locked())    # False


if __name__ == "__main__":
    asyncio.run(main())

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • race เกิดเมื่อมี await คั่นระหว่าง "อ่าน/เช็ค" กับ "เขียน" ค่าที่แชร์กัน
# • แก้ด้วย async with lock: ครอบ "ทั้ง" เช็คเงื่อนไข และการแก้ค่า ไว้ในก้อนเดียว
#   (Week7/server.py: เช็คโควตา + เช็คสต็อก + ตัดคูปอง ต้องอยู่ในล็อกเดียวกัน)
# • Lock ต้องสร้างครั้งเดียวแล้วใช้ร่วมกัน
