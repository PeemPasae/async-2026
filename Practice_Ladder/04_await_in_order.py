"""
ขั้น 04 / 20 · await ต่อกัน = ทำทีละอย่าง
ความยาก ●●○○○    อ้างอิง: Week2/asyncio05.py

โจทย์
-----
1) async def make_coffee(name, delay=0.2)
       รอ delay วินาที แล้วคืน f"coffee for {name}"

2) async def serve_in_order(names, delay=0.2)
       เรียก make_coffee ให้ลูกค้าทีละคน "ตามลำดับ" (คนแรกเสร็จก่อนค่อยเริ่มคนต่อไป)
       คืน list ผลลัพธ์ตามลำดับชื่อ

ตัวอย่าง
    await serve_in_order(["A", "B", "C"], 0.1)
    -> ["coffee for A", "coffee for B", "coffee for C"]   ใช้เวลา ≈ 0.3 s

ขั้นนี้ตั้งใจให้ "ช้า" เพื่อเทียบกับขั้น 05

คำใบ้
    results = []
    for name in names:
        results.append(await ...)

รัน:  python 04_await_in_order.py
"""
import asyncio
from _check import check


async def make_coffee(name, delay=0.2):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


async def serve_in_order(names, delay=0.2):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


if __name__ == "__main__":
    check(4, globals())
