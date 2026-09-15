"""
ตัวตรวจคำตอบของ Practice Ladder — ไม่ต้องแก้ไฟล์นี้
แต่ละไฟล์โจทย์จะเรียก check(<เลขขั้น>, globals()) ตอนรัน
"""
import asyncio
import inspect
import sys
import time
import traceback
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TESTS = {}


def test(step, desc):
    def deco(fn):
        TESTS.setdefault(step, []).append((desc, fn))
        return fn
    return deco


# ---------------------------------------------------------------- helpers
class Clock:
    def __enter__(self):
        self.t = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.elapsed = time.perf_counter() - self.t


def eq(actual, expected, what="ผลลัพธ์"):
    assert actual == expected, f"{what} ได้ {actual!r} แต่ควรได้ {expected!r}"


def near(actual, expected, tol, hint=""):
    msg = f"ใช้เวลา {actual:.2f}s แต่ควรประมาณ {expected:.2f}s (±{tol:.2f})"
    assert abs(actual - expected) <= tol, msg + (f"\n    คำใบ้: {hint}" if hint else "")


def need(ns, name):
    assert name in ns, f"ไม่พบ {name} ในไฟล์ (สะกดชื่อตรงกับโจทย์ไหม?)"
    return ns[name]


def need_async(ns, name):
    fn = need(ns, name)
    assert inspect.iscoroutinefunction(fn), f"{name} ต้องเขียนเป็น async def"
    return fn


async def assert_no_leftover_tasks():
    await asyncio.sleep(0.03)
    me = asyncio.current_task()
    left = [t for t in asyncio.all_tasks() if t is not me and not t.done()]
    assert not left, (f"ยังมี task ค้างอยู่ {len(left)} ตัวหลังฟังก์ชันจบ "
                      "(ลืม cancel / ลืมส่ง sentinel ให้ worker ครบ?)")


def has_lock(*objs):
    for obj in objs:
        values = obj.values() if isinstance(obj, dict) else vars(obj).values()
        if any(isinstance(v, asyncio.Lock) for v in values):
            return True
    return False


# ---------------------------------------------------------------- runner
def _run_one(fn, ns):
    if not inspect.iscoroutinefunction(fn):
        fn(ns)
        return

    async def main():
        if hasattr(asyncio, "timeout"):
            async with asyncio.timeout(5):
                await fn(ns)
        else:
            await asyncio.wait_for(fn(ns), 5)

    asyncio.run(main())


def check(step, ns):
    tests = TESTS.get(step, [])
    print(f"\n=== ตรวจขั้นที่ {step:02d} ===")
    passed = 0
    for desc, fn in tests:
        try:
            _run_one(fn, ns)
        except NotImplementedError:
            print(f"⬜ {desc}\n    ยังไม่ได้เขียน (ลบ raise NotImplementedError แล้วเขียนโค้ดแทน)")
        except AssertionError as e:
            print(f"❌ {desc}\n    {e}")
        except (TimeoutError, asyncio.TimeoutError):
            print(f"❌ {desc}\n    รันเกิน 5 วินาที โปรแกรมน่าจะค้าง "
                  "(ลืม task_done / sentinel / await สิ่งที่ไม่มีวันเสร็จ?)")
        except asyncio.CancelledError:
            print(f"❌ {desc}\n    CancelledError หลุดออกมาถึงตัวตรวจ (await task ที่ถูกยกเลิกโดยไม่ try/except?)")
        except Exception as e:
            frames = [f for f in traceback.extract_tb(e.__traceback__)
                      if not f.filename.endswith("_check.py")]
            where = f"\n    ที่บรรทัด {frames[-1].lineno}: {frames[-1].line}" if frames else ""
            print(f"💥 {desc}\n    {type(e).__name__}: {e}{where}")
        else:
            passed += 1
            print(f"✅ {desc}")
    print(f"\nผ่าน {passed}/{len(tests)}")
    if tests and passed == len(tests):
        print("🎉 ผ่านครบ ไปขั้นถัดไปได้เลย")


