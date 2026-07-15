import asyncio
import aiohttp

STUDENT_ID = "6710301005"
BASE_URL = "http://172.16.2.117:8088"

async def set_light(session, light_id, status):
    url = f"{BASE_URL}/api/{STUDENT_ID}/lights/{light_id}"
    async with session.post(url, json={"status": status}) as resp:
        data = await resp.json()
        print(f"{light_id} -> {data['current_status']}")

async def reset_all(session):
    url = f"{BASE_URL}/api/{STUDENT_ID}/lights/reset"
    async with session.delete(url) as resp:
        data = await resp.json()
        print(data["message"])

async def main():
    lights = ["light_1", "light_2", "light_3", "light_4"]

    async with aiohttp.ClientSession() as session:
        while True:  # วนซ้ำไปเรื่อยๆ
            # เปิดไล่ทีละดวง 1 -> 2 -> 3 -> 4
            for light_id in lights:
                await set_light(session, light_id, "ON")

            # เมื่อเปิดครบทั้ง 4 ดวงแล้ว ปิดทั้งหมดพร้อมกัน
            await reset_all(session)

asyncio.run(main())