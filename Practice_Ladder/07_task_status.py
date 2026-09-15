"""
ขั้น 07 / 20 · สถานะของ Task
ความยาก ●●○○○    อ้างอิง: Week3/task_01_status.py, task_05_nameing.py

โจทย์
-----
เขียน async def task_report()
    1. สร้าง task จาก slow_job() โดยตั้งชื่อว่า "Report-Job"
    2. เช็ค task.done() ทันที เก็บไว้เป็น done_before
    3. await task เพื่อเอาผลลัพธ์
    4. เช็ค task.done() อีกครั้ง เก็บเป็น done_after
    5. คืน dict:
       {"name": <ชื่อ task>, "done_before": ..., "result": ..., "done_after": ...}

ผลที่ถูก
    {"name": "Report-Job", "done_before": False, "result": "OK", "done_after": True}

คำใบ้
    asyncio.create_task(coro, name="...")   ·   task.get_name()

รัน:  python 07_task_status.py
"""
import asyncio
from _check import check


# ---- ให้มา (ห้ามแก้) ----
async def slow_job():
    await asyncio.sleep(0.1)
    return "OK"


# ---- เขียนโค้ดตรงนี้ ----
async def task_report():
    raise NotImplementedError


if __name__ == "__main__":
    check(7, globals())
