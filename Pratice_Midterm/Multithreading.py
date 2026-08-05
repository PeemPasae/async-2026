import time
import threading # ต้อง import โมดูลนี้

def make_coffee(order_id):
    print(f"กำลังชงออเดอร์ {order_id}...")
    time.sleep(2)
    print(f"ออเดอร์ {order_id} เสร็จแล้ว!")

# การเรียกใช้งาน
threads = [] # สร้าง List ว่างๆ ไว้เก็บ Thread

# 1. สร้าง Thread 
t1 = threading.Thread(target=make_coffee, args=(1,))
t2 = threading.Thread(target=make_coffee, args=(2,))

# 2. เก็บเข้า List และสั่งให้เริ่มทำงาน (.start)
threads.extend([t1, t2])
for t in threads:
    t.start() # สั่งเริ่มทำงานพร้อมกัน!

# 3. สั่งให้โปรแกรมหลัก "รอ" จนกว่าทุก Thread จะเสร็จ (.join)
for t in threads:
    t.join() 

print("ทำทุกออเดอร์เสร็จแล้ว!")