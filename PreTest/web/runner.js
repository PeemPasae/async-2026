// รัน Python จริงในเบราว์เซอร์ด้วย Pyodide (อยู่ใน Web Worker เพื่อหยุดได้ถ้าโค้ดค้าง)
// ส่วน PY_HARNESS = ตัวรันโค้ด + ชุดตรวจของแต่ละข้อ + อินเทอร์เน็ตจำลองสำหรับ PokéAPI

const PYODIDE_URL = "https://cdn.jsdelivr.net/npm/pyodide@0.27.7/";

const PY_HARNESS = String.raw`
import ast, asyncio, builtins, gc, inspect, json, re, sys, time, traceback, types, warnings
import js

warnings.simplefilter("always", RuntimeWarning)
LIMIT = 12.0


def emit(obj):
    js.pyEmit(json.dumps(obj))


# ─────────────────────────── stdout/stderr capture (มี timestamp ทุกบรรทัด)

class _Stream:
    def __init__(self, name, cap):
        self.name, self.cap, self.buf = name, cap, ""

    def write(self, s):
        s = str(s)
        self.buf += s
        while "\n" in self.buf:
            line, self.buf = self.buf.split("\n", 1)
            self.cap.push(self.name, line)
        return len(s)

    def flush(self):
        if self.buf:
            line, self.buf = self.buf, ""
            self.cap.push(self.name, line)

    def isatty(self):
        return False


class Capture:
    def __init__(self, live):
        self.live = live
        self.lines = []
        self.errs = []

    def push(self, stream, text):
        t = time.perf_counter() - self.t0
        (self.lines if stream == "out" else self.errs).append((t, text))
        if self.live:
            emit({"event": "line", "stream": stream, "t": t, "text": text})

    def __enter__(self):
        self.t0 = time.perf_counter()
        self._saved = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = _Stream("out", self), _Stream("err", self)
        return self

    def __exit__(self, *exc):
        sys.stdout.flush()
        sys.stderr.flush()
        sys.stdout, sys.stderr = self._saved
        return False

    @property
    def texts(self):
        return [t for _, t in self.lines]


# ─────────────────────────── อินเทอร์เน็ตจำลอง (PokéAPI)

POKEDEX = {
    "bulbasaur": (1, ["grass", "poison"], 69), "charizard": (6, ["fire", "flying"], 905),
    "squirtle": (7, ["water"], 90), "pikachu": (25, ["electric"], 60),
    "gengar": (94, ["ghost", "poison"], 405), "gyarados": (130, ["water", "flying"], 2350),
    "ditto": (132, ["normal"], 40), "eevee": (133, ["normal"], 65),
    "snorlax": (143, ["normal"], 4600), "mewtwo": (150, ["psychic"], 1220),
}
LATENCY = {"ditto": 0.7, "pikachu": 0.9, "charizard": 0.6}
URL_RE = re.compile(r"https?://pokeapi\.co/api/v2/pokemon/([^/?#]+)/?")


class Net:
    def __init__(self):
        self.calls = []

    async def request(self, url):
        url = str(url)
        m = URL_RE.fullmatch(url)
        name = m.group(1).lower() if m else None
        start = time.perf_counter()
        await asyncio.sleep(LATENCY.get(name, 0.5))
        self.calls.append({"url": url, "start": start, "end": time.perf_counter()})
        if name not in POKEDEX:
            return 404, None, "Not Found"
        pid, kinds, weight = POKEDEX[name]
        data = {
            "id": pid, "name": name, "weight": weight, "height": 7,
            "types": [{"slot": i + 1, "type": {"name": k, "url": f"https://pokeapi.co/api/v2/type/{k}/"}}
                      for i, k in enumerate(kinds)],
            "abilities": [], "stats": [],
        }
        return 200, data, json.dumps(data)


def make_aiohttp(net):
    m = types.ModuleType("aiohttp")

    class ClientError(Exception):
        pass

    class ClientResponseError(ClientError):
        def __init__(self, status, message=""):
            super().__init__(f"{status}, message='{message}'")
            self.status, self.message = status, message

    class ContentTypeError(ClientResponseError):
        pass

    class ClientResponse:
        def __init__(self, url, status, data, text):
            self.url, self.status, self._data, self._text = url, status, data, text
            self.ok = status < 400
            self.reason = "OK" if self.ok else "Not Found"

        async def json(self, *a, **k):
            if self._data is None:
                raise ContentTypeError(self.status, "Attempt to decode JSON with unexpected mimetype: text/plain")
            return json.loads(self._text)

        async def text(self, *a, **k):
            return self._text

        async def read(self):
            return self._text.encode()

        def raise_for_status(self):
            if not self.ok:
                raise ClientResponseError(self.status, self.reason)

        def release(self):
            pass

        def close(self):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

    class _RequestContext:
        def __init__(self, coro):
            self._coro = coro

        def __await__(self):
            return self._coro.__await__()

        async def __aenter__(self):
            return await self._coro

        async def __aexit__(self, *a):
            return False

    class ClientSession:
        def __init__(self, *a, **k):
            self.closed = False

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            self.closed = True
            return False

        async def close(self):
            self.closed = True

        def get(self, url, *a, **k):
            if self.closed:
                raise RuntimeError("Session is closed")

            async def go():
                status, data, text = await net.request(url)
                return ClientResponse(str(url), status, data, text)

            return _RequestContext(go())

    class ClientTimeout:
        def __init__(self, *a, **k):
            pass

    for name, obj in list(locals().items()):
        if isinstance(obj, type):
            setattr(m, name, obj)
    return m


def make_httpx(net):
    m = types.ModuleType("httpx")

    class HTTPStatusError(Exception):
        pass

    class Response:
        def __init__(self, url, status, data, text):
            self.url, self.status_code, self._data, self.text = url, status, data, text
            self.is_success = status < 400

        def json(self):
            if self._data is None:
                raise ValueError("Expecting value: line 1 column 1 (char 0)")
            return json.loads(self.text)

        def raise_for_status(self):
            if not self.is_success:
                raise HTTPStatusError(f"Client error '{self.status_code} Not Found' for url '{self.url}'")
            return self

    class AsyncClient:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def aclose(self):
            pass

        async def get(self, url, *a, **k):
            status, data, text = await net.request(url)
            return Response(str(url), status, data, text)

    def _sync(*a, **k):
        raise RuntimeError("httpx แบบ sync บล็อก event loop — ใช้ async with httpx.AsyncClient() as client: await client.get(url)")

    m.AsyncClient, m.Response, m.HTTPStatusError = AsyncClient, Response, HTTPStatusError
    m.get = m.Client = _sync
    return m


def make_requests():
    m = types.ModuleType("requests")

    def _sync(*a, **k):
        raise RuntimeError("requests เป็นแบบ synchronous (บล็อก event loop) — ใช้ aiohttp หรือ httpx.AsyncClient")

    m.get = m.post = m.Session = _sync
    return m


# ─────────────────────────── แปลง asyncio.run(x) ระดับบนสุด -> await x

def _blocked_run(main, **kw):
    if inspect.iscoroutine(main):
        main.close()
    raise RuntimeError("เรียก asyncio.run() จากในฟังก์ชัน — ในเว็บนี้ให้เรียก asyncio.run(...) ที่ระดับบนสุดของไฟล์ (นอก def)")


asyncio.run = _blocked_run


def import_names(tree):
    mods, runs = {"asyncio"}, set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name == "asyncio":
                    mods.add(a.asname or "asyncio")
        elif isinstance(node, ast.ImportFrom) and node.module == "asyncio":
            for a in node.names:
                runs.add(a.asname or a.name)
    return mods, runs


def dotted(f):
    parts = []
    while isinstance(f, ast.Attribute):
        parts.append(f.attr)
        f = f.value
    if isinstance(f, ast.Name):
        parts.append(f.id)
        return ".".join(reversed(parts))
    return ""


def is_asyncio(func, attr, names):
    mods, froms = names
    d = dotted(func)
    if "." in d:
        head, _, tail = d.rpartition(".")
        return tail == attr and head in mods
    return d == attr and attr in froms


def transform(tree, names):
    class T(ast.NodeTransformer):
        depth = 0

        def _scope(self, node):
            self.depth += 1
            self.generic_visit(node)
            self.depth -= 1
            return node

        visit_FunctionDef = visit_AsyncFunctionDef = visit_Lambda = visit_ClassDef = _scope

        def visit_Call(self, node):
            self.generic_visit(node)
            if self.depth == 0 and node.args and is_asyncio(node.func, "run", names):
                return ast.copy_location(ast.Await(value=node.args[0]), node)
            return node

    tree = T().visit(tree)
    ast.fix_missing_locations(tree)
    return tree


def uses(tree, names, attr):
    return any(isinstance(n, ast.Call) and is_asyncio(n.func, attr, names) for n in ast.walk(tree))


# ─────────────────────────── คำใบ้จากข้อความ error

HINTS = [
    (r"'await' outside async function", "await ใช้ได้เฉพาะในฟังก์ชันที่ประกาศด้วย async def"),
    (r"'async with' outside async function", "async with ต้องอยู่ในฟังก์ชัน async def"),
    (r"was never awaited", "มี coroutine ที่ถูกเรียกแต่ไม่ได้ await — ใส่ await ข้างหน้า"),
    (r"name 'asyncio' is not defined", "ลืม import asyncio ที่บรรทัดแรก"),
    (r"name 'aiohttp' is not defined", "ลืม import aiohttp"),
    (r"Passing coroutines is forbidden", "asyncio.wait() รับได้เฉพาะ Task — ห่อด้วย asyncio.create_task(...) ก่อน"),
    (r"'coroutine' object is not (subscriptable|iterable)", "เอาผลของ coroutine ไปใช้โดยยังไม่ได้ await"),
    (r"cannot unpack non-iterable coroutine", "ลืม await ก่อนแตกค่าผลลัพธ์"),
    (r"can't be used in 'await' expression", "await ได้เฉพาะ coroutine / Task / Future — สิ่งที่ await อยู่ไม่ใช่ coroutine"),
    (r"a coroutine was expected", "ต้องส่ง coroutine (เช่น func()) ไม่ใช่ตัวฟังก์ชันเปล่า ๆ หรือค่าอื่น"),
    (r"expected an indented block", "ต้องมีโค้ดย่อหน้าเข้าไปใต้บรรทัดที่ลงท้ายด้วย :"),
    (r"unindent does not match|unexpected indent", "ย่อหน้าไม่ตรงกัน — ใช้ 4 ช่องว่างให้เท่ากันในบล็อกเดียวกัน"),
    (r"was never closed|unmatched|does not match opening", "วงเล็บเปิด/ปิดไม่ครบคู่"),
    (r"expected ':'", "ท้ายบรรทัด def / with / if / for ต้องมี :"),
    (r"invalid syntax", "ไวยากรณ์ผิด — ดูวงเล็บ, จุลภาค และ : ท้ายบรรทัด"),
    (r"takes \d+ positional argument", "จำนวน argument ที่ส่งไม่ตรงกับที่ฟังก์ชันรับ"),
    (r"'NoneType' object is not subscriptable", "ตัวแปรเป็น None — ฟังก์ชันที่เรียกอาจลืม return"),
    (r"No module named", "เว็บนี้มี asyncio, aiohttp, httpx (จำลอง) และ standard library"),
    (r"is not defined", "ชื่อนี้ยังไม่ได้ประกาศ — สะกดผิดหรือเปล่า?"),
]


def hint_for(msg):
    for pat, hint in HINTS:
        if re.search(pat, msg):
            return hint
    return ""


def fmt_syntax(e):
    msg = f"{type(e).__name__}: {e.msg}"
    return {"kind": "syntax", "message": msg, "line": e.lineno, "hint": hint_for(msg)}


def fmt_exc(e):
    frames = [f.lineno for f in traceback.extract_tb(e.__traceback__) if f.filename == "main.py"]
    msg = f"{type(e).__name__}: {e}"
    return {"kind": "runtime", "message": msg, "line": frames[-1] if frames else None,
            "frames": frames, "hint": hint_for(msg)}


def lint(tree):
    notes = []
    async_defs = {n.name for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)}
    coro_calls = {"asyncio.sleep", "asyncio.gather", "asyncio.wait", "asyncio.wait_for"} | async_defs
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            name = dotted(node.value.func)
            if name in coro_calls:
                notes.append({"line": node.lineno,
                              "text": f"บรรทัด {node.lineno}: เรียก {name}(...) แต่ไม่ได้ await — coroutine จะไม่ถูกรัน"})
    for fn in ast.walk(tree):
        if isinstance(fn, ast.AsyncFunctionDef):
            for node in ast.walk(fn):
                if isinstance(node, ast.Call) and dotted(node.func) == "time.sleep":
                    notes.append({"line": node.lineno,
                                  "text": f"บรรทัด {node.lineno}: time.sleep() บล็อก event loop — ใช้ await asyncio.sleep() แทน"})
    return notes


# ─────────────────────────── ตัวช่วยสำหรับชุดตรวจ

class Call:
    def __init__(self, value, elapsed, lines, err):
        self.value, self.elapsed, self.lines, self.err = value, elapsed, lines, err

    @property
    def texts(self):
        return [t for _, t in self.lines]


class Ctx:
    def __init__(self, ns, tree, names, run, net):
        self.ns, self.tree, self.names, self.run, self.net = ns, tree, names, run, net
        self.tests = []

    def add(self, label, pts, ok, detail=""):
        self.tests.append({"label": label, "pts": pts, "ok": bool(ok), "detail": detail})

    def uses(self, attr):
        return uses(self.tree, self.names, attr)

    def fn(self, name, params):
        f = self.ns.get(name)
        if f is None or not callable(f):
            return False, f"ไม่พบฟังก์ชัน {name}()"
        if not inspect.iscoroutinefunction(f):
            return False, f"{name} ต้องประกาศด้วย async def"
        got = [p.name for p in inspect.signature(f).parameters.values()]
        if got != params:
            return False, f"{name} ควรรับ ({', '.join(params)}) แต่ตอนนี้รับ ({', '.join(got)})"
        return True, ""

    async def call(self, name, *args):
        f = self.ns.get(name)
        if f is None:
            return Call(None, 0, [], f"ไม่พบฟังก์ชัน {name}()")
        value, err = None, None
        with Capture(False) as cap:
            t0 = time.perf_counter()
            try:
                value = f(*args)
                if inspect.isawaitable(value):
                    value = await asyncio.wait_for(value, LIMIT)
            except asyncio.TimeoutError:
                err = f"รอนานเกิน {LIMIT:.0f} วินาที"
            except Exception as e:
                err = f"{type(e).__name__}: {e}"
                h = hint_for(err)
                if h:
                    err += f" → {h}"
            elapsed = time.perf_counter() - t0
        return Call(value, elapsed, cap.lines, err)


def timing(label, pts, r, lo, hi, ctx, slow_hint="งานยังรันทีละตัว ไม่ได้รันพร้อมกัน"):
    if r.err:
        ctx.add(label, pts, False, r.err)
    elif r.elapsed < lo:
        ctx.add(label, pts, False, f"ใช้เวลา {r.elapsed:.2f} วิ — เร็วเกินจริง ลืม await asyncio.sleep หรือเปล่า?")
    elif r.elapsed > hi:
        ctx.add(label, pts, False, f"ใช้เวลา {r.elapsed:.2f} วิ (เกิน {hi} วิ) — {slow_hint}")
    else:
        ctx.add(label, pts, True, f"ใช้เวลา {r.elapsed:.2f} วิ")


def same(label, pts, r, want, ctx, kind=None):
    if r.err:
        ctx.add(label, pts, False, r.err)
    elif kind is not None and not isinstance(r.value, kind):
        ctx.add(label, pts, False, f"ได้ {type(r.value).__name__} {r.value!r} — ต้องเป็น {kind.__name__}")
    elif r.value != want:
        ctx.add(label, pts, False, f"ได้ {r.value!r}\nควรได้ {want!r}")
    else:
        ctx.add(label, pts, True, repr(r.value))


# ─────────────────────────── ชุดตรวจของแต่ละข้อ

async def t_q1(c):
    ok, why = c.fn("say_hello", [])
    c.add("ประกาศ async def say_hello()", 2, ok, why)
    label = "พิมพ์ Hello → รอ 1.5 วิ → World"
    if not ok:
        c.add(label, 3, False, "ต้องมี say_hello ที่เป็น async def ก่อน")
    else:
        r = await c.call("say_hello")
        if r.err:
            c.add(label, 3, False, r.err)
        elif r.texts != ["Hello", "World"]:
            c.add(label, 3, False, f"พิมพ์ออกมา {r.texts!r} — ควรเป็น ['Hello', 'World']")
        else:
            gap = r.lines[1][0] - r.lines[0][0]
            good = 1.35 <= gap <= 1.8
            c.add(label, 3, good, f"Hello กับ World ห่างกัน {gap:.2f} วิ"
                  + ("" if good else (" — ควร ~1.5 วิ ลืม await หรือเปล่า?" if gap < 1.35 else " — นานเกินไป")))
    c.add("ท้ายไฟล์สั่งรัน asyncio.run(say_hello())", 0, c.run.texts == ["Hello", "World"],
          "" if c.run.texts == ["Hello", "World"] else ("รันไฟล์แล้วไม่มีอะไรพิมพ์ออกมา" if not c.run.texts else f"รันไฟล์ได้ {c.run.texts!r}"))


async def t_q2(c):
    ok1, why1 = c.fn("print_message", ["message", "delay"])
    ok2, why2 = c.fn("main_task", [])
    c.add("ประกาศ print_message(message, delay) และ main_task()", 2, ok1 and ok2, why1 or why2)
    if ok1:
        r = await c.call("print_message", "ping", 0.3)
        good = not r.err and r.texts == ["ping"] and 0.25 <= r.elapsed <= 0.6
        c.add("print_message รอ delay แล้วพิมพ์ message", 0, good,
              r.err or (f"ลองเรียก print_message('ping', 0.3): พิมพ์ {r.texts!r} ใช้ {r.elapsed:.2f} วิ"))
    label = "A ออกที่ ~1.0 วิ และ B ที่ ~2.0 วิ (รันพร้อมกัน)"
    if not ok2:
        c.add(label, 3, False, why2)
    else:
        r = await c.call("main_task")
        if r.err:
            c.add(label, 3, False, r.err)
        elif r.texts != ["A", "B"]:
            c.add(label, 3, False, f"พิมพ์ออกมา {r.texts!r} — ควรเป็น ['A', 'B']")
        else:
            ta, tb = r.lines[0][0], r.lines[1][0]
            good = 0.9 <= ta <= 1.35 and 1.85 <= tb <= 2.4
            detail = f"A ที่ {ta:.2f} วิ, B ที่ {tb:.2f} วิ"
            if tb > 2.4:
                detail += " — B ช้าไป: งานรันทีละตัว ให้ create_task ทั้งสองก่อนแล้วค่อย await"
            c.add(label, 3, good, detail)
    c.add("ใช้ asyncio.create_task()", 0, c.uses("create_task"), "" if c.uses("create_task") else "โจทย์กำหนดให้สร้าง Task ด้วย asyncio.create_task")
    c.add("ท้ายไฟล์สั่งรัน asyncio.run(main_task())", 0, c.run.texts == ["A", "B"],
          "" if c.run.texts == ["A", "B"] else ("รันไฟล์แล้วไม่มีอะไรพิมพ์ออกมา" if not c.run.texts else f"รันไฟล์ได้ {c.run.texts!r}"))


async def fetch_db_checks(c):
    ok, why = c.fn("fetch_db_record", ["table_name", "latency"])
    if ok:
        r = await c.call("fetch_db_record", "demo", 0.3)
        good = not r.err and r.value == "RowData_demo" and 0.25 <= r.elapsed <= 0.6
        c.add("fetch_db_record('demo', 0.3) → 'RowData_demo' หลัง ~0.3 วิ", 0, good,
              r.err or f"ได้ {r.value!r} ใช้ {r.elapsed:.2f} วิ")
    return ok, why


async def t_q3(c):
    ok1, why1 = c.fn("fetch_db_record", ["table_name", "latency"])
    ok2, why2 = c.fn("main_fetch", [])
    c.add("fetch_db_record(table_name, latency) และ main_fetch() ตรง signature", 4, ok1 and ok2, why1 or why2)
    await fetch_db_checks(c)
    want = ["RowData_users", "RowData_orders", "RowData_products"]
    if ok2:
        r = await c.call("main_fetch")
        same("main_fetch() คืน list ถูกต้องตามลำดับ", 2, r, want, c, list)
        timing("ทำงานพร้อมกัน ใช้เวลา ≤ 1.8 วิ", 2, r, 1.4, 1.8, c)
    else:
        c.add("main_fetch() คืน list ถูกต้องตามลำดับ", 2, False, why2)
        c.add("ทำงานพร้อมกัน ใช้เวลา ≤ 1.8 วิ", 2, False, why2)
    g = c.uses("gather")
    c.add("ใช้ asyncio.gather()", 2, g, "" if g else "โจทย์ข้อนี้กำหนดให้ใช้ asyncio.gather()")


async def t_q4(c):
    ok1, why1 = c.fn("fetch_db_record", ["table_name", "latency"])
    ok2, why2 = c.fn("main_fetch_wait", [])
    c.add("fetch_db_record(table_name, latency) และ main_fetch_wait() ตรง signature", 4, ok1 and ok2, why1 or why2)
    await fetch_db_checks(c)
    want = {"RowData_users", "RowData_orders", "RowData_products"}
    if ok2:
        r = await c.call("main_fetch_wait")
        same("main_fetch_wait() คืน set ถูกต้อง", 2, r, want, c, set)
        timing("ทำงานพร้อมกัน ใช้เวลา ≤ 1.8 วิ", 2, r, 1.4, 1.8, c)
    else:
        c.add("main_fetch_wait() คืน set ถูกต้อง", 2, False, why2)
        c.add("ทำงานพร้อมกัน ใช้เวลา ≤ 1.8 วิ", 2, False, why2)
    w, t = c.uses("wait"), c.uses("create_task")
    c.add("ใช้ asyncio.create_task() + asyncio.wait()", 2, w and t,
          "" if w and t else ("ยังไม่ได้ใช้ asyncio.wait()" if not w else "ยังไม่ได้สร้าง Task ด้วย asyncio.create_task()"))
    if c.uses("gather"):
        c.add("ไม่ใช้ gather ในข้อนี้", 0, False, "ข้อนี้ให้เปลี่ยนมาใช้ asyncio.wait() แทน gather")


async def t_q5(c):
    oks = [c.fn(n, []) for n in ("fetch_task_a", "fetch_task_b", "process_and_sort")]
    bad = next((why for ok, why in oks if not ok), "")
    c.add("ประกาศ fetch_task_a, fetch_task_b, process_and_sort เป็น async def", 2, not bad, bad)
    parts = []
    good = True
    for name, want, sec in (("fetch_task_a", [42, 12, 88], 1.0), ("fetch_task_b", [5, 67, 23], 1.5)):
        if name not in c.ns:
            good = False
            parts.append(f"ไม่พบ {name}")
            continue
        r = await c.call(name)
        fine = not r.err and r.value == want and sec - 0.1 <= r.elapsed <= sec + 0.3
        good = good and fine
        parts.append(f"{name}() → {r.err or repr(r.value)} ใน {r.elapsed:.2f} วิ" + ("" if fine else f" (ควรได้ {want} หลัง {sec} วิ)"))
    c.add("fetch_task_a / fetch_task_b คืนค่าและรอเวลาถูกต้อง", 3, good, "\n".join(parts))
    want = [5, 12, 23, 42, 67, 88]
    if "process_and_sort" in c.ns:
        r = await c.call("process_and_sort")
        timing("รันพร้อมกัน ใช้เวลา ≤ 1.8 วิ", 3, r, 1.4, 1.8, c)
        same("คืน list ที่รวมแล้วเรียงน้อยไปมาก", 5, r, want, c, list)
    else:
        c.add("รันพร้อมกัน ใช้เวลา ≤ 1.8 วิ", 3, False, "ไม่พบ process_and_sort")
        c.add("คืน list ที่รวมแล้วเรียงน้อยไปมาก", 5, False, "ไม่พบ process_and_sort")
    g = c.uses("gather")
    c.add("ใช้ asyncio.gather()", 2, g, "" if g else "โจทย์ข้อนี้กำหนดให้ใช้ asyncio.gather()")


async def t_q6(c):
    ok1, why1 = c.fn("fetch_pokemon", ["pokemon_name"])
    ok2, why2 = c.fn("get_pokemons_info", [])
    c.add("fetch_pokemon(pokemon_name) และ get_pokemons_info() เป็น async def", 3, ok1 and ok2, why1 or why2)
    if ok1:
        c.net.calls.clear()
        r = await c.call("fetch_pokemon", "pikachu")
        urls = [x["url"] for x in c.net.calls]
        good_url = urls == ["https://pokeapi.co/api/v2/pokemon/pikachu"]
        c.add("ยิง GET ไปที่ URL ถูกต้องผ่าน aiohttp/httpx", 2, good_url,
              f"URL ที่เรียก: {urls}" if urls else (r.err or "ยังไม่มีการเรียก HTTP เลย"))
        same("fetch_pokemon('pikachu') → {'name': 'pikachu', 'type': 'electric'}", 4, r,
             {"name": "pikachu", "type": "electric"}, c, dict)
        r2 = await c.call("fetch_pokemon", "gengar")
        same("ตัวที่มี 2 type: fetch_pokemon('gengar') → type แรก 'ghost'", 3, r2,
             {"name": "gengar", "type": "ghost"}, c, dict)
    else:
        for label, pts in (("ยิง GET ไปที่ URL ถูกต้องผ่าน aiohttp/httpx", 2),
                           ("fetch_pokemon('pikachu') → {'name': 'pikachu', 'type': 'electric'}", 4),
                           ("ตัวที่มี 2 type: fetch_pokemon('gengar') → type แรก 'ghost'", 3)):
            c.add(label, pts, False, why1)
    want = [{"name": "ditto", "type": "normal"}, {"name": "pikachu", "type": "electric"},
            {"name": "charizard", "type": "fire"}]
    if ok2:
        c.net.calls.clear()
        r = await c.call("get_pokemons_info")
        same("get_pokemons_info() คืน list 3 ตัวตามลำดับ", 4, r, want, c, list)
        timing("ดึง 3 ตัวพร้อมกัน (≤ 1.3 วิ, ถ้าทีละตัวจะ ~2.2 วิ)", 2, r, 0.8, 1.3, c)
    else:
        c.add("get_pokemons_info() คืน list 3 ตัวตามลำดับ", 4, False, why2)
        c.add("ดึง 3 ตัวพร้อมกัน (≤ 1.3 วิ, ถ้าทีละตัวจะ ~2.2 วิ)", 2, False, why2)
    g = c.uses("gather")
    c.add("ใช้ asyncio.gather()", 2, g, "" if g else "โจทย์ข้อนี้กำหนดให้ใช้ asyncio.gather()")


TESTS = {"q1": t_q1, "q2": t_q2, "q3": t_q3, "q4": t_q4, "q5": t_q5, "q6": t_q6}


# ─────────────────────────── จุดเข้า: รันไฟล์ แล้วตรวจ

async def check(src, qid):
    res = {"error": None, "lint": [], "tests": [], "runTime": 0, "stderr": []}
    try:
        tree = ast.parse(src, "main.py")
        names = import_names(tree)
        res["lint"] = lint(tree)
        code = compile(transform(ast.parse(src, "main.py"), names), "main.py", "exec",
                       flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
    except SyntaxError as e:
        res["error"] = fmt_syntax(e)
        return json.dumps(res)

    net = Net()
    sys.modules["aiohttp"] = make_aiohttp(net)
    sys.modules["httpx"] = make_httpx(net)
    sys.modules["requests"] = make_requests()
    ns = {"__name__": "__main__", "__file__": "main.py", "__builtins__": builtins}

    emit({"event": "run-start"})
    with Capture(True) as run:
        t0 = time.perf_counter()
        try:
            out = eval(code, ns)
            if inspect.iscoroutine(out):
                await asyncio.wait_for(out, LIMIT)
        except asyncio.TimeoutError:
            res["error"] = {"kind": "timeout", "message": f"ไฟล์รันนานเกิน {LIMIT:.0f} วินาที", "line": None, "hint": ""}
        except BaseException as e:
            res["error"] = fmt_exc(e)
        res["runTime"] = time.perf_counter() - t0
        gc.collect()
    emit({"event": "run-end", "t": res["runTime"]})

    res["stderr"] = [t for _, t in run.errs]
    ctx = Ctx(ns, tree, names, run, net)
    try:
        await TESTS[qid](ctx)
    except Exception as e:
        ctx.add("ตัวตรวจทำงานไม่จบ", 0, False, f"{type(e).__name__}: {e}")
    res["tests"] = ctx.tests
    return json.dumps(res)
`;

