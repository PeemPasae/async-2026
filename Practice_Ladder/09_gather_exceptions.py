"""
ขั้น 09 / 20 · gather เมื่อบางงานพัง
ความยาก ●●●○○    อ้างอิง: Week3/task_02_exception.py, Week5/fastapi_async_external_api_lab.py

โจทย์
-----
1) async def divide(a, b)
       รอ 0.1 วินาที แล้วคืน a / b

2) async def divide_all(pairs)
       pairs เป็น list ของ (a, b)
       หารทุกคู่ "พร้อมกัน" ถ้าคู่ไหน error ให้ใส่ข้อความ "error: <ชื่อ exception>" แทน
       คู่อื่นต้องได้ผลตามปกติ และลำดับต้องตรงกับ pairs

ตัวอย่าง
    await divide_all([(10, 2), (1, 0), (5, 2)])
    -> [5.0, "error: ZeroDivisionError", 2.5]     ใช้เวลา ≈ 0.1 s

คำใบ้
    asyncio.gather(..., return_exceptions=True)  จะคืน exception เป็นค่าใน list แทนการ raise
    isinstance(x, Exception)  ·  type(x).__name__

รัน:  python 09_gather_exceptions.py
"""
import asyncio
from _check import check


async def divide(a, b):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


async def divide_all(pairs):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


if __name__ == "__main__":
    check(9, globals())
