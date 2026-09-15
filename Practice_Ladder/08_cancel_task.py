"""
ขั้น 08 / 20 · ยกเลิก Task อย่างถูกวิธี
ความยาก ●●●○○    อ้างอิง: Week3/smart_courier.py, task_03_cancel.py

โจทย์
-----
1) async def download(filename)
       - ปกติ: รอ 0.3 วินาที แล้วคืน f"{filename} saved"
       - ถ้าถูก cancel ระหว่างรอ: ต่อท้าย filename ลง cleanup_log แล้ว "raise ต่อ"

2) async def start_and_cancel(filename, after)
       - สร้าง task ของ download(filename)
       - รอ after วินาที แล้ว cancel task
       - await task (ต้องจับ CancelledError ไม่ให้หลุดออกไป)
       - คืนค่า task.cancelled()

ตัวอย่าง
    await start_and_cancel("a.zip", 0.1)  -> True   และ cleanup_log == ["a.zip"]

จุดที่คนพลาด
    ถ้า except CancelledError แล้วไม่ raise ต่อ  task.cancelled() จะเป็น False

คำใบ้
    try:
        await asyncio.sleep(0.3)
        return ...
    except asyncio.CancelledError:
        ...
        raise

รัน:  python 08_cancel_task.py
"""
import asyncio
from _check import check

# ---- ให้มา (ห้ามแก้) ----
cleanup_log = []


# ---- เขียนโค้ดตรงนี้ ----
async def download(filename):
    raise NotImplementedError


async def start_and_cancel(filename, after):
    raise NotImplementedError


if __name__ == "__main__":
    check(8, globals())
