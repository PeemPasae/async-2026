"""
ขั้น 05 / 20 · create_task = ทำพร้อมกัน
ความยาก ●●○○○    อ้างอิง: Week2/asyncio07.py, asyncio09.py, Week1/up04_asyncio.py

โจทย์
-----
เขียน async def serve_together(names, delay=0.2)
    ชงกาแฟให้ทุกคน "พร้อมกัน" ด้วย make_coffee ที่ให้มา
    คืน list ผลลัพธ์เรียงตามลำดับชื่อ (ไม่ใช่ลำดับที่เสร็จ)

ตัวอย่าง
    await serve_together(["A", "B", "C", "D"], 0.2)
    -> ["coffee for A", ..., "coffee for D"]   ใช้เวลา ≈ 0.2 s (ไม่ใช่ 0.8 s)

ลองทำ 2 แบบ
    แบบ 1: create_task ทุกคนเก็บใน list ก่อน แล้ววน await ทีละ task
    แบบ 2: asyncio.gather(*tasks)

คำใบ้
    ถ้าเขียน  for n in names: await make_coffee(n)  จะกลับไปช้าเหมือนขั้น 04
    ต้อง "สร้างครบก่อน แล้วค่อยรอ"

รัน:  python 05_create_task_together.py
"""
import asyncio
from _check import check


# ---- ให้มา (ห้ามแก้) ----
async def make_coffee(name, delay=0.2):
    await asyncio.sleep(delay)
    return f"coffee for {name}"


# ---- เขียนโค้ดตรงนี้ ----
async def serve_together(names, delay=0.2):
    raise NotImplementedError


if __name__ == "__main__":
    check(5, globals())
