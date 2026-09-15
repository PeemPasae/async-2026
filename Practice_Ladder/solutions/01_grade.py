"""เฉลยขั้น 01"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from _check import check


def grade(score):
    if score < 0 or score > 100:
        return "Invalid"
    if score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    return "F"


if __name__ == "__main__":
    check(1, globals())
