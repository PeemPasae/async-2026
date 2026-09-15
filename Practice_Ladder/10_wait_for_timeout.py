"""
ขั้น 10 / 20 · wait_for: กำหนดเวลาสูงสุด
ความยาก ●●●○○    อ้างอิง: Week3/task_09_wait_for.py, Week4/foodcourt_04_wait_for.py, foodcourt_05_mix_concepts.py

โจทย์
-----
1) async def order_with_timeout(shop, timeout)
       เรียก cook(shop) ที่ให้มา แต่ห้ามรอเกิน timeout วินาที
       ทันเวลา  -> คืนผลของ cook เช่น "chicken ready"
       ไม่ทัน   -> คืน f"{shop}: timeout"

2) async def order_many(shops, timeout)
       สั่งทุกร้านพร้อมกัน แต่ละร้านมี timeout ของตัวเอง
       คืน list ผลตามลำดับ shops

ตัวอย่าง
    await order_with_timeout("steak", 0.2)   -> "steak: timeout"   (≈0.2 s ไม่ใช่ 0.8 s)
    await order_many(["chicken", "steak", "noodle"], 0.35)
    -> ["chicken ready", "steak: timeout", "noodle ready"]      (≈0.35 s)

คำใบ้
    try:
        return await asyncio.wait_for(cook(shop), timeout=timeout)
    except asyncio.TimeoutError:
        ...
    ขั้นที่ 2 ใช้ gather กับฟังก์ชันขั้นที่ 1 ได้เลย

รัน:  python 10_wait_for_timeout.py
"""
import asyncio
from _check import check

# ---- ให้มา (ห้ามแก้) ----
SHOP_TIME = {"chicken": 0.1, "noodle": 0.3, "steak": 0.8}


async def cook(shop):
    await asyncio.sleep(SHOP_TIME[shop])
    return f"{shop} ready"


# ---- เขียนโค้ดตรงนี้ ----
async def order_with_timeout(shop, timeout):
    raise NotImplementedError


async def order_many(shops, timeout):
    raise NotImplementedError


if __name__ == "__main__":
    check(10, globals())
