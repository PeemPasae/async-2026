"""
ขั้น 17 / 20 · Pipeline 2 ต่อ: ครัว → ไรเดอร์
ความยาก ●●●●○    อ้างอิง: Week8/06_scraper_downloader.py (producer → queue → consumer)

โจทย์
-----
เขียน async def food_pipeline(orders, cooks=2, riders=1, cook_time=0.1, ride_time=0.05)

    orders ──► kitchen_q ──► [พ่อครัว × cooks] ──► delivery_q ──► [ไรเดอร์ × riders] ──► delivered

    พ่อครัว:  ดึงออเดอร์จาก kitchen_q → รอ cook_time → ใส่ลง delivery_q → task_done
    ไรเดอร์:  ดึงจาก delivery_q → รอ ride_time → เพิ่ม f"{order} delivered" ลง list → task_done

    คืน list delivered (ลำดับไหนก็ได้) และหลังจบต้องไม่มี task ค้าง

ตัวอย่าง
    await food_pipeline(["o1", "o2", "o3", "o4"], cooks=2, riders=2)
    -> ["o1 delivered", ...]    ใช้เวลา ≈ 0.25 s

ลำดับการปิดระบบ (สำคัญ)
    1. ใส่ออเดอร์ทั้งหมด → await kitchen_q.join()
    2. ส่ง None ให้พ่อครัวครบทุกคน
    3. await delivery_q.join()   ← ทำหลังข้อ 1 เพราะพ่อครัวยังใส่ของลง delivery_q อยู่
    4. ส่ง None ให้ไรเดอร์ครบทุกคน
    5. gather รอทุก task จบ

รัน:  python 17_queue_pipeline.py
"""
import asyncio
from _check import check


async def food_pipeline(orders, cooks=2, riders=1, cook_time=0.1, ride_time=0.05):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


if __name__ == "__main__":
    check(17, globals())
