"""
05 · เมธอดของ Task
อ้างอิงงานในคลาส: Week3/task_01 – task_06, Week1/pid04_asyncio.py

┌───────────────────────────────┬───────────────────────────────────────────────────────┐
│ คำสั่ง                         │ ความหมาย                                                │
├───────────────────────────────┼───────────────────────────────────────────────────────┤
│ task.done()                   │ จบแล้วหรือยัง (สำเร็จ / error / ถูกยกเลิก = True หมด)       │
│ task.cancelled()              │ จบเพราะถูกยกเลิกหรือไม่                                   │
│ task.result()                 │ ค่าที่ return  · ยังไม่จบ → InvalidStateError               │
│                               │ · ถ้า task error → raise error ตัวนั้นซ้ำ                   │
│ task.exception()              │ ดู error โดยไม่ raise (สำเร็จ → None) · ต้องจบก่อน         │
│ task.get_name() / set_name()  │ อ่าน / ตั้งชื่อ task  (ค่าเริ่มต้น "Task-1", "Task-2", ...)   │
│ task.add_done_callback(fn)    │ ให้เรียก fn(task) อัตโนมัติเมื่อ task จบ                     │
│                               │ fn เป็นฟังก์ชัน "ธรรมดา" (def) รับ task 1 ตัว               │
│ asyncio.current_task()        │ task ที่กำลังรันบรรทัดนี้อยู่                                  │
│ asyncio.all_tasks()           │ set ของ task ที่ยังไม่จบใน loop (รวม task ของ main ด้วย)     │
└───────────────────────────────┴───────────────────────────────────────────────────────┘
(task.cancel() อธิบายแยกในไฟล์ 06)

รัน:  python 05_task_methods.py
"""
import asyncio


async def short_job():
    await asyncio.sleep(0.3)
    return "Success"


async def broken_job():
    await asyncio.sleep(0.1)
    return 10 / 0


def on_finish(finished_task):
    # callback: ฟังก์ชันธรรมดา ถูกเรียกอัตโนมัติเมื่อ task จบ และได้ task ตัวนั้นเป็นพารามิเตอร์
    print(f"   [callback] {finished_task.get_name()} จบแล้ว ผล = {finished_task.result()!r}")


async def main():
    print("=== 1) done() ก่อน/หลัง และ result() ===")
    task = asyncio.create_task(short_job())
    print("   done() ตอนสร้าง   :", task.done())            # False
    try:
        task.result()                                    # ยังไม่จบ → error
    except asyncio.InvalidStateError as e:
        print("   result() ก่อนจบ  : InvalidStateError:", e)
    await task
    print("   done() หลัง await :", task.done())            # True
    print("   result()          :", task.result())          # Success
    print("   exception()       :", task.exception())       # None
    print("   cancelled()       :", task.cancelled())       # False

    print("\n=== 2) task ที่ error: exception() ดูได้โดยโปรแกรมไม่พัง ===")
    bad = asyncio.create_task(broken_job())
    await asyncio.sleep(0.2)                              # ไม่ await bad ตรง ๆ จึงไม่ raise ใส่ main
    print("   done()      :", bad.done())                    # True (จบเพราะ error ก็นับว่าจบ)
    print("   exception() :", type(bad.exception()).__name__)  # ZeroDivisionError
    try:
        bad.result()                                     # result() จะ raise error ตัวเดิม
    except ZeroDivisionError:
        print("   result()    : raise ZeroDivisionError ซ้ำ")

    print("\n=== 3) ชื่อ task ===")
    t = asyncio.create_task(short_job())
    print("   ชื่อเริ่มต้น :", t.get_name())                  # Task-4 (เลขขึ้นกับจำนวน task ที่เคยสร้าง)
    t.set_name("Payment-Validator")
    print("   หลัง set_name:", t.get_name())
    t2 = asyncio.create_task(short_job(), name="Named-At-Create")
    print("   ตั้งตอนสร้าง :", t2.get_name())
    await asyncio.gather(t, t2)

    print("\n=== 4) add_done_callback ===")
    t = asyncio.create_task(short_job(), name="Download")
    t.add_done_callback(on_finish)                        # ส่ง "ชื่อฟังก์ชัน" ไม่มีวงเล็บ
    await t
    await asyncio.sleep(0)                                # ให้ loop มีจังหวะเรียก callback

    print("\n=== 5) current_task และ all_tasks ===")
    me = asyncio.current_task()
    print("   task ที่รัน main อยู่ :", me.get_name())
    jobs = [asyncio.create_task(short_job(), name=f"Job-{i}") for i in range(3)]
    names = sorted(x.get_name() for x in asyncio.all_tasks())
    print(f"   all_tasks() มี {len(names)} ตัว :", names)     # 4 = main + Job-0..2
    await asyncio.gather(*jobs)


if __name__ == "__main__":
    asyncio.run(main())

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • done() True ได้ 3 แบบ: สำเร็จ / error / ถูกยกเลิก
# • result() ใช้ได้เมื่อ done แล้วเท่านั้น และจะ raise ถ้า task error
# • exception() ใช้เช็ค error แบบไม่ raise
# • callback เป็น def ธรรมดา รับ task · ส่งชื่อฟังก์ชันโดยไม่ใส่ ()
# • all_tasks() นับ task ของ main ด้วยเสมอ
