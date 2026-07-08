# Delivery System): นักศึกษาต้องเขียน try...except CancelledError ได้ถูกต้อง 
# และใช้ .get_name(), .cancel(), และ .cancelled() ได้
import asyncio
from datetime import datetime


def log(message: str) -> None:
    """พิมพ์ข้อความพร้อมวันที่และเวลาปัจจุบัน รูปแบบ 'Wed Jul  8 10:37:49 2026'"""
    now = datetime.now().strftime("%a %b %e %H:%M:%S %Y")
    print(f"{now} {message}")


async def delivery_task(package_id: str, duration: float) -> str:
    """
    จำลองการส่งพัสดุของพนักงาน 1 คน
    - พิมพ์ข้อความเมื่อเริ่มส่ง
    - รอ (จำลองการเดินทาง) ด้วย asyncio.sleep(duration)
    - เมื่อส่งเสร็จ ให้ return ข้อความยืนยันการส่งสำเร็จ
    - หากถูกยกเลิกระหว่างทาง ให้ดักจับ asyncio.CancelledError
      เพื่อพิมพ์ข้อความแจ้งเตือนและส่งพัสดุกลับคลัง
    """
    log(f"[START] Package {package_id}: Delivery started, ETA {duration} seconds...")
    try:
        await asyncio.sleep(duration)
    except asyncio.CancelledError:
        log("Delivery Canceled! Returning package to warehouse.")
        # ต้อง re-raise ต่อ เพื่อให้ Task เปลี่ยนสถานะเป็น cancelled() == True อย่างถูกต้อง
        raise

    log(f"[DONE] Package {package_id}: Delivery finished.")
    return f"Package {package_id} Delivered!"


async def main():
    # 2) สร้าง Task จาก delivery_task โดยตั้งชื่อ Task ว่า "Express-Courier"
    task = asyncio.create_task(
        delivery_task(package_id="P001", duration=5.0),
        name="Express-Courier",
    )

    # 3) ระหว่างที่พัสดุกำลังเดินทาง ให้รอผ่านไป 2 วินาที แล้วตรวจสอบสถานะ
    await asyncio.sleep(2)
    log(f"[CHECK] Current task name: {task.get_name()}")
    log(f"[CHECK] Is task done? {task.done()}")

    # 4) หากผ่านไป 2 วินาทีแล้วยังไม่เสร็จ (duration=5.0 > 2 วินาที) ให้ยกเลิกงานทันที
    if not task.done():
        log("[ACTION] Delivery is taking too long. Cancelling task...")
        task.cancel()

    # ต้อง await task เพื่อให้ CancelledError ถูกส่งเข้าไปประมวลผลจนจบ
    try:
        result = await task
        log(f"[RESULT] {result}")
    except asyncio.CancelledError:
        log("[MAIN] Caught CancelledError in main().")

    # 5) ตรวจสอบสถานะภายนอกของ Task ว่าถูกยกเลิกจริงหรือไม่
    log(f"[VERIFY] task.cancelled() == {task.cancelled()}")


if __name__ == "__main__":
    asyncio.run(main())