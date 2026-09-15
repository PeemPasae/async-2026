"""
ขั้น 11 / 20 · wait(FIRST_COMPLETED): เอาคนแรกที่ตอบ แล้วยกเลิกที่เหลือ
ความยาก ●●●○○    อ้างอิง: Week3/stock_price.py, task_08_wait.py, Week4/foodcourt_03_wait_first.py

โจทย์
-----
เขียน async def fastest_server(servers)
    servers เป็น dict {ชื่อเซิร์ฟเวอร์: delay}
    1. สร้าง task ของ ping(name, delay) ให้ทุกเซิร์ฟเวอร์
    2. รอจนมี "ตัวแรก" เสร็จ
    3. cancel ทุกตัวที่ยังไม่เสร็จ
    4. คืน tuple (ชื่อผู้ชนะ, จำนวน task ที่ถูก cancel)

ตัวอย่าง
    await fastest_server({"alpha": 0.5, "beta": 0.1, "gamma": 0.3})
    -> ("beta", 2)      ใช้เวลา ≈ 0.1 s
    และ ping_cancelled จะมี "alpha", "gamma"

จุดที่คนพลาด
    done เป็น set  →  ใช้ done.pop() หรือ list(done)[0]  (done[0] ใช้ไม่ได้)
    ผลลัพธ์ต้องเรียก .result() จาก task

รัน:  python 11_wait_first_completed.py
"""
import asyncio
from _check import check

# ---- ให้มา (ห้ามแก้) ----
ping_cancelled = []


async def ping(name, delay):
    try:
        await asyncio.sleep(delay)
        return name
    except asyncio.CancelledError:
        ping_cancelled.append(name)
        raise


# ---- เขียนโค้ดตรงนี้ ----
async def fastest_server(servers):
    raise NotImplementedError


if __name__ == "__main__":
    check(11, globals())
