"""
13 · FastAPI: route, path/query/body, HTTPException, async def, WebSocket
อ้างอิงงานในคลาส: Week5/fastapi_basic_lab.py, fastapi_async_basic_lab.py, chat-hello/main.py,
                 Week4/foodcourt_api.py, Week7/server.py

ต้องมี:  pip install fastapi
ไฟล์นี้ "ยิงทดสอบ" app เองโดยไม่ต้องเปิด uvicorn · ของจริงรันด้วย  uvicorn ชื่อไฟล์:app --reload

┌──────────────────────────────────────────┬──────────────────────────────────────────────┐
│ @app.get("/path") / .post / .delete       │ ผูกฟังก์ชันกับ method + URL                       │
│ "/items/{item_id}"  +  item_id: int       │ path parameter · แปลงชนิดให้ ("5" → 5)          │
│                                          │ แปลงไม่ได้ ("abc") → 422 อัตโนมัติ                │
│ def f(q: str, age: int = 18)             │ พารามิเตอร์ที่ไม่อยู่ใน path = query ?q=..&age=.. │
│                                          │ มีค่าเริ่มต้น = ไม่บังคับส่ง                        │
│ class Order(BaseModel): ...  +  o: Order │ JSON body · field ขาด/ชนิดผิด → 422              │
│ raise HTTPException(404, detail="...")   │ ตอบ error พร้อม status code                      │
│ return dict                              │ แปลงเป็น JSON ให้ (status 200)                    │
│ async def + await asyncio.sleep          │ ไม่บล็อก รับ request อื่นระหว่างรอได้                │
│ def + time.sleep                         │ FastAPI ย้ายไปรันใน thread pool (ใช้ได้แต่เปลือง) │
│ async def + time.sleep                   │ ✘ บล็อก event loop ทั้งเซิร์ฟเวอร์                  │
│ @app.websocket("/ws/{id}")               │ เปิดท่อค้างไว้ส่งข้อมูลสองทาง                        │
└──────────────────────────────────────────┴──────────────────────────────────────────────┘

รัน:  python 13_fastapi.py
"""
import asyncio
import sys
import time

try:
    import httpx
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.testclient import TestClient
    from pydantic import BaseModel
except ImportError:
    sys.exit("ไฟล์นี้ต้องติดตั้งก่อน:  pip install fastapi httpx")

app = FastAPI(title="Explained Food Court")

KITCHEN_LATENCY = {"chicken": 0.8, "noodle": 1.5, "steak": 4.0}


# 1) GET ธรรมดา ─────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "server alive"}          # dict → JSON


# 2) path parameter + แปลงชนิด ─────────────────────────────────────────────────
@app.get("/items/{item_id}")
async def read_item(item_id: int):              # "/items/21" → item_id = 21 (int)
    return {"item_id": item_id, "doubled": item_id * 2}


# 3) query parameter ────────────────────────────────────────────────────────
@app.get("/users")
async def search_users(username: str, age: int = 18):   # /users?username=Alice&age=21
    return {"username": username, "age": age}


# 4) JSON body ด้วย Pydantic + HTTPException + async sleep ────────────────────────
class OrderModel(BaseModel):
    student_id: str
    menu_name: str


@app.post("/order/{shop_name}")
async def cook_food(shop_name: str, order: OrderModel):  # shop_name จาก path, order จาก body
    if shop_name not in KITCHEN_LATENCY:
        raise HTTPException(status_code=404, detail="Shop not found")
    await asyncio.sleep(KITCHEN_LATENCY[shop_name] / 4)   # หาร 4 ให้ตัวอย่างรันเร็ว
    return {"status": "READY_FOR_PICKUP", "shop": shop_name,
            "student_id": order.student_id, "menu": order.menu_name}


# 5) WebSocket + ConnectionManager (Week5/chat-hello) ─────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, student_id: str, ws: WebSocket):
        await ws.accept()                        # ต้อง accept ก่อนส่ง/รับอะไรทั้งนั้น
        self.active[student_id] = ws

    def disconnect(self, student_id: str):
        self.active.pop(student_id, None)

    async def broadcast(self, message: str):
        for ws in list(self.active.values()):    # list(...) กัน dict เปลี่ยนระหว่างวน
            await ws.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{student_id}")
async def websocket_endpoint(websocket: WebSocket, student_id: str):
    await manager.connect(student_id, websocket)
    await manager.broadcast(f"[System] {student_id} เข้าห้อง")
    try:
        while True:
            text = await websocket.receive_text()         # รอข้อความจาก client
            await manager.broadcast(f"[{student_id}] {text}")
    except WebSocketDisconnect:                           # client ปิดการเชื่อมต่อ
        manager.disconnect(student_id)


# ───────────────────────────────────────────────── ยิงทดสอบ (ไม่ใช่ส่วนของเซิร์ฟเวอร์)
async def try_http():
    transport = httpx.ASGITransport(app=app)             # ส่ง request เข้า app ตรง ๆ
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        async def show(label, resp):
            print(f"   {label:<38} → {resp.status_code} {resp.json()}")

        print("=== HTTP ===")
        await show("GET /", await c.get("/"))
        await show("GET /items/21", await c.get("/items/21"))
        r = await c.get("/items/abc")
        print(f"   {'GET /items/abc':<38} → {r.status_code} (แปลงเป็น int ไม่ได้)")
        await show("GET /users?username=Alice", await c.get("/users", params={"username": "Alice"}))
        r = await c.get("/users")
        print(f"   {'GET /users (ไม่ส่ง username)':<38} → {r.status_code} (ขาด query ที่บังคับ)")
        body = {"student_id": "6710301005", "menu_name": "T-Bone"}
        await show("POST /order/pizza", await c.post("/order/pizza", json=body))
        r = await c.post("/order/steak", json={"student_id": "6710301005"})
        print(f"   {'POST /order/steak (ขาด menu_name)':<38} → {r.status_code} (Pydantic ตรวจ body)")

        print("\n=== async endpoint รับหลาย request พร้อมกัน ===")
        start = time.perf_counter()
        rs = await asyncio.gather(*(c.post(f"/order/{s}", json=body) for s in KITCHEN_LATENCY))
        print(f"   สั่ง 3 ร้านพร้อมกัน ได้ {[r.json()['shop'] for r in rs]} "
              f"ใน {time.perf_counter() - start:.2f} s (ตัวช้าสุด 1.00 s)")


def try_websocket():
    print("\n=== WebSocket ===")
    with TestClient(app) as client:
        with client.websocket_connect("/ws/peem") as ws:
            print("   ได้รับ:", ws.receive_text())         # [System] peem เข้าห้อง
            ws.send_text("สวัสดีทุกคน")
            print("   ได้รับ:", ws.receive_text())         # [peem] สวัสดีทุกคน


if __name__ == "__main__":
    asyncio.run(try_http())
    try_websocket()

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • path param อยู่ใน {} ของ URL · query param คือพารามิเตอร์ที่เหลือ · body ใช้ BaseModel
# • 404 ใช้ HTTPException · 422 FastAPI ตอบให้เองเมื่อข้อมูลผิดรูปแบบ
# • endpoint ที่รอ I/O → async def + await ห้าม time.sleep
# • WebSocket: accept → วน receive → broadcast · จับ WebSocketDisconnect ตอนออก
