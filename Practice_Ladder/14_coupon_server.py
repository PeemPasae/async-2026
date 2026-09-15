"""
ขั้น 14 / 20 · ระบบแจกคูปอง (Lock + หลายเงื่อนไข)
ความยาก ●●●●○    อ้างอิง: Week7/server.py

โจทย์
-----
เขียนคลาส CouponServer(total, limit=2)
    self.coupons = ["C01", "C02", ..., f"C{total:02d}"]
    แต่ละคนรับได้ไม่เกิน limit ใบ

    async def claim(self, user) คืน tuple:
        ("SUCCESS", "C01")   ได้คูปองใบถัดไป
        ("LIMIT", None)      คนนี้ได้ครบ limit แล้ว
        ("SOLD_OUT", None)   คูปองหมด

    ต้องมี await asyncio.sleep(0.01) ก่อนตัดคูปอง (จำลองเขียนฐานข้อมูล)
    ถ้าหลายคนเรียก claim พร้อมกัน: ห้ามแจกซ้ำ ห้ามแจกเกิน ห้ามมีใครได้เกิน limit

ตัวอย่าง
    s = CouponServer(5)
    await s.claim("u1") -> ("SUCCESS", "C01")
    await s.claim("u1") -> ("SUCCESS", "C02")
    await s.claim("u1") -> ("LIMIT", None)

คำใบ้
    เก็บ index ของคูปองใบถัดไป และ dict {user: [coupon, ...]}
    เช็ค LIMIT, เช็ค SOLD_OUT, ตัดคูปอง — ทั้ง 3 อย่างอยู่ใน lock ก้อนเดียว

รัน:  python 14_coupon_server.py
"""
import asyncio
from _check import check


class CouponServer:
    def __init__(self, total, limit=2):
        # เขียนโค้ดตรงนี้
        raise NotImplementedError

    async def claim(self, user):
        # เขียนโค้ดตรงนี้
        raise NotImplementedError


if __name__ == "__main__":
    check(14, globals())
