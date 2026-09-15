"""เฉลยขั้น 13"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check


class Wallet:
    def __init__(self, balance):
        self.balance = balance
        self.lock = asyncio.Lock()

    async def withdraw(self, amount):
        async with self.lock:                 # เช็คยอด + หักเงิน อยู่ในล็อกเดียวกัน
            if self.balance >= amount:
                await asyncio.sleep(0.01)
                self.balance -= amount
                return True
            return False


if __name__ == "__main__":
    check(13, globals())
