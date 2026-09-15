"""
ขั้น 19 / 20 · FastAPI: สร้าง API ร้านอาหารเอง
ความยาก ●●●●○    อ้างอิง: Week5/fastapi_basic_lab.py, Week4/foodcourt_api.py, Week7/server.py

ต้องติดตั้งก่อน:  pip install fastapi
ตัวตรวจจะยิง request เข้า app โดยตรง ไม่ต้องรัน uvicorn
(ถ้าอยากเปิดดูใน browser:  uvicorn 19_fastapi_foodcourt:app --reload  ใช้ไม่ได้เพราะชื่อไฟล์ขึ้นต้นด้วยตัวเลข
 ให้ copy ไปไฟล์ชื่อ foodcourt.py แล้ว  uvicorn foodcourt:app --reload  → http://127.0.0.1:8000/docs)

โจทย์
-----
1) GET /menu/{shop}?qty=1
       คืน {"shop": shop, "qty": qty, "total": PRICES[shop] * qty}
       qty ไม่ส่งมา = 1  ·  ร้านที่ไม่มีใน PRICES → 404

2) POST /order    JSON {"student_id": "...", "shop": "..."}
       ใช้ Pydantic BaseModel รับ body (ขาด field → FastAPI ตอบ 422 ให้เอง)
       ร้านไม่มี → 404
       รอ COOK_TIME[shop] วินาทีแบบไม่บล็อก แล้วคืน
       {"student_id": ..., "shop": ..., "status": "READY"}

3) POST /claim    JSON {"student_id": "..."}
       มีคูปอง TOTAL_COUPONS ใบ คนละไม่เกิน 1 ใบ
       คืน {"status": "SUCCESS"} / {"status": "LIMIT"} / {"status": "SOLD_OUT"}
       ต้องมี await asyncio.sleep(0.05) ก่อนตัดคูปอง และยิงพร้อมกันต้องไม่แจกเกิน

คำใบ้
    @app.get("/menu/{shop}")
    async def menu(shop: str, qty: int = 1): ...
    raise HTTPException(status_code=404, detail="shop not found")
    coupon_lock = asyncio.Lock()  +  global ตัวนับคูปอง

รัน:  python 19_fastapi_foodcourt.py
"""
import asyncio
import sys

from _check import check

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:
    sys.exit("ขั้นนี้ต้องติดตั้ง FastAPI ก่อน:  pip install fastapi")

# ---- ให้มา (ห้ามแก้) ----
PRICES = {"chicken": 50, "noodle": 45, "steak": 159}
COOK_TIME = {"chicken": 0.1, "noodle": 0.2, "steak": 0.3}
TOTAL_COUPONS = 3

app = FastAPI(title="Practice Food Court")

# ---- เขียนโค้ดตรงนี้ ----


if __name__ == "__main__":
    check(19, globals())
