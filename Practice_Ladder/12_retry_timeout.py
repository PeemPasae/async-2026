"""
ขั้น 12 / 20 · retry + timeout (รวม loop, wait_for, try/except)
ความยาก ●●●○○    อ้างอิง: Week3/task_09_wait_for.py, Week7/client.py (ยิงซ้ำหลายครั้ง)

โจทย์
-----
เขียน async def fetch_with_retry(fetch, attempts, timeout)
    fetch     = ฟังก์ชัน async ไม่มีพารามิเตอร์ (เรียกด้วย fetch())
    attempts  = ลองได้สูงสุดกี่ครั้ง
    timeout   = แต่ละครั้งรอได้ไม่เกินกี่วินาที

    - ลองเรียก fetch() โดยจำกัดเวลา
    - ถ้าหมดเวลา ให้ลองใหม่ (เรียก fetch() ครั้งใหม่)
    - สำเร็จเมื่อไร คืน (ผลลัพธ์, ครั้งที่สำเร็จ)   ← นับครั้งแรก = 1
    - ถ้าไม่สำเร็จเลย คืน (None, attempts)

ตัวอย่าง (ตัวตรวจจะสร้าง fetch ที่ช้า 2 ครั้งแรก แล้วเร็วในครั้งที่ 3)
    await fetch_with_retry(fetch, 5, 0.1)  -> ("data", 3)

คำใบ้
    for attempt in range(1, attempts + 1):
        try:
            ...
        except asyncio.TimeoutError:
            ...

รัน:  python 12_retry_timeout.py
"""
import asyncio
from _check import check


async def fetch_with_retry(fetch, attempts, timeout):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


if __name__ == "__main__":
    check(12, globals())
