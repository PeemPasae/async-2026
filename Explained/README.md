# อธิบายฟังก์ชันสำคัญ ทีละตัว

แต่ละไฟล์อธิบายฟังก์ชันหนึ่งกลุ่ม ในไฟล์มี 3 ส่วน

1. **ด้านบน:** บอกว่ารับอะไร คืนอะไร และใช้ตอนไหน
2. **ตรงกลาง:** ตัวอย่างที่รันได้ พร้อมคอมเมนต์ภาษาไทยทีละบรรทัด
3. **ท้ายไฟล์:** สรุปสั้น ๆ ไว้ทวนก่อนสอบ

## วิธีอ่าน

เปิดไฟล์ใน VS Code แล้วรันไปพร้อมกัน ผลที่พิมพ์ออกมามีเวลากำกับไว้ เช่น `[1.00s]` ให้เทียบกับคอมเมนต์ในโค้ดว่าเกิดขึ้นตรงตามที่อธิบายไหม

```bash
cd async-2026/Explained
python 01_def_vs_async_def.py
```

## ลำดับการอ่าน (จากเล็กไปใหญ่)

| ไฟล์ | ฟังก์ชันที่อธิบาย | ใช้ต่อในโจทย์ฝึก (Practice_Ladder) |
|---|---|---|
| `01_def_vs_async_def.py` | `def` / `async def`, coroutine object, `asyncio.run` | ขั้น 03 |
| `02_await_and_sleep.py` | `await`, `asyncio.sleep` เทียบกับ `time.sleep` | ขั้น 03–04 |
| `03_create_task.py` | `asyncio.create_task`, `await task` | ขั้น 05 |
| `04_gather.py` | `asyncio.gather`, `*list`, `return_exceptions` | ขั้น 06, 09 |
| `05_task_methods.py` | `done`, `result`, `exception`, `get_name`, `add_done_callback`, `current_task`, `all_tasks` | ขั้น 07 |
| `06_cancel.py` | `task.cancel`, `CancelledError`, `cancelled` | ขั้น 08 |
| `07_wait_for.py` | `asyncio.wait_for`, `TimeoutError` | ขั้น 10, 12 |
| `08_wait.py` | `asyncio.wait`, `FIRST_COMPLETED` / `FIRST_EXCEPTION` / `ALL_COMPLETED` | ขั้น 11 |
| `09_lock.py` | race condition, `asyncio.Lock`, `async with` | ขั้น 13–14 |
| `10_queue.py` | `Queue`, `put`/`get`, `maxsize`, `task_done`/`join`, sentinel | ขั้น 15–17 |
| `11_thread_process.py` | `threading.Thread`, `multiprocessing.Process`, `asyncio.to_thread`, `run_in_executor` | Week 1–2 |
| `12_httpx_client.py` | `httpx.AsyncClient`, `get`/`post`, `json()`, `raise_for_status` | ขั้น 18 |
| `13_fastapi.py` | route, path/query/body, `HTTPException`, WebSocket | ขั้น 19 |
| `14_redis_stream_pubsub.py` | `set`/`get`, `xadd`, `xgroup_create`, `xreadgroup`, `xack`, `publish`/`subscribe` | Week 9–10 |

## สิ่งที่ต้องติดตั้ง

- ไฟล์ 01–11 ใช้แค่ Python ธรรมดา
- ไฟล์ 12 ต้องมี `httpx` (เครื่องมีอยู่แล้ว)
- ไฟล์ 13 ต้องติดตั้ง `fastapi` ก่อน
- ไฟล์ 14 ต้องติดตั้ง `redis` และต้องมี Redis server เปิดอยู่ ถ้าไม่มี server ไฟล์จะแจ้งแล้วจบ ให้อ่านโค้ดกับคอมเมนต์แทน

อ่านไฟล์ไหนจบแล้ว ให้ไปทำโจทย์ขั้นที่ตรงกันใน `../Practice_Ladder` ต่อได้เลย