# ======================================================================
# ระดับ 0 · อุ่นเครื่อง Python
# ======================================================================
@test(1, "grade() ตัดเกรดถูกทุกช่วง รวมค่าขอบพอดี")
def _(ns):
    g = need(ns, "grade")
    for score, exp in [(100, "A"), (80, "A"), (79.9, "B"), (70, "B"), (69, "C"),
                       (60, "C"), (59, "D"), (50, "D"), (49.5, "F"), (0, "F")]:
        eq(g(score), exp, f"grade({score})")


@test(1, "คะแนนนอกช่วง 0–100 ได้ 'Invalid'")
def _(ns):
    g = need(ns, "grade")
    for score in (-1, 100.5, 150):
        eq(g(score), "Invalid", f"grade({score})")


@test(2, "summarize() สรุปรายการอาหารได้ถูก")
def _(ns):
    s = need(ns, "summarize")
    orders = [{"menu": "ข้าวมันไก่", "price": 50},
              {"menu": "สเต็ก", "price": 159},
              {"menu": "ก๋วยเตี๋ยว", "price": 45}]
    eq(s(orders), {"count": 3, "total": 254, "most_expensive": "สเต็ก"})


@test(2, "summarize([]) ไม่พังเมื่อไม่มีรายการ")
def _(ns):
    eq(need(ns, "summarize")([]), {"count": 0, "total": 0, "most_expensive": None})


# ======================================================================
# ระดับ 1 · coroutine
# ======================================================================
@test(3, "add_later เป็น async def: เรียกเฉย ๆ ได้ coroutine, await แล้วได้ผลบวก")
async def _(ns):
    fn = need_async(ns, "add_later")
    coro = fn(1, 2, 0)
    assert inspect.iscoroutine(coro), "เรียก add_later(...) แล้วควรได้ coroutine object"
    coro.close()
    eq(await fn(1, 2, 0), 3, "await add_later(1, 2, 0)")


@test(3, "await add_later(2, 3, 0.2) ได้ 5 และรอประมาณ 0.2 วินาที")
async def _(ns):
    fn = need_async(ns, "add_later")
    with Clock() as c:
        r = await fn(2, 3, 0.2)
    eq(r, 5)
    near(c.elapsed, 0.2, 0.08, "ใช้ await asyncio.sleep(delay)")


@test(4, "make_coffee('A', 0.1) คืน 'coffee for A'")
async def _(ns):
    fn = need_async(ns, "make_coffee")
    with Clock() as c:
        eq(await fn("A", 0.1), "coffee for A")
    near(c.elapsed, 0.1, 0.06)


@test(4, "serve_in_order ทำทีละคนตามลำดับ (3 คน × 0.1 s ≈ 0.3 s)")
async def _(ns):
    fn = need_async(ns, "serve_in_order")
    with Clock() as c:
        r = await fn(["A", "B", "C"], 0.1)
    eq(r, ["coffee for A", "coffee for B", "coffee for C"])
    assert c.elapsed > 0.2, "เร็วเกินไป — ขั้นนี้ให้ await ทีละคนเรียงกัน (ยังไม่ต้องทำพร้อมกัน)"
    near(c.elapsed, 0.3, 0.08)
    eq(await fn([], 0.1), [], "serve_in_order([])")


@test(5, "serve_together ทำพร้อมกัน (4 คน × 0.2 s ≈ 0.2 s) และคืนผลตามลำดับชื่อ")
async def _(ns):
    fn = need_async(ns, "serve_together")
    with Clock() as c:
        r = await fn(["A", "B", "C", "D"], 0.2)
    eq(r, ["coffee for A", "coffee for B", "coffee for C", "coffee for D"])
    near(c.elapsed, 0.2, 0.08, "สร้าง task ให้ครบทุกคนก่อน แล้วค่อย await (หรือใช้ gather)")


@test(5, "serve_together([]) ได้ []")
async def _(ns):
    eq(await need_async(ns, "serve_together")([], 0.2), [])


