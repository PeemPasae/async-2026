"""
08 · asyncio.wait (FIRST_COMPLETED / FIRST_EXCEPTION / ALL_COMPLETED)
อ้างอิงงานในคลาส: Week3/stock_price.py, task_08_wait.py, task_10_gather_vs_wait.py,
                 Week4/foodcourt_03_wait_first.py, Practice_Midterm/Test.py

done, pending = await asyncio.wait(tasks, timeout=None, return_when=ALL_COMPLETED)
    รับ   : iterable ของ "Task" (set หรือ list) → ต้อง create_task ก่อนส่ง
    return_when:
        asyncio.FIRST_COMPLETED  คืนเมื่อมีตัวแรกจบ (จบแบบไหนก็ได้ รวม error)
        asyncio.FIRST_EXCEPTION  คืนเมื่อมีตัวแรกที่ error · ถ้าไม่มีใคร error = รอทั้งหมด
        asyncio.ALL_COMPLETED    รอทุกตัว (ค่าเริ่มต้น)
    timeout : หมดเวลาแล้วคืนค่าเลย "ไม่ raise" (ต่างจาก wait_for)
    คืน   : (done, pending) เป็น "set ของ Task" 2 ก้อน
            done    = ตัวที่จบแล้ว → ต้องเรียก .result() เองถึงได้ค่า
            pending = ตัวที่ยังรันอยู่ → wait "ไม่ยกเลิกให้" ต้อง cancel เอง

gather vs wait
    gather → ได้ "ค่าผลลัพธ์" เป็น list เรียงลำดับ · รอทุกตัว
    wait   → ได้ "Task" เป็น set · เลือกได้ว่ารอแค่ไหน · เหมาะกับการแข่งกัน

รัน:  python 08_wait.py
"""
import asyncio
import time

_start = time.perf_counter()


def reset_clock():
    global _start
    _start = time.perf_counter()


def log(msg):
    print(f"[{time.perf_counter() - _start:4.2f}s] {msg}")


async def fetch_price(server, seconds, fail=False):
    await asyncio.sleep(seconds)
    if fail:
        raise ValueError(f"{server} ล่ม")
    return f"[{server}] 150 USD"


async def cleanup(pending):
    # ยกเลิกตัวที่เหลือ แล้วรอให้มันรับรู้การยกเลิกจริง ๆ (กันคำเตือนตอนปิดโปรแกรม)
    for t in pending:
        t.cancel()
    await asyncio.gather(*pending, return_exceptions=True)


async def main():
    print("=== 1) FIRST_COMPLETED: เอาเซิร์ฟเวอร์ที่ตอบเร็วสุด ===")
    reset_clock()
    tasks = {
        asyncio.create_task(fetch_price("Alpha", 3.0), name="Alpha"),
        asyncio.create_task(fetch_price("Beta", 0.8), name="Beta"),
        asyncio.create_task(fetch_price("Gamma", 1.5), name="Gamma"),
    }
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    log(f"done {len(done)} ตัว, pending {len(pending)} ตัว")
    winner = done.pop()                         # done เป็น set → ใช้ pop() หรือ list(done)[0]
    log(f"ผู้ชนะ: {winner.get_name()} → {winner.result()}")
    await cleanup(pending)
    log(f"ยกเลิก {[t.get_name() for t in pending]} แล้ว")

    print("\n=== 2) FIRST_EXCEPTION (โจทย์ Practice_Midterm/Test.py) ===")
    reset_clock()
    tasks = [
        asyncio.create_task(fetch_price("S1", 1)),
        asyncio.create_task(fetch_price("S2", 2, fail=True)),
        asyncio.create_task(fetch_price("S3", 3)),
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
    log(f"Done: {len(done)}, Pending: {len(pending)}   ← S1 จบที่ 1 s, S2 error ที่ 2 s")
    for t in done:
        if t.exception():
            log(f"   error: {t.exception()}")
        else:
            log(f"   ok: {t.result()}")
    await cleanup(pending)

    print("\n=== 3) ALL_COMPLETED + timeout: หมดเวลาไม่ raise แค่ได้ของเท่าที่เสร็จ ===")
    reset_clock()
    tasks = [
        asyncio.create_task(fetch_price("Fast", 0.3)),
        asyncio.create_task(fetch_price("Slow", 5.0)),
    ]
    done, pending = await asyncio.wait(tasks, timeout=1.0)
    log(f"ครบ 1 s: done {len(done)} ตัว, pending {len(pending)} ตัว (ไม่มี TimeoutError)")
    await cleanup(pending)


if __name__ == "__main__":
    asyncio.run(main())

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • ส่ง Task (create_task แล้ว) ไม่ใช่ coroutine ดิบ
# • ได้ set ของ Task → .result() เอง · ใช้ done.pop() หรือ list(done)[0] ห้าม done[0]
# • pending ไม่ถูกยกเลิกให้ → for t in pending: t.cancel()
# • FIRST_EXCEPTION ถ้าไม่มี error เลย = รอทั้งหมด
# • wait(timeout=) ไม่ raise · wait_for(timeout=) raise TimeoutError
