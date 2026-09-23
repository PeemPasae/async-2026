# ==========================================
# PreQuize 1 — Hello World Student
# ==========================================
# ส่งแล้วเมื่อ 16 ก.ย. 2569 8:51 น. -> ได้ 5/5
#   [/] test_function_structure: Passed (+2)
#   [/] test_execution_and_time: Passed (+3)
#
# โจทย์คือแพตเทิร์นเดียวกับ Exam_Practice/a1.py คือ
# ต้อง await coroutine ไม่ใช่เรียกเฉยๆ ไม่งั้นได้
#   RuntimeWarning: coroutine 'say_hello' was never awaited
#
# ที่ส่งไปเป็นแบบนี้ (ผ่านแล้ว ไม่ต้องแก้)

import asyncio


async def say_hello():
    print("Hello")
    await asyncio.sleep(1.5)
    print("World")


async def main():
    await say_hello()


asyncio.run(say_hello())


# --- ข้อสังเกตไว้อ่าน ไม่ใช่ข้อผิด ---
#
# main() ถูกประกาศไว้แต่ไม่มีใครเรียก เป็น dead code
# เพราะบรรทัดสุดท้ายเรียก say_hello() ตรงๆ ข้าม main() ไป
#
# ข้อนี้ผ่านเพราะตัวตรวจดูแค่ผลลัพธ์กับเวลา
# แต่ถ้าโจทย์ข้ออื่นเขียนในเกณฑ์ว่า "ต้องมีฟังก์ชันหลักครอบการทำงาน"
# (เช่น Q2 ที่ระบุ main_task ไว้ชัด) การข้าม main() แบบนี้จะโดนหักคะแนนโครงสร้าง
#
# ถ้าอยากให้เรียกผ่าน main() จริง เปลี่ยนบรรทัดสุดท้ายเป็น
#     asyncio.run(main())
# ผลลัพธ์กับเวลาเหมือนเดิมทุกอย่าง
