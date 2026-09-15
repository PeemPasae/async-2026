"""
12 · httpx.AsyncClient (เรียก HTTP API แบบ async)
อ้างอิงงานในคลาส: Week3/stock_price_httpx.py, Week4/food_utils.py, Week6/robots.py, WX/web.py

ไฟล์นี้ใช้เซิร์ฟเวอร์จำลอง (MockTransport) จึงรันได้โดยไม่ต้องต่อเน็ต
ของจริงแค่ตัด transport=... ออก แล้วใส่ URL จริง

async with httpx.AsyncClient(base_url=..., timeout=10.0) as client:
    - เปิด connection pool ครั้งเดียว ใช้ยิงได้หลาย request · ออกจาก with แล้วปิดให้เอง
    - base_url: เขียน path สั้น ๆ ได้ เช่น client.get("/price/beta")
    - timeout: เวลาสูงสุดต่อ request (เกิน → httpx.TimeoutException)

response = await client.get(url, params={...})
response = await client.post(url, json={...})      ← json= จะแปลง dict เป็น JSON และตั้ง header ให้
    response.status_code   เช่น 200, 404
    response.json()        แปลง body เป็น dict   ← httpx ไม่ต้อง await
    response.text          body แบบข้อความ
    response.raise_for_status()   ถ้า 4xx/5xx → raise httpx.HTTPStatusError

error ที่ควรรู้
    httpx.HTTPStatusError   ได้คำตอบแต่ status เป็น 4xx/5xx (มาจาก raise_for_status)
    httpx.RequestError      ต่อไม่ติด / timeout (TimeoutException เป็นลูกของมัน)
    httpx.HTTPError         แม่ของทั้งสองตัว → except httpx.HTTPError จับได้ครบ

เทียบ aiohttp (Week4/light):
    async with aiohttp.ClientSession() as s:
        async with s.post(url, json=...) as resp:
            data = await resp.json()        ← aiohttp ต้อง await .json()

ห้ามใช้ requests ใน async def เพราะมันบล็อก event loop

รัน:  python 12_httpx_client.py
"""
import asyncio
import json
import time

import httpx


# ----------------------------------------------------------------- เซิร์ฟเวอร์จำลอง
LATENCY = {"alpha": 1.0, "beta": 0.3, "gamma": 0.6}


async def fake_server(request: httpx.Request):
    path = request.url.path
    if request.method == "GET" and path.startswith("/price/"):
        name = path.split("/")[-1]
        if name not in LATENCY:
            return httpx.Response(404, json={"detail": "server not found"})
        await asyncio.sleep(LATENCY[name])
        currency = request.url.params.get("currency", "USD")
        return httpx.Response(200, json={"server": name, "price": 150, "currency": currency})
    if request.method == "POST" and path == "/order":
        body = json.loads(request.content)
        return httpx.Response(200, json={"status": "READY", "menu": body["menu"]})
    return httpx.Response(404, json={"detail": "not found"})


def make_client():
    return httpx.AsyncClient(base_url="http://api.test", timeout=10.0,
                             transport=httpx.MockTransport(fake_server))


# ----------------------------------------------------------------- ตัวอย่างการใช้
async def get_price(client, server):
    r = await client.get(f"/price/{server}", params={"currency": "THB"})   # → /price/beta?currency=THB
    r.raise_for_status()
    return r.json()


async def main():
    async with make_client() as client:
        print("=== 1) GET + params + json() ===")
        r = await client.get("/price/beta", params={"currency": "THB"})
        print("   status_code :", r.status_code)
        print("   json()      :", r.json())

        print("\n=== 2) POST ส่ง JSON body ===")
        r = await client.post("/order", json={"student_id": "6710301005", "menu": "สเต็ก"})
        print("   json()      :", r.json())

        print("\n=== 3) raise_for_status() เมื่อได้ 404 ===")
        r = await client.get("/price/omega")
        print("   status_code :", r.status_code)
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            print("   HTTPStatusError:", e.response.status_code, e.response.json())

        print("\n=== 4) ใช้ client ตัวเดียว ยิงหลาย request พร้อมกันด้วย gather ===")
        start = time.perf_counter()
        results = await asyncio.gather(*(get_price(client, s) for s in ["alpha", "beta", "gamma"]))
        print(f"   ได้ {len(results)} ผล ใน {time.perf_counter() - start:.2f} s (ตัวช้าสุด 1.0 s)")

        print("\n=== 5) จำกัดเวลาเองด้วย wait_for + รวบ error ด้วย httpx.HTTPError ===")

        async def safe_price(server, limit):
            try:
                data = await asyncio.wait_for(get_price(client, server), timeout=limit)
                return f"{server}: {data['price']} {data['currency']}"
            except asyncio.TimeoutError:
                return f"{server}: ช้าเกิน {limit} s"
            except httpx.HTTPError as e:
                return f"{server}: error {type(e).__name__}"

        print("  ", await asyncio.gather(safe_price("beta", 0.5),
                                          safe_price("alpha", 0.5),
                                          safe_price("omega", 0.5)))


if __name__ == "__main__":
    asyncio.run(main())

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • async with httpx.AsyncClient() as client: เปิดครั้งเดียว ส่ง client ให้ทุก task
# • await client.get/post(...) · r.json() ไม่ต้อง await (aiohttp ต้อง await)
# • r.raise_for_status() เปลี่ยน 4xx/5xx เป็น exception
# • ยิงหลายตัวพร้อมกัน = gather ของฟังก์ชันที่ใช้ client เดียวกัน