const WORKER_SRC = `
let py = null;
self.pyEmit = (s) => postMessage({ type: "emit", data: JSON.parse(s) });
self.onmessage = async (e) => {
  const m = e.data;
  if (m.type === "init") {
    try {
      importScripts(m.base + "pyodide.js");
      py = await loadPyodide({ indexURL: m.base });
      await py.runPythonAsync(m.harness);
      postMessage({ type: "ready" });
    } catch (err) {
      postMessage({ type: "fatal", message: String(err && err.message || err) });
    }
  } else if (m.type === "run") {
    try {
      py.globals.set("_src", m.code);
      py.globals.set("_qid", m.qid);
      const out = await py.runPythonAsync("await check(_src, _qid)");
      postMessage({ type: "done", id: m.id, result: JSON.parse(out) });
    } catch (err) {
      postMessage({ type: "done", id: m.id, result: { error: { kind: "internal", message: String(err && err.message || err) }, tests: [], lint: [] } });
    }
  }
};
`;

// ตัวควบคุมฝั่งหน้าเว็บ: เปิด worker, ส่งโค้ดไปรัน, หยุด worker ถ้าค้างเกินเวลา
class PyRunner {
  constructor({ onStatus, onEmit }) {
    this.onStatus = onStatus;
    this.onEmit = onEmit;
    this.worker = null;
    this.ready = false;
    this.pending = null;
    this.seq = 0;
  }

