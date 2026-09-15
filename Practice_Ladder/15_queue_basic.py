"""
ขั้น 15 / 20 · Queue พื้นฐาน: producer 1 ตัว consumer 1 ตัว
ความยาก ●●●○○    อ้างอิง: Week8/02_basic_asyncio_queue.py, 03_put_and_get_mechanism.py

โจทย์
-----
1) async def producer(q, items)
       ใส่ของใน items ลงคิวทีละชิ้น (พัก 0.01 s ระหว่างชิ้น)
       ใส่ครบแล้วปิดท้ายด้วย None  (sentinel = สัญญาณว่าหมดแล้ว)

2) async def consumer(q)
       ดึงของออกจากคิวไปเรื่อย ๆ จนเจอ None
       คืน list ของที่ได้ (ไม่รวม None)

3) async def pipeline(items)
       สร้าง asyncio.Queue() แล้วรัน producer กับ consumer พร้อมกัน
       คืน list ที่ consumer ได้

ตัวอย่าง
    await pipeline(["a", "b", "c"]) -> ["a", "b", "c"]
    await pipeline([])              -> []

คำใบ้
    item = await q.get()
    if item is None: break
    _, got = await asyncio.gather(producer(q, items), consumer(q))

รัน:  python 15_queue_basic.py
"""
import asyncio
from _check import check


async def producer(q, items):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


async def consumer(q):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


async def pipeline(items):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


if __name__ == "__main__":
    check(15, globals())
