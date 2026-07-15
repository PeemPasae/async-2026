import asyncio
import aiohttp

BASE_URL = "http://172.16.2.117:8088"

# ลำดับรหัสนักศึกษาตามตำแหน่งบนจอ Monitor (เรียงแถวบนลงล่าง, ซ้ายไปขวา ตามรูปที่ส่งมา)
STUDENT_GRID = [
    ["6710301001", "6710301003", "6710301004", "6710301005", "6710301006", "6710301007", "6710301008"],
    ["6710301009", "6710301010", "6710301011", "6710301012", "6710301017", "6710301018", "6710301019"],
    ["6710301020", "6710301021", "6710301022", "6710301023", "6710301024", "6710301025", "6710301027"],
    ["6710301030", "6710301031", "6710301032", "6710301033", "6710301034", "6710301036", "6710301037"],
    ["6710301041", "6710301042", "6710301043", "6710301045", "6710301047", "6710301048", "6710301049"],
    ["6710301051", "6710301054", "6720301001", "6720301002", "6720301003", "6720301004", None],
]

# แพทเทิร์นรูปหัวใจ (1 = ติดไฟ, 0 = ดับ) ขนาด 6 แถว x 7 คอลัมน์ ให้ตรงกับ STUDENT_GRID
HEART_PATTERN = [
    [0, 1, 1, 0, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
]

LIGHTS = ["light_1", "light_2", "light_3", "light_4"]


async def reset_student(session, student_id):
    url = f"{BASE_URL}/api/{student_id}/lights/reset"
    try:
        async with session.delete(url) as resp:
            await resp.json()
    except Exception as e:
        print(f"❌ reset {student_id} ผิดพลาด: {e}")


async def set_light(session, student_id, light_id, status):
    url = f"{BASE_URL}/api/{student_id}/lights/{light_id}"
    try:
        async with session.post(url, json={"status": status}) as resp:
            await resp.json()
    except Exception as e:
        print(f"❌ {student_id}/{light_id} ผิดพลาด: {e}")


async def turn_on_student(session, student_id):
    # เปิดไฟทั้ง 4 ดวงของนักศึกษาคนนี้พร้อมกัน (1 คน = 1 pixel)
    await asyncio.gather(*[set_light(session, student_id, l, "ON") for l in LIGHTS])


async def main():
    all_ids = [sid for row in STUDENT_GRID for sid in row if sid is not None]
    heart_ids = [
        STUDENT_GRID[r][c]
        for r in range(len(STUDENT_GRID))
        for c in range(len(STUDENT_GRID[r]))
        if STUDENT_GRID[r][c] is not None and HEART_PATTERN[r][c] == 1
    ]

    async with aiohttp.ClientSession() as session:
        # 1) ดับไฟทุกคนก่อน
        print("🔻 กำลังดับไฟทั้งหมด...")
        await asyncio.gather(*[reset_student(session, sid) for sid in all_ids])

        # 2) เปิดเฉพาะตำแหน่งที่เป็นรูปหัวใจ
        print("❤️ กำลังวาดรูปหัวใจ...")
        await asyncio.gather(*[turn_on_student(session, sid) for sid in heart_ids])

        print(f"✅ เสร็จแล้ว! เปิดไฟ {len(heart_ids)} คน จากทั้งหมด {len(all_ids)} คน")


asyncio.run(main())