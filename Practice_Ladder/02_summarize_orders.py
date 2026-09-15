"""
ขั้น 02 / 20 · อุ่นเครื่อง: list, dict, loop
ความยาก ●○○○○    อ้างอิง: Week4/foodcourt_02_gather.py (การวนผลลัพธ์ที่เป็น dict)

โจทย์
-----
เขียน summarize(orders) รับ list ของ dict แบบ {"menu": str, "price": int}
คืน dict 3 key:

    "count"          จำนวนรายการ
    "total"          ราคารวม
    "most_expensive" ชื่อเมนูที่แพงที่สุด (ถ้าไม่มีรายการเลย = None)

ตัวอย่าง
    summarize([{"menu": "ข้าวมันไก่", "price": 50},
               {"menu": "สเต็ก", "price": 159}])
    -> {"count": 2, "total": 209, "most_expensive": "สเต็ก"}

    summarize([]) -> {"count": 0, "total": 0, "most_expensive": None}

คำใบ้
    sum(o["price"] for o in orders)
    max(orders, key=lambda o: o["price"])   ← ระวัง max([]) จะ error

รัน:  python 02_summarize_orders.py
"""
from _check import check


def summarize(orders):
    # เขียนโค้ดตรงนี้
    raise NotImplementedError


if __name__ == "__main__":
    check(2, globals())
