"""
ขั้น 13 / 20 · แก้ race condition ด้วย asyncio.Lock
ความยาก ●●●○○    อ้างอิง: Week7/server_vulnerable.py → Week7/server.py

โจทย์
-----
คลาส Wallet ด้านล่าง "มีบั๊ก" ลองรันไฟล์นี้ก่อนแก้ จะเห็นว่าถอนพร้อมกัน 10 ครั้ง
ครั้งละ 30 จากยอด 100 แล้วสำเร็จเกิน 3 ครั้ง ยอดติดลบ

แก้คลาสให้ถูก:
    - ถอนพร้อมกันกี่ครั้งก็ได้ ยอดห้ามติดลบ
    - ต้องใช้ asyncio.Lock
    - ห้ามลบบรรทัด await asyncio.sleep(0.01) (มันจำลองการเช็คกับธนาคาร)

ผลที่ถูก
    สำเร็จ 3 ครั้ง, balance == 10

ลองคิดก่อนแก้
    ทำไม thread เดียวก็ยังเกิด race ได้?  ดูว่ามี await อยู่ระหว่าง "เช็คยอด" กับ "หักเงิน"

คำใบ้
    สร้าง self.lock = asyncio.Lock() ใน __init__
    ครอบทั้ง if เช็คยอด และการหักเงินไว้ใน  async with self.lock:

รัน:  python 13_fix_race_lock.py
"""
import asyncio
from _check import check


class Wallet:
    def __init__(self, balance):
        self.balance = balance

    async def withdraw(self, amount):
        if self.balance >= amount:
            await asyncio.sleep(0.01)
            self.balance -= amount
            return True
        return False


if __name__ == "__main__":
    check(13, globals())
