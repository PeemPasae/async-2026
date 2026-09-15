"""เฉลยขั้น 02"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from _check import check


def summarize(orders):
    if not orders:
        return {"count": 0, "total": 0, "most_expensive": None}
    top = max(orders, key=lambda o: o["price"])
    return {
        "count": len(orders),
        "total": sum(o["price"] for o in orders),
        "most_expensive": top["menu"],
    }


if __name__ == "__main__":
    check(2, globals())