  start() {
    this.ready = false;
    this.onStatus("loading");
    const url = URL.createObjectURL(new Blob([WORKER_SRC], { type: "text/javascript" }));
    this.worker = new Worker(url);
    this.worker.onmessage = (e) => this.handle(e.data);
    this.worker.onerror = (e) => this.onStatus("fatal", e.message || "Worker error");
    this.worker.postMessage({ type: "init", base: PYODIDE_URL, harness: PY_HARNESS });
  }

  handle(m) {
    if (m.type === "ready") {
      this.ready = true;
      this.onStatus("ready");
    } else if (m.type === "fatal") {
      this.onStatus("fatal", m.message);
    } else if (m.type === "emit") {
      this.onEmit(m.data);
    } else if (m.type === "done" && this.pending && this.pending.id === m.id) {
      clearTimeout(this.pending.timer);
      const { resolve } = this.pending;
      this.pending = null;
      resolve(m.result);
    }
  }

  run(code, qid, timeoutMs = 45000) {
    return new Promise((resolve) => {
      const id = ++this.seq;
      const timer = setTimeout(() => {
        // โค้ดค้าง (เช่น while True ที่ไม่มี await) — ทิ้ง worker แล้วเริ่มใหม่
        this.worker.terminate();
        this.pending = null;
        resolve({
          error: { kind: "timeout", message: "โค้ดค้างนานเกินไปจึงถูกหยุด — มีลูปไม่รู้จบ หรือลูปที่ไม่มี await หรือเปล่า?", line: null, hint: "" },
          tests: [], lint: [], stderr: [],
        });
        this.start();
      }, timeoutMs);
      this.pending = { id, resolve, timer };
      this.worker.postMessage({ type: "run", id, code, qid });
    });
  }
}

window.PyRunner = PyRunner;