@test(6, "cook() รอ แล้วบันทึกชื่อลง finish_order และคืนชื่อ")
async def _(ns):
    fn = need_async(ns, "cook")
    log = []
    eq(await fn("steak", 0.05, log), "steak")
    eq(log, ["steak"], "finish_order")


@test(6, "cook_all คืน (ผลตามลำดับเมนู, ลำดับที่ทำเสร็จจริง) ใน ≈0.3 s")
async def _(ns):
    fn = need_async(ns, "cook_all")
    with Clock() as c:
        results, finished = await fn({"steak": 0.3, "chicken": 0.1, "noodle": 0.2})
    eq(list(results), ["steak", "chicken", "noodle"], "results (ต้องเรียงตาม menu)")
    eq(finished, ["chicken", "noodle", "steak"], "finish_order (เรียงตามเวลาที่เสร็จ)")
    near(c.elapsed, 0.3, 0.08, "ทุกเมนูต้องทำพร้อมกัน")


# ======================================================================
# ระดับ 2 · ควบคุม task
# ======================================================================
@test(7, "task_report คืนสถานะก่อน/หลัง และชื่อ task ถูก")
async def _(ns):
    fn = need_async(ns, "task_report")
    eq(await fn(), {"name": "Report-Job", "done_before": False,
                    "result": "OK", "done_after": True})


@test(8, "download ปกติรอ 0.3 s แล้วคืน '<ชื่อไฟล์> saved'")
async def _(ns):
    fn = need_async(ns, "download")
    with Clock() as c:
        eq(await fn("c.zip"), "c.zip saved")
    near(c.elapsed, 0.3, 0.08)


@test(8, "download ถูก cancel แล้วบันทึก cleanup_log และ raise ต่อ")
async def _(ns):
    fn = need_async(ns, "download")
    log = need(ns, "cleanup_log")
    log.clear()
    task = asyncio.create_task(fn("b.zip"))
    await asyncio.sleep(0.05)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    eq(log, ["b.zip"], "cleanup_log")
    assert task.cancelled(), "task.cancelled() เป็น False — ใน except CancelledError ต้อง raise ต่อ"


@test(8, "start_and_cancel('a.zip', 0.1) คืน True ภายใน ≈0.1 s")
async def _(ns):
    fn = need_async(ns, "start_and_cancel")
    need(ns, "cleanup_log").clear()
    with Clock() as c:
        eq(await fn("a.zip", 0.1), True)
    near(c.elapsed, 0.1, 0.08)
    eq(ns["cleanup_log"], ["a.zip"], "cleanup_log")


@test(9, "divide(9, 3) ได้ 3.0")
async def _(ns):
    eq(await need_async(ns, "divide")(9, 3), 3.0)


@test(9, "divide_all แปลง error เป็นข้อความ ไม่ทำให้ตัวอื่นพัง และทำพร้อมกัน")
async def _(ns):
    fn = need_async(ns, "divide_all")
    with Clock() as c:
        r = await fn([(10, 2), (1, 0), (5, 2)])
    eq(list(r), [5.0, "error: ZeroDivisionError", 2.5])
    near(c.elapsed, 0.1, 0.07, "ใช้ gather(..., return_exceptions=True)")
    eq(list(await fn([])), [], "divide_all([])")


@test(10, "order_with_timeout: ทันเวลาได้ผลปกติ")
async def _(ns):
    fn = need_async(ns, "order_with_timeout")
    with Clock() as c:
        eq(await fn("chicken", 0.5), "chicken ready")
    near(c.elapsed, 0.1, 0.06)


@test(10, "order_with_timeout: เกินเวลาได้ '<shop>: timeout' ทันทีที่หมดเวลา")
async def _(ns):
    fn = need_async(ns, "order_with_timeout")
    with Clock() as c:
        eq(await fn("steak", 0.2), "steak: timeout")
    near(c.elapsed, 0.2, 0.08, "ใช้ asyncio.wait_for(..., timeout=...)")


