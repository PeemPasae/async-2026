"""
ขั้น 01 / 20 · อุ่นเครื่อง: if / elif และค่าขอบ
ความยาก ●○○○○    อ้างอิง: WX/grade.py, WX/ticket.py

โจทย์
-----
เขียนฟังก์ชัน grade(score) คืนเกรดเป็นตัวอักษร

    80–100  -> "A"
    70–79.x -> "B"
    60–69.x -> "C"
    50–59.x -> "D"
    0–49.x  -> "F"
    น้อยกว่า 0 หรือมากกว่า 100 -> "Invalid"

ตัวอย่าง
    grade(80)    -> "A"
    grade(79.9)  -> "B"
    grade(-1)    -> "Invalid"

คำใบ้
    เช็คกรณี Invalid ก่อน แล้วไล่จากเกรดสูงลงล่างด้วย >= จะไม่ต้องเขียนช่วงซ้ำ

รัน:  python 01_grade.py
"""
from _check import check


def grade(score):
    # เขียนโค้ดตรงนี้
    if score >= 80 and score <= 100:
        return "A"
    elif score >= 70 and score < 80:
        return "B"
    elif score >= 60 and score < 70:
        return "C"
    elif score >= 50 and score < 60:
        return "D"
    elif score >= 0 and score < 50:
        return "F"
    else:
        return "Invalid"


if __name__ == "__main__":
    check(1, globals())
