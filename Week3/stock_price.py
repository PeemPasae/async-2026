# นักเรียนต้องเลือกใช้ asyncio.wait() พร้อมออปชัน return_when=asyncio.FIRST_COMPLETED เท่านั้น (หากใครใช้ gather หรือ wait_for จะไม่ตรงสเปกเงื่อนไขการแข่งส่งข้อมูล)
import asyncio
from datetime import datetime


def log(message: str) -> None:
    """พิมพ์ข้อความพร้อมวันที่และเวลาปัจจุบัน รูปแบบ 'Wed Jul  8 10:37:49 2026'"""
    now = datetime.now().strftime("%a %b %e %H:%M:%S %Y")
    print(f"{now} {message}")


async def fetch_stock_price(server_name: str, delay: float) -> str:
    """
    จำลองการดึงราคาหุ้นจากเซิร์ฟเวอร์แต่ละสาขา
    - ใช้ asyncio.sleep(delay) แทนความหน่วงของเครือข่ายจริง
    - ส่งค่ากลับเป็นข้อความราคาหุ้นเมื่อดึงข้อมูลสำเร็จ
    """
    log(f"[REQUEST] Fetching price from [{server_name}] (expected delay: {delay}s)...")
    await asyncio.sleep(delay)
    result = f"[{server_name}] Price: 150 USD"
    log(f"[RESPONSE] {result}")
    return result


async def main():
    # 1) แตก Task ขึ้นมา 3 ตัวพร้อมกันใน Event Loop
    tasks = {
        asyncio.create_task(fetch_stock_price("Alpha", 3.0), name="Alpha"),
        asyncio.create_task(fetch_stock_price("Beta", 0.8), name="Beta"),
        asyncio.create_task(fetch_stock_price("Gamma", 1.5), name="Gamma"),
    }

    # 2) ใช้ asyncio.wait() กับ return_when=FIRST_COMPLETED
    #    เพราะต้องการ "ดีดตัวหลุด" ทันทีที่มีตัวแรกเสร็จ โดยยังต้อง
    #    เก็บ pending set ไว้เพื่อนำไป .cancel() ต่อ (asyncio.gather()
    #    ไม่รองรับการหยุดรอกลางคันแบบนี้ จึงไม่เหมาะกับโจทย์ข้อนี้)
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    # 3) แสดงผลลัพธ์ของเซิร์ฟเวอร์ที่ชนะการแข่งขัน (ตัวที่เร็วที่สุด)
    winner_task = done.pop()
    winner_result = winner_task.result()
    log(f"[WINNER] Task '{winner_task.get_name()}' won the race -> {winner_result}")

    # 4) [Anti-Memory Leak] วนลูปยกเลิกงานที่ยังค้างอยู่ใน pending ให้หมด
    log(f"[CLEANUP] Cancelling {len(pending)} pending task(s): "
        f"{[t.get_name() for t in pending]}")
    for task in pending:
        task.cancel()

    # รอให้การยกเลิกเสร็จสมบูรณ์ (กันไม่ให้เกิด warning "Task was destroyed
    # but it is pending") พร้อมเก็บ exception จากการ cancel ไว้เฉยๆ
    await asyncio.gather(*pending, return_exceptions=True)

    for task in pending:
        log(f"[VERIFY] Task '{task.get_name()}' cancelled() == {task.cancelled()}")


if __name__ == "__main__":
    asyncio.run(main())