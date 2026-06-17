import sys

def calculate_ticket_price(age):
    # --- เขียนโค้ดของนักเรียนในส่วนนี้ / Write your code here ---
    if age < 12:
        price = 120
    elif 12 <= age <= 60:
        price = 200
    elif age > 60:
        price = 150
    return price
    pass
    # --------------------------------------------------------

def main():
    # เปลี่ยนมาเช็ก > 1 และใช้ sys.argv[-1] เพื่อความแม่นยำใน VPL
    if len(sys.argv) > 1:
        test_age = int(sys.argv[-1])
        result = calculate_ticket_price(test_age)
        print(result)
    else:
        test_age = 25
        result = calculate_ticket_price(test_age)
        print(f"Age: {test_age} -> Ticket Price: {result} Baht")

if __name__ == "__main__":
    main()