"""
Server Machine 2 : ระบบที่ปลอดภัย (แก้ Race Condition ด้วย asyncio.Lock)

วิธีรัน (ใช้คนละ port กับ server_vulnerable.py จะได้เปิดทั้งคู่พร้อมกันได้):
    uvicorn server:app --host 0.0.0.0 --port 8089 --reload
"""
import asyncio
from typing import Dict, List
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Coupon Hunting - SAFE (asyncio.Lock)")

STUDENTS = ["Student_6710301005", "Student_6710301012", "Student_6710301037", "Student_6710301054", "Student_6720301004"]
GROUP_SIZE = len(STUDENTS)
TOTAL_COUPONS = (GROUP_SIZE * 2) - 1

coupons_db: List[str] = [f"COUPON-{i:02d}" for i in range(1, TOTAL_COUPONS + 1)]

# ใช้ Pointer ชี้ตำแหน่งคูปองใบถัดไปที่จะจ่ายแจก
current_coupon_index = 0

student_claims: Dict[str, List[str]] = {student_id: [] for student_id in STUDENTS}

# กุญแจห้องน้ำ 1 ดอก: ใครถืออยู่คนเดียวเท่านั้นที่เข้า Critical Section ได้
# ที่เหลือต้อง await รอคิวจนกว่ากุญแจจะถูกคืน
coupon_lock = asyncio.Lock()


class ClaimRequest(BaseModel):
    student_id: str


@app.post("/claim")
async def claim_coupon(req: ClaimRequest):
    global current_coupon_index
    student_id = req.student_id

    # เช็คชื่อได้นอกล็อก เพราะไม่ได้แตะ Shared State ที่เปลี่ยนแปลงได้
    if student_id not in student_claims:
        return {"status": "INVALID_STUDENT", "message": "ไม่พบรายชื่อในระบบ"}

    # ── PROTECTED CRITICAL SECTION ────────────────────────────────
    # ต้องครอบทั้ง 3 อย่างไว้ในล็อกก้อนเดียวกัน คือ
    #   1) เช็คโควตาส่วนตัว   2) เช็คสต็อกคงเหลือ   3) ตัดคูปอง + ขยับ Pointer
    # ถ้าล็อกแค่ตอนตัดคูปอง แต่ปล่อยให้เช็คโควตาอยู่นอกล็อก
    # จะยังมีคนได้ 3 ใบอยู่ดี เพราะสองคำขอเช็คโควตาผ่านพร้อมกันได้
    async with coupon_lock:

        if len(student_claims[student_id]) >= 2:
            return {"status": "LIMIT_REACHED", "message": "คุณรับคูปองครบ 2 ใบแล้ว"}

        if current_coupon_index < len(coupons_db):
            index_to_claim = current_coupon_index

            # หลับตรงนี้ได้อย่างปลอดภัย เพราะยังถือกุญแจอยู่ในมือ
            # คำขอของคนอื่นจะไปติดคิวรออยู่ที่บรรทัด async with ด้านบน
            # ไม่มีใครหลุดเข้ามาอ่าน current_coupon_index ตัวเดิมซ้ำได้
            await asyncio.sleep(0.1)

            coupon = coupons_db[index_to_claim]
            student_claims[student_id].append(coupon)
            current_coupon_index = index_to_claim + 1

            return {
                "status": "SUCCESS",
                "claimed_coupon": coupon,
                "total_owned": len(student_claims[student_id])
            }

        return {
            "status": "OUT_OF_STOCK",
            "message": "คูปองหมดแล้ว"
        }
    # ออกจากบล็อกเมื่อไหร่ กุญแจถูกคืนอัตโนมัติทันที
    # แม้โค้ดข้างในจะ return หรือ raise exception ก็ตาม


@app.get("/my-coupons/{student_id}")
async def get_my_coupons(student_id: str):
    """ดูคูปองเฉพาะของนักเรียนคนเดียว (client.py เรียกใช้ตอนจบภารกิจ)"""
    if student_id not in student_claims:
        return {"status": "INVALID_STUDENT", "message": "ไม่พบรายชื่อในระบบ"}

    my_coupons = student_claims[student_id]
    return {
        "student_id": student_id,
        "total_claimed": len(my_coupons),
        "claimed_coupons": my_coupons
    }


@app.get("/summary")
async def get_summary():
    all_issued = [c for coupons in student_claims.values() for c in coupons]
    duplicated = sorted({c for c in all_issued if all_issued.count(c) > 1})

    return {
        "remaining_stock": len(coupons_db) - current_coupon_index,
        "total_coupons_in_stock": TOTAL_COUPONS,
        "total_issued": len(all_issued),
        "over_issued": len(all_issued) - TOTAL_COUPONS,
        "duplicated_coupons": duplicated,
        "student_claims": student_claims
    }
