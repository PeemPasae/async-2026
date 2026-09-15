"""
01 · def กับ async def · coroutine object · asyncio.run
อ้างอิงงานในคลาส: Week2/asyncio01.py – asyncio03.py

┌──────────────────────┬──────────────────────────────────────────────────────┐
│ เขียนแบบนี้           │ เกิดอะไรขึ้น                                           │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ def f(): ...         │ เรียก f() แล้ว "รันทันที" ได้ค่าที่ return กลับมาเลย      │
│ async def g(): ...   │ เรียก g() แล้ว "ยังไม่รัน" ได้ coroutine object กลับมา  │
│                      │ (คิดว่าเป็น "ใบสั่งงาน" ที่ยังไม่มีใครหยิบไปทำ)            │
│ asyncio.run(g())     │ เปิด event loop → รันใบสั่งงานจนจบ → คืนค่าที่ return    │
│                      │ → ปิด loop  (ใช้ครั้งเดียวที่จุดเริ่มโปรแกรม)             │
└──────────────────────┴──────────────────────────────────────────────────────┘

รัน:  python 01_def_vs_async_def.py   แล้วอ่านผลเทียบกับคอมเมนต์ทีละข้อ
"""
import asyncio


def normal_add(a, b):
    print("   (normal_add กำลังทำงาน)")
    return a + b


async def async_add(a, b):
    print("   (async_add กำลังทำงาน)")
    return a + b


def main():
    print("1) เรียกฟังก์ชัน def ธรรมดา")
    result = normal_add(1, 2)          # รันทันที → เห็นข้อความ "กำลังทำงาน"
    print("   ได้ค่า:", result)          # 3

    print("\n2) เรียกฟังก์ชัน async def แบบเดียวกันเป๊ะ")
    coro = async_add(1, 2)             # ไม่เห็น "กำลังทำงาน" เพราะโค้ดข้างในยังไม่ถูกรัน
    print("   ได้ค่า:", coro)            # <coroutine object async_add at 0x...>
    print("   type(coro)      =", type(coro))       # <class 'coroutine'>
    print("   type(async_add) =", type(async_add))  # <class 'function'>  ← ตัวฟังก์ชันยังเป็น function

    print("\n3) ส่ง coroutine ให้ asyncio.run")
    result = asyncio.run(coro)         # ตอนนี้ถึงเห็น "กำลังทำงาน"
    print("   ได้ค่า:", result)          # 3  ← ค่าที่ return ออกมาจาก asyncio.run

    print("\n4) coroutine object ใช้ได้ครั้งเดียว")
    try:
        asyncio.run(coro)              # ใบสั่งงานใบเดิมถูกทำไปแล้ว
    except RuntimeError as e:
        print("   RuntimeError:", e)    # cannot reuse already awaited coroutine
    print("   → ถ้าจะรันใหม่ ต้องเรียก async_add(1, 2) ใหม่เพื่อสร้างใบสั่งงานใบใหม่")


if __name__ == "__main__":
    main()

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • async def ทำให้ฟังก์ชัน "คืน coroutine" แทนการรันทันที
# • coroutine จะรันได้ 3 ทาง: asyncio.run(...) · await ... · asyncio.create_task(...)
# • asyncio.run ใช้ครั้งเดียวที่ระดับบนสุด (ห้ามเรียกซ้อนข้างใน async def)
# • ในข้อสอบ: เห็น f() ของ async def โดยไม่มี await / run / create_task → "ไม่รัน"
