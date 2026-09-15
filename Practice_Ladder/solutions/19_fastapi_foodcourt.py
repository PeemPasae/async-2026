"""เฉลยขั้น 19"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio

from _check import check

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:
    sys.exit("ขั้นนี้ต้องติดตั้ง FastAPI ก่อน:  pip install fastapi")

PRICES = {"chicken": 50, "noodle": 45, "steak": 159}
COOK_TIME = {"chicken": 0.1, "noodle": 0.2, "steak": 0.3}
TOTAL_COUPONS = 3

app = FastAPI(title="Practice Food Court")

coupon_lock = asyncio.Lock()
coupons_left = TOTAL_COUPONS
claimed = set()


class OrderIn(BaseModel):
    student_id: str
    shop: str


class ClaimIn(BaseModel):
    student_id: str


@app.get("/menu/{shop}")
async def menu(shop: str, qty: int = 1):
    if shop not in PRICES:
        raise HTTPException(status_code=404, detail="shop not found")
    return {"shop": shop, "qty": qty, "total": PRICES[shop] * qty}


@app.post("/order")
async def order(body: OrderIn):
    if body.shop not in COOK_TIME:
        raise HTTPException(status_code=404, detail="shop not found")
    await asyncio.sleep(COOK_TIME[body.shop])
    return {"student_id": body.student_id, "shop": body.shop, "status": "READY"}


@app.post("/claim")
async def claim(body: ClaimIn):
    global coupons_left
    async with coupon_lock:
        if body.student_id in claimed:
            return {"status": "LIMIT"}
        if coupons_left <= 0:
            return {"status": "SOLD_OUT"}
        await asyncio.sleep(0.05)
        coupons_left -= 1
        claimed.add(body.student_id)
        return {"status": "SUCCESS"}


if __name__ == "__main__":
    check(19, globals())
