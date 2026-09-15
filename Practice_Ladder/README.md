# บันไดฝึกเขียน asyncio (20 ขั้น)

เริ่มจากฟังก์ชันเล็ก ๆ แล้วค่อย ๆ ยากขึ้น แต่ละขั้นใช้ของที่ฝึกมาจากขั้นก่อน ๆ

## วิธีใช้

1. เปิดไฟล์ขั้นที่จะทำ แล้วอ่านโจทย์ใน docstring ด้านบน
2. ลบ `raise NotImplementedError` ออก แล้วเขียนโค้ดแทน
3. รันไฟล์นั้นตรง ๆ ตัวตรวจจะบอกว่าผ่านกี่ข้อ ถ้าไม่ผ่านจะบอกว่าผิดตรงไหน

```bash
cd async-2026/Practice_Ladder
python 01_grade.py
```

| สัญลักษณ์ | ความหมาย |
|---|---|
| ✅ | ผ่าน |
| ❌ | ผลลัพธ์หรือเวลาไม่ตรงกับที่โจทย์ต้องการ |
| 💥 | โค้ด error (จะบอกบรรทัดที่พังให้) |
| ⬜ | ยังไม่ได้เขียน |

ติดจริง ๆ ค่อยเปิด `solutions/` ไฟล์ชื่อเดียวกัน ถ้ารันไฟล์เฉลยก็จะผ่านครบ

## ขั้นทั้งหมด

| ขั้น | ไฟล์ | ฝึกอะไร | อ้างอิงจากงานในคลาส |
|---|---|---|---|
| **ระดับ 0 · อุ่นเครื่อง** ||||
| 01 | `01_grade.py` | if / elif, ค่าขอบ | WX/grade.py |
| 02 | `02_summarize_orders.py` | list, dict, sum, max | Week4 |
| **ระดับ 1 · coroutine** ||||
| 03 | `03_first_coroutine.py` | `async def`, `await asyncio.sleep` | Week2 asyncio01–04 |
| 04 | `04_await_in_order.py` | await ต่อกัน = ทีละอย่าง | Week2 asyncio05 |
| 05 | `05_create_task_together.py` | `create_task` ทำพร้อมกัน | Week2 asyncio07, 09 |
| 06 | `06_gather_order.py` | `gather` ลำดับผล vs ลำดับเสร็จ | Week3 task_07 |
| **ระดับ 2 · ควบคุม task** ||||
| 07 | `07_task_status.py` | `done()`, `get_name()` | Week3 task_01, 05 |
| 08 | `08_cancel_task.py` | `cancel()`, `CancelledError` | Week3 smart_courier |
| 09 | `09_gather_exceptions.py` | `return_exceptions=True` | Week3 task_02 |
| 10 | `10_wait_for_timeout.py` | `wait_for` + timeout | Week4 foodcourt_04, 05 |
| 11 | `11_wait_first_completed.py` | `wait(FIRST_COMPLETED)` + cancel pending | Week3 stock_price |
| 12 | `12_retry_timeout.py` | loop + wait_for + retry | รวมขั้น 10 |
| **ระดับ 3 · ข้อมูลที่แชร์กัน** ||||
| 13 | `13_fix_race_lock.py` | แก้บั๊ก race ด้วย `asyncio.Lock` | Week7 server |
| 14 | `14_coupon_server.py` | Lock + หลายเงื่อนไข | Week7 server |
| **ระดับ 4 · Queue** ||||
| 15 | `15_queue_basic.py` | put / get / sentinel | Week8 02, 03 |
| 16 | `16_queue_workers.py` | หลาย worker, `task_done`, `join` | Week8 05, 08 |
| 17 | `17_queue_pipeline.py` | pipeline 2 คิวต่อกัน | Week8 06 |
| **ระดับ 5 · ของจริง** ||||
| 18 | `18_httpx_robot_factory.py` | `httpx.AsyncClient` (เซิร์ฟเวอร์จำลอง ไม่ต้องต่อเน็ต) | Week6 robots |
| 19 | `19_fastapi_foodcourt.py` | FastAPI: path, query, body, 404, Lock | Week5, Week7 |
| 20 | `20_boss_lunch_rush.py` | Lock + wait_for + Queue รวมกัน | ทุกขั้น |

## หมายเหตุ

- ขั้น 18 ต้องมี `httpx` ส่วนขั้น 19 ต้องมี `fastapi` เพิ่ม (`pip install fastapi`)
- ตัวตรวจจับเวลาด้วย ถ้าผลลัพธ์ถูกแต่ขึ้น ❌ เรื่องเวลา แปลว่ายังไม่ได้ทำพร้อมกัน (หรือพร้อมกันเกินไปในขั้น 04)
- ถ้าเครื่องช้ามากจนเวลาคลาดเคลื่อน ลองรันใหม่อีกครั้ง
