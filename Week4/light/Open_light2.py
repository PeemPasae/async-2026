import asyncio
import time
import aiohttp

STUDENT_ID = "6710301005"
BASE_URL = "http://172.16.2.117:8088"   # <-- ใช้ IP และ port นี้แทน 127.0.0.1:8000

async def turn_on_light(session, light_id):
    url = f"{BASE_URL}/api/{STUDENT_ID}/lights/{light_id}"
    async with session.post(url, json={"status": "ON"}) as resp:
        data = await resp.json()
        print(f"{light_id} -> {data['current_status']}")

async def main():
    start_time = time.perf_counter()  # เริ่มจับเวลา

    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            turn_on_light(session, "light_1"),
            turn_on_light(session, "light_2"),
            turn_on_light(session, "light_3"),
            turn_on_light(session, "light_4"),
        )

    end_time = time.perf_counter()  # จบการจับเวลา
    total_time = end_time - start_time
    print(f"\n⏱️ Total time: {total_time:.2f} seconds")

asyncio.run(main())