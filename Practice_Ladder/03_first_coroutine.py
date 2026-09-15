"""
ขั้น 03 / 20 · coroutine ตัวแรก
ความยาก ●○○○○    อ้างอิง: Week2/asyncio01–04.py

โจทย์
-----
เขียน async def add_later(a, b, delay)
    1. รอ delay วินาทีแบบไม่บล็อก
    2. คืนค่า a + b

ตัวอย่าง
    asyncio.run(add_later(2, 3, 1))   -> 5 (หลังรอ 1 วินาที)

สิ่งที่ควรสังเกต
    add_later(2, 3, 1) เฉย ๆ ไม่ได้ 5 แต่ได้ "coroutine object" — ต้อง await หรือ asyncio.run

คำใบ้
    await asyncio.sleep(delay)   ไม่ใช่ time.sleep(delay)

รัน:  python 03_first_coroutine.py
"""
import asyncio
from _check import check


async def add_later(a, b, delay):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


if __name__ == "__main__":
    check(3, globals())