@test(10, "order_many สั่งหลายร้านพร้อมกัน แต่ละร้านมี timeout ของตัวเอง")
async def _(ns):
    fn = need_async(ns, "order_many")
    with Clock() as c:
        r = await fn(["chicken", "steak", "noodle"], 0.35)
    eq(list(r), ["chicken ready", "steak: timeout", "noodle ready"])
    near(c.elapsed, 0.35, 0.1)


@test(11, "fastest_server คืนผู้ชนะและจำนวนที่ยกเลิก")
async def _(ns):
    fn = need_async(ns, "fastest_server")
    log = need(ns, "ping_cancelled")
    log.clear()
    with Clock() as c:
        r = await fn({"alpha": 0.5, "beta": 0.1, "gamma": 0.3})
    eq(tuple(r), ("beta", 2))
    near(c.elapsed, 0.1, 0.07, "ใช้ asyncio.wait(..., return_when=asyncio.FIRST_COMPLETED)")
    await asyncio.sleep(0.02)
    eq(sorted(log), ["alpha", "gamma"], "ping_cancelled (ตัวที่ช้าต้องถูก cancel)")
    await assert_no_leftover_tasks()


@test(11, "fastest_server กรณีมีเซิร์ฟเวอร์เดียว")
async def _(ns):
    eq(tuple(await need_async(ns, "fastest_server")({"solo": 0.05})), ("solo", 0))


def _flaky(delays, value="data"):
    calls = {"n": 0}

    async def fetch():
        d = delays[min(calls["n"], len(delays) - 1)]
        calls["n"] += 1
        await asyncio.sleep(d)
        return value
    return fetch, calls


@test(12, "สำเร็จตั้งแต่ครั้งแรก → ('data', 1)")
async def _(ns):
    fetch, _calls = _flaky([0.01])
    eq(tuple(await need_async(ns, "fetch_with_retry")(fetch, 3, 0.1)), ("data", 1))


@test(12, "ช้า 2 ครั้งแรก สำเร็จครั้งที่ 3 → ('data', 3) ใน ≈0.25 s")
async def _(ns):
    fetch, calls = _flaky([0.5, 0.5, 0.05])
    with Clock() as c:
        r = await need_async(ns, "fetch_with_retry")(fetch, 5, 0.1)
    eq(tuple(r), ("data", 3))
    eq(calls["n"], 3, "จำนวนครั้งที่เรียก fetch()")
    near(c.elapsed, 0.25, 0.1, "ครั้งที่ timeout ต้องตัดทิ้งที่ 0.1 s ไม่ใช่รอจนเสร็จ")


@test(12, "ช้าตลอด → (None, attempts)")
async def _(ns):
    fetch, _calls = _flaky([1.0])
    with Clock() as c:
        eq(tuple(await need_async(ns, "fetch_with_retry")(fetch, 2, 0.1)), (None, 2))
    near(c.elapsed, 0.2, 0.1)


# ======================================================================
# ระดับ 3 · shared state
# ======================================================================
@test(13, "ถอนเงินพร้อมกัน 10 ครั้ง ครั้งละ 30 จาก 100 → สำเร็จ 3 ครั้ง เหลือ 10")
async def _(ns):
    Wallet = need(ns, "Wallet")
    w = Wallet(100)
    results = await asyncio.gather(*(w.withdraw(30) for _ in range(10)))
    eq(sum(1 for r in results if r is True), 3, "จำนวนครั้งที่ถอนสำเร็จ")
    eq(w.balance, 10, "balance")


@test(13, "ใช้ asyncio.Lock และถอนเกินยอดได้ False")
async def _(ns):
    Wallet = need(ns, "Wallet")
    w = Wallet(50)
    assert has_lock(w, ns), "ยังไม่พบ asyncio.Lock (ใน __init__ หรือระดับไฟล์)"
    eq(await w.withdraw(60), False, "withdraw(60) จากยอด 50")
    eq(w.balance, 50, "balance")


@test(14, "คนเดียวขอ 3 ครั้ง → SUCCESS, SUCCESS, LIMIT")
async def _(ns):
    s = need(ns, "CouponServer")(5)
    got = [tuple(await s.claim("u1")) for _ in range(3)]
    eq(got, [("SUCCESS", "C01"), ("SUCCESS", "C02"), ("LIMIT", None)])


