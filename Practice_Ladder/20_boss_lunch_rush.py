"""
ขั้น 20 / 20 · บอสท้ายด่าน: Lunch Rush (Lock + wait_for + Queue รวมกัน)
ความยาก ●●●●●    อ้างอิง: ขั้น 10, 13, 16

โจทย์
-----
ส่วนที่ 1: class FoodCourt(stock)
    self.stock = dict(stock)      เช่น {"steak": 2, "chicken": 10}
    ต้องมี asyncio.Lock

    async def reserve(self, menu) -> bool
        (ใน lock) ถ้าสต็อก menu > 0: await asyncio.sleep(0.01) แล้วลด 1 → True
        ถ้าหมดหรือไม่มีเมนูนี้ → False

    async def release(self, menu)
        (ใน lock) คืนสต็อก menu 1 ชิ้น

    async def cook(self, menu, timeout) -> str
        รอ COOK_TIME[menu] แต่ห้ามเกิน timeout → "READY" หรือ "TIMEOUT"

    async def order(self, student, menu, timeout) -> str
        จองไม่ได้ → "SOLD_OUT"
        จองได้ → cook → ถ้า "TIMEOUT" ต้อง release คืนสต็อก → คืนสถานะ

ส่วนที่ 2: async def lunch_rush(court, orders, n_cooks, timeout) -> dict
    orders = [("s1", "chicken"), ("s2", "steak"), ...]
    ใส่ทุกออเดอร์ลง Queue แล้วให้พ่อครัว n_cooks คนช่วยกันเรียก court.order(...)
    คืน dict {(student, menu): สถานะ}
    ปิดพ่อครัวทุกคนให้เรียบร้อย ไม่มี task ค้าง

ตัวอย่าง
    court = FoodCourt({"steak": 2})
    4 คนสั่ง steak พร้อมกัน → READY 2 จาน, SOLD_OUT 2 จาน   (≈0.5 s)
    FoodCourt({"steak": 1}).order("s1", "steak", 0.1) → "TIMEOUT" และสต็อกกลับเป็น 1

เพิ่มความทนทาน (ไม่บังคับ)
    ใน worker ใช้ try/finally เรียก q.task_done() เพื่อไม่ให้ join() ค้างถ้า order() พัง

รัน:  python 20_boss_lunch_rush.py
"""
import asyncio
from _check import check

# ---- ให้มา (ห้ามแก้) ----
COOK_TIME = {"chicken": 0.1, "noodle": 0.2, "steak": 0.5}


# ---- เขียนโค้ดตรงนี้ ----
class FoodCourt:
    def __init__(self, stock):
        raise NotImplementedError

    async def reserve(self, menu):
        raise NotImplementedError

    async def release(self, menu):
        raise NotImplementedError

    async def cook(self, menu, timeout):
        raise NotImplementedError

    async def order(self, student, menu, timeout):
        raise NotImplementedError


async def lunch_rush(court, orders, n_cooks, timeout):
    raise NotImplementedError


if __name__ == "__main__":
    check(20, globals())
