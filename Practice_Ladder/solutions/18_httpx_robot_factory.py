"""เฉลยขั้น 18"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
import json

import httpx
from _check import check

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


async def reset(client):
    r = await client.post("/reset")
    r.raise_for_status()
    return r.json()


async def grab_part(client, robot, part):
    r = await client.post(f"/robot/{robot}/grab", json={"part": part})
    r.raise_for_status()
    return r.json()


async def run_robot(client, robot):
    got = []
    for part in PARTS:                          # หุ่นตัวเดียว: ทีละชิ้น
        data = await grab_part(client, robot, part)
        got.append(data["part"])
    return got


async def run_factory(robots):
    async with make_client() as client:
        await reset(client)
        results = await asyncio.gather(*(run_robot(client, r) for r in robots))   # หลายตัว: พร้อมกัน
    return dict(zip(robots, results))


if __name__ == "__main__":
    check(18, globals())