@test(14, "คูปองหมด → SOLD_OUT")
async def _(ns):
    s = need(ns, "CouponServer")(1, limit=5)
    eq(tuple(await s.claim("u1")), ("SUCCESS", "C01"))
    eq(tuple(await s.claim("u2")), ("SOLD_OUT", None))


@test(14, "5 คน × ยิงพร้อมกันคนละ 4 ครั้ง (คูปอง 9 ใบ) → ไม่ซ้ำ ไม่เกิน ไม่มีใครเกิน 2")
async def _(ns):
    s = need(ns, "CouponServer")(9)
    users = [f"u{u}" for u in range(5) for _ in range(4)]
    results = await asyncio.gather(*(s.claim(u) for u in users))
    success = [(u, r[1]) for u, r in zip(users, results) if r[0] == "SUCCESS"]
    coupons = [c for _, c in success]
    eq(len(coupons), 9, "จำนวนคูปองที่แจกออกไป")
    eq(len(set(coupons)), 9, "จำนวนคูปองที่ไม่ซ้ำกัน (ถ้าน้อยกว่า 9 = แจกซ้ำ)")
    per_user = Counter(u for u, _ in success)
    assert max(per_user.values()) <= 2, f"มีคนได้เกิน 2 ใบ: {dict(per_user)}"


# ======================================================================
# ระดับ 4 · Queue
# ======================================================================
@test(15, "producer ใส่ของครบตามลำดับแล้วปิดท้ายด้วย None")
async def _(ns):
    q = asyncio.Queue()
    await need_async(ns, "producer")(q, [1, 2])
    got = []
    while not q.empty():
        got.append(q.get_nowait())
    eq(got, [1, 2, None], "ของในคิว")


@test(15, "consumer ดึงจนเจอ None แล้วคืน list")
async def _(ns):
    q = asyncio.Queue()
    for x in ["x", "y", None]:
        q.put_nowait(x)
    eq(await need_async(ns, "consumer")(q), ["x", "y"])


@test(15, "pipeline รัน producer + consumer พร้อมกัน")
async def _(ns):
    fn = need_async(ns, "pipeline")
    eq(await fn(["a", "b", "c"]), ["a", "b", "c"])
    eq(await fn([]), [], "pipeline([])")


@test(16, "6 งาน · 3 worker · งานละ 0.1 s → ≈0.2 s และปิด worker ครบ")
async def _(ns):
    fn = need_async(ns, "process_jobs")
    jobs = [f"job{i}" for i in range(6)]
    with Clock() as c:
        r = await fn(jobs, 3, 0.1)
    eq(sorted(r["done"]), sorted(jobs), "done")
    eq(sorted(r["per_worker"]), ["W1", "W2", "W3"], "ชื่อ worker ใน per_worker")
    eq(sum(r["per_worker"].values()), 6, "ผลรวม per_worker")
    near(c.elapsed, 0.2, 0.08)
    await assert_no_leftover_tasks()


@test(16, "5 งาน · 1 worker · งานละ 0.05 s → ≈0.25 s")
async def _(ns):
    with Clock() as c:
        r = await need_async(ns, "process_jobs")(list(range(5)), 1, 0.05)
    eq(r["per_worker"], {"W1": 5}, "per_worker")
    near(c.elapsed, 0.25, 0.08)
    await assert_no_leftover_tasks()


@test(17, "4 ออเดอร์ · 2 พ่อครัว · 2 ไรเดอร์ → ส่งครบใน ≈0.25 s")
async def _(ns):
    fn = need_async(ns, "food_pipeline")
    orders = ["o1", "o2", "o3", "o4"]
    with Clock() as c:
        r = await fn(orders, cooks=2, riders=2, cook_time=0.1, ride_time=0.05)
    eq(sorted(r), sorted(f"{o} delivered" for o in orders))
    near(c.elapsed, 0.25, 0.08)
    await assert_no_leftover_tasks()


