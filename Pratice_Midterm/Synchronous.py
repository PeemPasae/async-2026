import time

def make_coffee(order_id):
    print(f"กำลังชงออเดอร์ {order_id}...")
    time.sleep(2) # จำลองเวลาชง 2 วินาที
    print(f"ออเดอร์ {order_id} เสร็จแล้ว!")

# การเรียกใช้งาน
print("เริ่มการทำงาน Synchronous")
make_coffee(1)
make_coffee(2)
print("ทำทุกออเดอร์เสร็จแล้ว!")