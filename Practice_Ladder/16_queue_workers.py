"""
ขั้น 16 / 20 · หลาย worker + task_done / join / sentinel
ความยาก ●●●●○    อ้างอิง: Week8/05_task_completion_and_join.py, 08_coupon_producer_consumer2.py

โจทย์
-----
เขียน async def process_jobs(jobs, n_workers, job_time)
    - ใส่ทุกงานใน jobs ลง asyncio.Queue
    - สร้าง worker n_workers ตัว ชื่อ "W1", "W2", ... แต่ละตัว:
        ดึงงาน → รอ job_time วินาที → บันทึกว่าทำเสร็จ → q.task_done()
    - รอจนงานในคิวหมด (q.join())
    - ส่ง None ให้ worker ทุกตัว แล้วรอให้ worker จบครบ
    - คืน dict:
        {"done": [งานที่ทำเสร็จ...],
         "per_worker": {"W1": จำนวนงาน, "W2": ..., ...}}   ← ต้องมีทุก worker แม้ทำ 0 งาน

ตัวอย่าง
    6 งาน, 3 worker, งานละ 0.1 s  -> ใช้เวลา ≈ 0.2 s
    หลังฟังก์ชันจบต้องไม่มี worker ค้างอยู่

จุดที่คนพลาด
    ลืม task_done() ตอนเจอ None  → ไม่พังตรงนี้ แต่ติดนิสัยไปจะทำให้ join() ค้างในขั้นถัดไป
    ส่ง None น้อยกว่าจำนวน worker → มี worker ค้างรอ get() ตลอดไป

คำใบ้ (โครง)
    async def worker(name):
        per_worker[name] = 0
        while True:
            job = await q.get()
            if job is None:
                q.task_done()
                break
            ...

รัน:  python 16_queue_workers.py
"""
import asyncio
from _check import check


async def process_jobs(jobs, n_workers, job_time):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


if __name__ == "__main__":
    check(16, globals())