@test(17, "3 ออเดอร์ · 3 พ่อครัว · 1 ไรเดอร์ (คอขวดที่ไรเดอร์) → ≈0.25 s")
async def _(ns):
    fn = need_async(ns, "food_pipeline")
    with Clock() as c:
        r = await fn(["a", "b", "c"], cooks=3, riders=1, cook_time=0.1, ride_time=0.05)
    eq(len(r), 3, "จำนวนที่ส่งถึง")
    near(c.elapsed, 0.25, 0.08)
    await assert_no_leftover_tasks()


# ======================================================================
# ระดับ 5 · ของจริง
# ======================================================================
@test(18, "grab_part ยิง POST แล้วคืน JSON")
async def _(ns):
    need(ns, "server_log").clear()
    async with need(ns, "make_client")() as client:
        r = await need_async(ns, "grab_part")(client, "r1", "A")
    eq(r, {"robot": "r1", "part": "A", "status": "OK"})


@test(18, "run_robot หยิบ A → B → C ตามลำดับ (≈0.3 s)")
async def _(ns):
    log = need(ns, "server_log")
    log.clear()
    async with ns["make_client"]() as client:
        with Clock() as c:
            r = await need_async(ns, "run_robot")(client, "r9")
    eq(list(r), ["A", "B", "C"])
    eq(log, ["r9:A", "r9:B", "r9:C"], "ลำดับที่เซิร์ฟเวอร์ได้รับ")
    near(c.elapsed, 0.3, 0.08, "หุ่นตัวเดียวต้องหยิบทีละชิ้น")


@test(18, "run_factory: reset ก่อน แล้วหุ่น 4 ตัวทำพร้อมกัน (≈0.3 s)")
async def _(ns):
    log = need(ns, "server_log")
    log.clear()
    robots = ["r1", "r2", "r3", "r4"]
    with Clock() as c:
        r = await need_async(ns, "run_factory")(robots)
    eq({k: list(v) for k, v in r.items()}, {rb: ["A", "B", "C"] for rb in robots})
    assert log and log[0] == "reset", f"คำขอแรกต้องเป็น reset แต่ได้ {log[:1]}"
    eq(log.count("reset"), 1, "จำนวนครั้งที่ reset")
    near(c.elapsed, 0.3, 0.1, "ใช้ gather กับ run_robot ของหุ่นทุกตัว")


def _asgi_client(ns):
    import httpx
    app = need(ns, "app")
    assert app is not None, "ยังไม่ได้สร้าง app"
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


@test(19, "GET /menu/{shop}?qty= คิดราคา และร้านที่ไม่มีได้ 404")
async def _(ns):
    async with _asgi_client(ns) as client:
        r = await client.get("/menu/steak", params={"qty": 2})
        eq(r.status_code, 200, "status ของ GET /menu/steak?qty=2")
        eq(r.json(), {"shop": "steak", "qty": 2, "total": 318})
        eq((await client.get("/menu/noodle")).json(), {"shop": "noodle", "qty": 1, "total": 45},
           "GET /menu/noodle (qty ไม่ส่ง = 1)")
        eq((await client.get("/menu/pizza")).status_code, 404, "status ของ GET /menu/pizza")


@test(19, "POST /order เป็น async จริง: 3 ออเดอร์พร้อมกันจบใน ≈0.3 s")
async def _(ns):
    async with _asgi_client(ns) as client:
        shops = ["chicken", "noodle", "steak"]
        with Clock() as c:
            rs = await asyncio.gather(*(client.post("/order", json={"student_id": f"s{i}", "shop": s})
                                        for i, s in enumerate(shops)))
        for i, (s, r) in enumerate(zip(shops, rs)):
            eq(r.status_code, 200, f"status ของออเดอร์ {s}")
            eq(r.json(), {"student_id": f"s{i}", "shop": s, "status": "READY"})
        near(c.elapsed, 0.3, 0.12, "ใช้ async def + await asyncio.sleep ไม่ใช่ time.sleep")
        r = await client.post("/order", json={"student_id": "x", "shop": "pizza"})
        eq(r.status_code, 404, "status ของออเดอร์ร้านที่ไม่มี")
        r = await client.post("/order", json={"student_id": "x"})
        eq(r.status_code, 422, "status เมื่อ JSON ขาด shop (ใช้ BaseModel)")


