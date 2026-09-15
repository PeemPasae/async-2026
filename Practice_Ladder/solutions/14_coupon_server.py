"""เฉลยขั้น 14"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import asyncio
from _check import check


class CouponServer:
    def __init__(self, total, limit=2):
        self.coupons = [f"C{i:02d}" for i in range(1, total + 1)]
        self.index = 0
        self.limit = limit
        self.claims = {}
        self.lock = asyncio.Lock()

    async def claim(self, user):
        async with self.lock:
            mine = self.claims.setdefault(user, [])
            if len(mine) >= self.limit:
                return ("LIMIT", None)
            if self.index >= len(self.coupons):
                return ("SOLD_OUT", None)
            await asyncio.sleep(0.01)
            coupon = self.coupons[self.index]
            self.index += 1
            mine.append(coupon)
            return ("SUCCESS", coupon)


if __name__ == "__main__":
    check(14, globals())
