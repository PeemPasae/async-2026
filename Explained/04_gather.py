"""
04 · asyncio.gather
อ้างอิงงานในคลาส: Week3/task_07_gather.py, Week4/foodcourt_02_gather.py, WX/web.py

results = await asyncio.gather(aw1, aw2, aw3, ..., return_exceptions=False)
    รับ   : coroutine หรือ task กี่ตัวก็ได้ "แยกเป็นอาร์กิวเมนต์"
            ถ้ามีใน list ต้องแตกด้วย *  →  asyncio.gather(*my_list)
            coroutine ที่ส่งเข้าไปจะถูกห่อเป็น task ให้อัตโนมัติ
    ทำ    : รันทุกตัวพร้อมกัน แล้วรอจน "ทุกตัว" เสร็จ
    คืน   : list ของผลลัพธ์ "เรียงตามลำดับที่ส่งเข้าไป" (ไม่ใช่ลำดับที่เสร็จ)

return_exceptions=False (ค่าเริ่มต้น)
    ถ้ามีตัวไหน error → gather raise error นั้นทันที
    ตัวอื่น "ไม่ถูกยกเลิก" ยังรันต่อเบื้องหลัง แต่เราไม่ได้ผลของมัน
return_exceptions=True
    ไม่ raise — error จะกลายเป็น "ค่า" อยู่ใน list ตรงตำแหน่งนั้น

รัน:  python 04_gather.py
"""
import asyncio
import time

_start = time.perf_counter()


def reset_clock():
    global _start
    _start = time.perf_counter()


def log(msg):
    print(f"[{time.perf_counter() - _start:4.2f}s] {msg}")


async def fetch(name, seconds, fail=False):
    log(f"   {name}: เริ่ม")
    await asyncio.sleep(seconds)
    if fail:
        log(f"   {name}: พัง!")
        raise ValueError(f"{name} ล้มเหลว")
    log(f"   {name}: เสร็จ")
    return f"data-{name}"


async def main():
    print("=== 1) ผลเรียงตามลำดับที่ส่งเข้า ไม่ใช่ลำดับที่เสร็จ · เวลารวม = ตัวช้าสุด ===")
    reset_clock()
    results = await asyncio.gather(
        fetch("Users", 1.0),
        fetch("Products", 0.5),        # เสร็จก่อน แต่ยังอยู่ตำแหน่งที่ 2
        fetch("Invoices", 0.8),
    )
    log(f"results = {results}")        # ['data-Users', 'data-Products', 'data-Invoices'] ที่ 1.00s

    print("\n=== 2) มีงานใน list → ต้องใช้ * แตกออก ===")
    reset_clock()
    names = ["A", "B", "C"]
    coros = [fetch(n, 0.3) for n in names]
    results = await asyncio.gather(*coros)      # ถ้าลืม * จะ error: list ไม่ใช่ awaitable
    log(f"results = {results}")
    # แตกผลใส่ตัวแปรได้เลยถ้ารู้จำนวน:  a, b, c = await asyncio.gather(...)

    print("\n=== 3) มี error และไม่ใส่ return_exceptions ===")
    reset_clock()
    try:
        await asyncio.gather(fetch("OK", 1.0), fetch("BAD", 0.3, fail=True))
    except ValueError as e:
        log(f"gather raise: {e}   ← ออกมาที่ 0.30s ไม่รอ OK")
    await asyncio.sleep(0.9)
    log("สังเกตว่า 'OK: เสร็จ' ยังโผล่มา — ตัวอื่นไม่ได้ถูกยกเลิก")

    print("\n=== 4) return_exceptions=True → error กลายเป็นค่าใน list ===")
    reset_clock()
    results = await asyncio.gather(
        fetch("X", 0.5),
        fetch("Y", 0.3, fail=True),
        return_exceptions=True,
    )
    log(f"results = {results!r}")
    for r in results:
        if isinstance(r, Exception):
            log(f"   พบ error ชนิด {type(r).__name__}: {r}")
        else:
            log(f"   ได้ค่า {r}")


if __name__ == "__main__":
    asyncio.run(main())

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • gather = รอ "ทุกตัว" เสร็จ แล้วได้ list เรียงตามลำดับที่ส่ง
# • อย่าลืม * เมื่อส่ง list
# • อยากให้งานหนึ่งพังแล้วงานอื่นยังได้ผล → return_exceptions=True
# • อยากได้แค่ตัวแรกที่เสร็จ → ไม่ใช่ gather ใช้ asyncio.wait (ไฟล์ 08)