@test(19, "POST /claim: คนละ 1 ใบ มี 3 ใบ ยิงพร้อมกันก็ไม่เกิน")
async def _(ns):
    async with _asgi_client(ns) as client:
        first = (await client.post("/claim", json={"student_id": "s0"})).json()
        again = (await client.post("/claim", json={"student_id": "s0"})).json()
        eq(first, {"status": "SUCCESS"}, "s0 ขอครั้งแรก")
        eq(again, {"status": "LIMIT"}, "s0 ขอครั้งที่สอง")
        rs = await asyncio.gather(*(client.post("/claim", json={"student_id": f"s{i}"})
                                    for i in range(1, 6)))
        statuses = Counter(r.json()["status"] for r in rs)
        eq(dict(statuses), {"SUCCESS": 2, "SOLD_OUT": 3}, "ผลของ 5 คนที่ยิงพร้อมกัน")


@test(20, "reserve / release จัดการสต็อกถูก")
async def _(ns):
    court = need(ns, "FoodCourt")({"steak": 1})
    eq(await court.reserve("steak"), True, "reserve ครั้งแรก")
    eq(await court.reserve("steak"), False, "reserve ตอนหมด")
    eq(await court.reserve("pizza"), False, "reserve เมนูที่ไม่มี")
    await court.release("steak")
    eq(court.stock["steak"], 1, "stock หลัง release")
    assert has_lock(court, ns), "ยังไม่พบ asyncio.Lock"


@test(20, "order: ทำไม่ทันได้ TIMEOUT และคืนสต็อก / ไม่มีของได้ SOLD_OUT")
async def _(ns):
    court = need(ns, "FoodCourt")({"steak": 1})
    with Clock() as c:
        eq(await court.order("s1", "steak", 0.1), "TIMEOUT")
    near(c.elapsed, 0.11, 0.08)
    eq(court.stock["steak"], 1, "stock หลัง TIMEOUT (ต้องคืน)")
    eq(await court.order("s1", "chicken", 1.0), "SOLD_OUT")


@test(20, "สเต็ก 2 ชิ้น · 4 คนสั่งพร้อมกัน → READY 2 · SOLD_OUT 2")
async def _(ns):
    court = need(ns, "FoodCourt")({"steak": 2})
    with Clock() as c:
        rs = await asyncio.gather(*(court.order(f"s{i}", "steak", 1.0) for i in range(4)))
    eq(dict(Counter(rs)), {"READY": 2, "SOLD_OUT": 2})
    eq(court.stock["steak"], 0, "stock")
    assert c.elapsed < 0.75, f"ใช้ {c.elapsed:.2f}s — สองจานที่ได้ต้องทำพร้อมกัน (≈0.5 s)"


@test(20, "lunch_rush: คิว + พ่อครัว 2 คน ได้ผลครบทุกออเดอร์ และไม่มี task ค้าง")
async def _(ns):
    court = need(ns, "FoodCourt")({"chicken": 10, "noodle": 1})
    orders = [("s1", "chicken"), ("s2", "chicken"), ("s3", "noodle"),
              ("s4", "noodle"), ("s5", "chicken"), ("s6", "chicken")]
    with Clock() as c:
        r = await need_async(ns, "lunch_rush")(court, orders, 2, 1.0)
    eq(set(r), set(orders), "key ของผลลัพธ์")
    eq([r[o] for o in orders if o[1] == "chicken"], ["READY"] * 4, "ผลของ chicken")
    eq(sorted(r[o] for o in orders if o[1] == "noodle"), ["READY", "SOLD_OUT"], "ผลของ noodle")
    assert 0.15 < c.elapsed < 0.7, f"ใช้ {c.elapsed:.2f}s — ควรอยู่ราว 0.25–0.45 s (พ่อครัว 2 คนทำขนานกัน)"
    await assert_no_leftover_tasks()
