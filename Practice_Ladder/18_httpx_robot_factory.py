"""
ขั้น 18 / 20 · httpx.AsyncClient: โรงงานหุ่นยนต์
ความยาก ●●●●○    อ้างอิง: Week6/robots.py (TODO ที่ยังว่างอยู่), Week4/food_utils.py

ขั้นนี้ไม่ต้องต่อเน็ต — make_client() ให้ client ที่คุยกับเซิร์ฟเวอร์ปลอมในไฟล์นี้
เซิร์ฟเวอร์ปลอมรองรับ
    POST /reset                         -> {"status": "RESET"}
    POST /robot/{robot}/grab  JSON {"part": "A"}
                                        -> รอ 0.1 s -> {"robot": ..., "part": ..., "status": "OK"}

โจทย์
-----
1) async def reset(client)                 POST /reset แล้วคืน JSON
2) async def grab_part(client, robot, part) POST /robot/{robot}/grab พร้อม JSON แล้วคืน JSON
3) async def run_robot(client, robot)      หยิบ PARTS ทีละชิ้นตามลำดับ A → B → C
                                           คืน list ของ "part" จากคำตอบ เช่น ["A", "B", "C"]
4) async def run_factory(robots)           เปิด client ด้วย  async with make_client() as client:
                                           reset 1 ครั้ง แล้วให้หุ่นทุกตัวทำพร้อมกัน
                                           คืน dict {robot: ["A", "B", "C"], ...}

ตัวอย่าง
    await run_factory(["r1", "r2", "r3", "r4"])   ใช้เวลา ≈ 0.3 s (ไม่ใช่ 1.2 s)

คำใบ้
    r = await client.post("/reset")
    r = await client.post(f"/robot/{robot}/grab", json={"part": part})
    r.raise_for_status();  r.json()     ← httpx: .json() ไม่ต้อง await
    dict(zip(robots, results))

รัน:  python 18_httpx_robot_factory.py
"""
import asyncio
import json

import httpx
from _check import check

# ---- ให้มา (ห้ามแก้) ----
PARTS = ["A", "B", "C"]
server_log = []


async def _fake_factory(request: httpx.Request):
    path = request.url.path
    if request.method == "POST" and path == "/reset":
        server_log.append("reset")
        return httpx.Response(200, json={"status": "RESET"})
    parts = path.strip("/").split("/")
    if request.method == "POST" and len(parts) == 3 and parts[0] == "robot" and parts[2] == "grab":
        part = json.loads(request.content)["part"]
        await asyncio.sleep(0.1)
        server_log.append(f"{parts[1]}:{part}")
        return httpx.Response(200, json={"robot": parts[1], "part": part, "status": "OK"})
    return httpx.Response(404, json={"detail": "not found"})


def make_client():
    return httpx.AsyncClient(base_url="http://factory.test",
                             transport=httpx.MockTransport(_fake_factory))


# ---- เขียนโค้ดตรงนี้ ----
async def reset(client):
    raise NotImplementedError


async def grab_part(client, robot, part):
    raise NotImplementedError


async def run_robot(client, robot):
    raise NotImplementedError


async def run_factory(robots):
    raise NotImplementedError


if __name__ == "__main__":
    check(18, globals())
