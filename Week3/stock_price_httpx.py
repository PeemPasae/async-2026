# stock_price_httpx.py (เวอร์ชันสำหรับแจกเป็นโจทย์หรือแนวทางให้นักเรียนเขียน)
import asyncio
import httpx  
from time import ctime

async def fetch_stock_price(server_name: str):
    """
    TODO: Assignment 3 - เขียนฟังก์ชันเชื่อมต่อ Mock Server ผ่านระบบเครือข่าย
    1. กำหนดเป้าหมายไปที่พอร์ต 8088 ตามสเปกเซิร์ฟเวอร์ของอาจารย์
    2. ใช้ httpx.AsyncClient() ดึงข้อมูลเพื่อไม่ให้เกิดการ Block สัญญาณ Event Loop
    3. นำข้อมูล JSON (server และ price_usd) มาจัดฟอร์แมตแสดงผล
    """
    url = f"http://127.0.0.1:8088/price/{server_name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        return f"[{data['server']}] Price: {data['price_usd']} USD"

async def main():
    """
    จัดการส่งกลุ่ม Tasks ทำ Concurrency Racing บนเซิร์ฟเวอร์ย่อย Alpha, Beta, Gamma
    และปิดกั้นทรัพยากรตัวที่ค้างคา (pending) ทิ้งทันทีเมื่อมีผู้ชนะ
    """
    # 1) แปลงคอรูทีนดึงข้อมูลของทั้ง 3 สาขาให้เป็น asyncio.Task
    #    เพื่อส่งเข้าคิวรันพร้อมกันใน Event Loop
    tasks = {
        asyncio.create_task(fetch_stock_price("alpha"), name="Alpha"),
        asyncio.create_task(fetch_stock_price("beta"), name="Beta"),
        asyncio.create_task(fetch_stock_price("gamma"), name="Gamma"),
    }
 
    # 2) ใช้ asyncio.wait() กับ return_when=FIRST_COMPLETED เพื่อดีดตัวหลุด
    #    จากการรอทันทีที่มีเซิร์ฟเวอร์ตัวแรกตอบกลับสำเร็จ
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
 
    # 3) ดึงผลลัพธ์จากเซิร์ฟเวอร์ที่ชนะการแข่งขัน (ตัวที่เร็วที่สุด) มาพิมพ์แสดง
    winner_task = done.pop()
    print(f"{ctime()} [WINNER] Task '{winner_task.get_name()}' won the race -> {winner_task.result()}")
 
    # 4) [Anti-Memory Leak] วนลูปดึงงานที่ยังค้างอยู่ใน pending มายกเลิกทิ้งให้หมด
    #    เพื่อตัดสัญญาณ Network Request ที่ยังวิ่งค้างอยู่บนระบบเครือข่าย
    for task in pending:
        task.cancel()
 
    # รอให้การยกเลิกเสร็จสมบูรณ์ เพื่อกัน warning "Task was destroyed
    # but it is pending" และเก็บ exception จากการ cancel ไว้เฉยๆ
    await asyncio.gather(*pending, return_exceptions=True)
 
    for task in pending:
        print(f"{ctime()} [VERIFY] Task '{task.get_name()}' cancelled() == {task.cancelled()}")
 
if __name__ == "__main__":
    asyncio.run(main())