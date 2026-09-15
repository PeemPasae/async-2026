"""
ขั้น 06 / 20 · gather: ลำดับผลลัพธ์ vs ลำดับที่เสร็จจริง
ความยาก ●●○○○    อ้างอิง: Week3/task_07_gather.py, Week4/foodcourt_02_gather.py

โจทย์
-----
1) async def cook(name, seconds, finish_order)
       รอ seconds วินาที → ต่อท้าย name ลงใน list finish_order → คืน name

2) async def cook_all(menu)
       menu เป็น dict {ชื่อเมนู: วินาที}
       ทำทุกเมนูพร้อมกันด้วย asyncio.gather โดยใช้ finish_order ร่วมกัน list เดียว
       คืน tuple (results, finish_order)

ตัวอย่าง
    await cook_all({"steak": 0.3, "chicken": 0.1, "noodle": 0.2})
    -> (["steak", "chicken", "noodle"],     ← gather เรียงตามที่ส่งเข้าไป
        ["chicken", "noodle", "steak"])     ← ลำดับที่เสร็จจริง
    ใช้เวลา ≈ 0.3 s

คำใบ้
    menu.items() ให้ (name, seconds)
    asyncio.gather(*(cook(n, s, finish_order) for n, s in menu.items()))

รัน:  python 06_gather_order.py
"""
import asyncio
from _check import check


async def cook(name, seconds, finish_order):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


async def cook_all(menu):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


if __name__ == "__main__":
    check(6, globals())
