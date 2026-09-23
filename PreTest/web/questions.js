// ข้อมูลโจทย์ทั้งหมด — ช่องว่างในโค้ดเขียนเป็น ⟦คำตอบ⟧ (คำตอบอื่นที่ยอมรับคั่นด้วย ‖)
// การตรวจจริงทำโดยรันโค้ด (ดู runner.js) ไม่ได้เทียบตัวอักษร

window.LEVEL_INFO = [
  { name: "เติมคำ", desc: "โค้ดครบเกือบหมด เหลือแค่คีย์เวิร์ดสำคัญให้เติม" },
  { name: "เติมบรรทัด", desc: "บางบรรทัดหายไปทั้งบรรทัด ต้องเขียนเองทั้งคำสั่ง" },
  { name: "เขียนฟังก์ชัน", desc: "มีโครงกับคอมเมนต์บอกขั้นตอน เขียนตัวฟังก์ชันเอง" },
  { name: "เหมือนสอบ", desc: "เหลือแค่โจทย์ — เขียนเองทั้งไฟล์เหมือนวันสอบ" },
];

window.QUESTIONS = [
  // ───────────────────────────── Q1
  {
    id: "q1",
    num: 1,
    title: "Hello World",
    topic: "async def · await asyncio.sleep",
    points: 5,
    brief: `
      <p>เขียนฟังก์ชัน asynchronous ชื่อ <code>say_hello()</code> ที่พิมพ์ข้อความตามลำดับ โดยหน่วงเวลาแบบ async</p>
      <ol>
        <li>สร้าง <code>async def say_hello():</code></li>
        <li>พิมพ์ <code>"Hello"</code></li>
        <li><code>await asyncio.sleep(1.5)</code> หน่วง 1.5 วินาที</li>
        <li>พิมพ์ <code>"World"</code></li>
      </ol>
      <p>แล้วสั่งรันด้วย <code>asyncio.run(...)</code></p>`,
    output: `Hello\n(รอ 1.5 วินาที)\nWorld`,
    rubric: [
      [2, "ประกาศ say_hello() และโครงสร้างโค้ดถูกต้อง"],
      [3, "ใช้ await asyncio.sleep(1.5) และรันได้ตรงเวลา"],
    ],
    hints: [
      "ฟังก์ชันที่ข้างในมี await ต้องประกาศด้วย async def",
      "asyncio.sleep() คืน coroutine — ต้องมี await ข้างหน้าถึงจะรอจริง",
      "บรรทัดสุดท้ายของไฟล์: asyncio.run(say_hello())",
    ],
    solution: `import asyncio


async def say_hello():
    print("Hello")
    await asyncio.sleep(1.5)
    print("World")


asyncio.run(say_hello())
`,
    levels: [
      `import ⟦asyncio⟧


⟦async⟧ def say_hello():
    print("Hello")
    ⟦await⟧ asyncio.⟦sleep⟧(1.5)
    print("World")


asyncio.⟦run⟧(say_hello())
`,
      `import asyncio


⟦async def say_hello():⟧
    print("Hello")
    ⟦await asyncio.sleep(1.5)⟧
    print("World")


⟦asyncio.run(say_hello())⟧
`,
      `import asyncio


async def say_hello():
    # 1) พิมพ์ "Hello"
    # 2) หน่วงเวลา 1.5 วินาทีแบบ async
    # 3) พิมพ์ "World"
    pass


# สั่งรัน say_hello() ด้วย asyncio
`,
      `# Q1: เขียน say_hello() ให้พิมพ์ Hello, รอ 1.5 วินาที, แล้วพิมพ์ World
`,
    ],
  },

  // ───────────────────────────── Q2
  {
    id: "q2",
    num: 2,
    title: "Tasks พร้อมกัน",
    topic: "asyncio.create_task",
    points: 5,
    brief: `
      <p>สร้าง coroutine แล้วรัน 2 งานพร้อมกันด้วย <code>asyncio.create_task()</code></p>
      <ol>
        <li><code>async def print_message(message, delay):</code> — <code>await asyncio.sleep(delay)</code> แล้ว <code>print(message)</code></li>
        <li><code>async def main_task():</code>
          <ul>
            <li>Task 1 เรียก <code>print_message("A", 1.0)</code></li>
            <li>Task 2 เรียก <code>print_message("B", 2.0)</code></li>
            <li><code>await</code> รอทั้งสอง Task จนเสร็จ</li>
          </ul>
        </li>
      </ol>`,
    output: `(ผ่านไป 1.0 วินาที)\nA\n(รวม 2.0 วินาที)\nB`,
    rubric: [
      [2, "ประกาศ print_message และ main_task ถูกต้อง"],
      [3, "สร้าง Task ให้ทำงานพร้อมกัน ได้ A แล้ว B ตรงเวลา (รวม ~2 วิ)"],
    ],
    hints: [
      "task = asyncio.create_task(coroutine) — งานจะเริ่มวิ่งทันทีที่ event loop ว่าง",
      "สร้าง task ครบทั้งสองตัวก่อน แล้วค่อย await ทีละตัว ถ้า await print_message(...) ตรง ๆ จะกลายเป็นทำทีละงาน (รวม 3 วิ)",
      "อย่าลืม asyncio.run(main_task()) ท้ายไฟล์",
    ],
    solution: `import asyncio


async def print_message(message, delay):
    await asyncio.sleep(delay)
    print(message)


async def main_task():
    task1 = asyncio.create_task(print_message("A", 1.0))
    task2 = asyncio.create_task(print_message("B", 2.0))

    await task1
    await task2


asyncio.run(main_task())
`,
    levels: [
      `import asyncio


⟦async⟧ def print_message(message, delay):
    await asyncio.sleep(⟦delay⟧)
    print(⟦message⟧)


async def main_task():
    task1 = asyncio.⟦create_task⟧(print_message("A", 1.0))
    task2 = asyncio.⟦create_task⟧(print_message(⟦"B"‖'B'⟧, ⟦2.0‖2⟧))

    ⟦await⟧ task1
    ⟦await⟧ task2


asyncio.run(⟦main_task()⟧)
`,
      `import asyncio


async def print_message(message, delay):
    ⟦await asyncio.sleep(delay)⟧
    ⟦print(message)⟧


async def main_task():
    ⟦task1 = asyncio.create_task(print_message("A", 1.0))⟧
    ⟦task2 = asyncio.create_task(print_message("B", 2.0))⟧

    ⟦await task1⟧
    ⟦await task2⟧


asyncio.run(main_task())
`,
      `import asyncio


async def print_message(message, delay):
    # รอ delay วินาที แล้วพิมพ์ message
    pass


async def main_task():
    # สร้าง task1 -> print_message("A", 1.0)
    # สร้าง task2 -> print_message("B", 2.0)
    # รอให้ทั้งสอง task เสร็จ
    pass


asyncio.run(main_task())
`,
      `# Q2: print_message(message, delay) + main_task() ที่รัน "A"(1.0s) กับ "B"(2.0s) พร้อมกันด้วย create_task
`,
    ],
  },

  // ───────────────────────────── Q3
  {
    id: "q3",
    num: 3,
    title: "ดึงข้อมูลด้วย gather",
    topic: "asyncio.gather · return ค่า",
    points: 10,
    brief: `
      <p>ดึงข้อมูลจากฐานข้อมูลสมมติ 3 ตารางพร้อมกันด้วย <code>asyncio.gather()</code></p>
      <ol>
        <li><code>async def fetch_db_record(table_name: str, latency: float):</code> — <code>await asyncio.sleep(latency)</code> แล้ว <code>return f"RowData_{table_name}"</code></li>
        <li><code>async def main_fetch():</code> เรียก 3 ตารางพร้อมกันผ่าน <code>asyncio.gather()</code>
          <ul>
            <li><code>"users"</code> latency 1.0 · <code>"orders"</code> latency 1.5 · <code>"products"</code> latency 0.5</li>
            <li>คืนค่าผลลัพธ์จาก gather เป็น <code>list</code></li>
          </ul>
        </li>
      </ol>`,
    output: `['RowData_users', 'RowData_orders', 'RowData_products']\n(รวม ~1.5 วินาที)`,
    rubric: [
      [4, "fetch_db_record และ main_fetch ตรงตาม signature"],
      [6, "ใช้ gather, คืน list ถูกต้อง, ใช้เวลาไม่เกิน 1.8 วิ"],
    ],
    hints: [
      "asyncio.gather(coro1, coro2, coro3) — ส่ง coroutine เป็น argument แยกกัน (ไม่ต้องใส่ใน list เว้นแต่ใช้ *)",
      "ต้อง await asyncio.gather(...) ถึงจะได้ list ของผลลัพธ์",
      "ผลลัพธ์ของ gather เรียงตามลำดับที่ส่งเข้าไป ไม่ใช่ตามลำดับที่เสร็จ",
    ],
    solution: `import asyncio


async def fetch_db_record(table_name: str, latency: float):
    await asyncio.sleep(latency)
    return f"RowData_{table_name}"


async def main_fetch():
    results = await asyncio.gather(
        fetch_db_record("users", 1.0),
        fetch_db_record("orders", 1.5),
        fetch_db_record("products", 0.5),
    )
    return results


if __name__ == "__main__":
    print(asyncio.run(main_fetch()))
`,
    levels: [
      `import asyncio


async def fetch_db_record(table_name: str, latency: float):
    await asyncio.sleep(⟦latency⟧)
    ⟦return⟧ f"RowData_{table_name}"


async def main_fetch():
    results = ⟦await⟧ asyncio.⟦gather⟧(
        fetch_db_record("users", 1.0),
        fetch_db_record(⟦"orders"‖'orders'⟧, ⟦1.5⟧),
        fetch_db_record("products", 0.5),
    )
    return ⟦results⟧


if __name__ == "__main__":
    print(asyncio.run(⟦main_fetch()⟧))
`,
      `import asyncio


async def fetch_db_record(table_name: str, latency: float):
    ⟦await asyncio.sleep(latency)⟧
    ⟦return f"RowData_{table_name}"⟧


async def main_fetch():
    ⟦results = await asyncio.gather(⟧
        ⟦fetch_db_record("users", 1.0),⟧
        ⟦fetch_db_record("orders", 1.5),⟧
        ⟦fetch_db_record("products", 0.5),⟧
    )
    return results


if __name__ == "__main__":
    ⟦print(asyncio.run(main_fetch()))⟧
`,
      `import asyncio


async def fetch_db_record(table_name: str, latency: float):
    """
    Coroutine ดึงข้อมูลจากฐานข้อมูลสมมติ:
    1. await asyncio.sleep(latency)
    2. return f"RowData_{table_name}"
    """
    await asyncio.sleep(latency)
    return f"RowData_{table_name}"


async def main_fetch():
    # ดึง users(1.0), orders(1.5), products(0.5) พร้อมกันด้วย asyncio.gather
    # แล้ว return list ผลลัพธ์
    pass


if __name__ == "__main__":
    print(asyncio.run(main_fetch()))
`,
      `# Q3: fetch_db_record(table_name, latency) + main_fetch() ใช้ asyncio.gather
`,
    ],
  },

  // ───────────────────────────── Q4
  {
    id: "q4",
    num: 4,
    title: "เปลี่ยนเป็น wait",
    topic: "create_task · asyncio.wait · done/pending",
    points: 10,
    brief: `
      <p>ทำแบบข้อ 3 แต่ใช้ <code>asyncio.wait()</code> แทน <code>asyncio.gather()</code></p>
      <ol>
        <li><code>fetch_db_record</code> เหมือนข้อ 3</li>
        <li><code>async def main_fetch_wait():</code>
          <ul>
            <li>สร้าง 3 Task ด้วย <code>asyncio.create_task()</code>: users 1.0 · orders 1.5 · products 0.5</li>
            <li><code>await asyncio.wait(...)</code> รอให้ทุก Task เสร็จ</li>
            <li>ดึงผลจาก <code>done</code> ด้วย <code>task.result()</code></li>
            <li>คืนค่าเป็น <code>set</code></li>
          </ul>
        </li>
      </ol>`,
    output: `{'RowData_users', 'RowData_orders', 'RowData_products'}\n(รวม ~1.5 วินาที)\n* set ไม่มีลำดับ — พิมพ์ออกมาสลับกันได้`,
    rubric: [
      [4, "fetch_db_record และ main_fetch_wait ตรงตาม signature"],
      [6, "ใช้ wait, คืน set ถูกต้อง, ใช้เวลาไม่เกิน 1.8 วิ"],
    ],
    hints: [
      "asyncio.wait() รับ Task (ไม่รับ coroutine ตรง ๆ ใน Python 3.11+) — ห่อด้วย asyncio.create_task() ก่อน",
      "asyncio.wait คืนค่า 2 ตัว: done, pending = await asyncio.wait(tasks)",
      "set comprehension: {task.result() for task in done}",
    ],
    solution: `import asyncio


async def fetch_db_record(table_name: str, latency: float):
    await asyncio.sleep(latency)
    return f"RowData_{table_name}"


async def main_fetch_wait():
    tasks = [
        asyncio.create_task(fetch_db_record("users", 1.0)),
        asyncio.create_task(fetch_db_record("orders", 1.5)),
        asyncio.create_task(fetch_db_record("products", 0.5)),
    ]

    done, pending = await asyncio.wait(tasks)

    return {task.result() for task in done}


if __name__ == "__main__":
    print(asyncio.run(main_fetch_wait()))
`,
    levels: [
      `import asyncio


async def fetch_db_record(table_name: str, latency: float):
    await asyncio.sleep(latency)
    return f"RowData_{table_name}"


async def main_fetch_wait():
    tasks = [
        asyncio.⟦create_task⟧(fetch_db_record("users", 1.0)),
        asyncio.⟦create_task⟧(fetch_db_record("orders", 1.5)),
        asyncio.create_task(fetch_db_record("products", 0.5)),
    ]

    ⟦done⟧, ⟦pending⟧ = await asyncio.⟦wait⟧(tasks)

    return {task.⟦result⟧() for task in ⟦done⟧}


if __name__ == "__main__":
    print(asyncio.run(main_fetch_wait()))
`,
      `import asyncio


async def fetch_db_record(table_name: str, latency: float):
    await asyncio.sleep(latency)
    return f"RowData_{table_name}"


async def main_fetch_wait():
    tasks = [
        ⟦asyncio.create_task(fetch_db_record("users", 1.0)),⟧
        ⟦asyncio.create_task(fetch_db_record("orders", 1.5)),⟧
        ⟦asyncio.create_task(fetch_db_record("products", 0.5)),⟧
    ]

    ⟦done, pending = await asyncio.wait(tasks)⟧

    ⟦return {task.result() for task in done}⟧


if __name__ == "__main__":
    print(asyncio.run(main_fetch_wait()))
`,
      `import asyncio


async def fetch_db_record(table_name: str, latency: float):
    """
    Coroutine ดึงข้อมูลจากฐานข้อมูลสมมติ:
    1. await asyncio.sleep(latency)
    2. return f"RowData_{table_name}"
    """
    await asyncio.sleep(latency)
    return f"RowData_{table_name}"


async def main_fetch_wait():
    # 1) สร้าง list ของ 3 tasks ด้วย asyncio.create_task
    # 2) done, pending = await asyncio.wait(...)
    # 3) return set ของ task.result() จาก done
    pass


if __name__ == "__main__":
    print(asyncio.run(main_fetch_wait()))
`,
      `# Q4: fetch_db_record(table_name, latency) + main_fetch_wait() ใช้ create_task + asyncio.wait คืนค่าเป็น set
`,
    ],
  },

  // ───────────────────────────── Q5
  {
    id: "q5",
    num: 5,
    title: "รวมผลแล้วเรียง",
    topic: "gather + unpack · รวม list · sorted",
    points: 15,
    brief: `
      <p>สร้าง coroutine 2 ตัวจำลองการดึงข้อมูล รันพร้อมกันด้วย <code>asyncio.gather()</code> แล้วเรียงตัวเลขจาก<strong>น้อยไปมาก</strong></p>
      <ol>
        <li><code>async def fetch_task_a():</code> — sleep 1.0 แล้ว return <code>[42, 12, 88]</code></li>
        <li><code>async def fetch_task_b():</code> — sleep 1.5 แล้ว return <code>[5, 67, 23]</code></li>
        <li><code>async def process_and_sort():</code> — gather ทั้งสอง, รวม list, เรียงน้อยไปมาก, return list</li>
      </ol>`,
    output: `[5, 12, 23, 42, 67, 88]\n(รวม ~1.5 วินาที)`,
    rubric: [
      [5, "fetch_task_a, fetch_task_b, process_and_sort ถูกต้อง"],
      [5, "ใช้ gather ทำงานพร้อมกัน ไม่เกิน 1.8 วิ"],
      [5, "รวมข้อมูลและเรียงน้อยไปมากถูกต้อง"],
    ],
    hints: [
      "gather คืน list ของผลลัพธ์ แตกใส่ 2 ตัวแปรได้เลย: a, b = await asyncio.gather(...)",
      "รวม list สองอันด้วย a + b",
      "sorted(x) คืน list ใหม่ที่เรียงแล้ว / x.sort() เรียงในที่แต่คืน None — ระวัง return x.sort()",
    ],
    solution: `import asyncio


async def fetch_task_a():
    await asyncio.sleep(1.0)
    return [42, 12, 88]


async def fetch_task_b():
    await asyncio.sleep(1.5)
    return [5, 67, 23]


async def process_and_sort():
    result_a, result_b = await asyncio.gather(fetch_task_a(), fetch_task_b())

    combined = result_a + result_b

    return sorted(combined)


if __name__ == "__main__":
    print(asyncio.run(process_and_sort()))
`,
    levels: [
      `import asyncio


async def fetch_task_a():
    await asyncio.sleep(⟦1.0‖1⟧)
    return [42, 12, 88]


async def fetch_task_b():
    await asyncio.sleep(1.5)
    return ⟦[5, 67, 23]⟧


async def process_and_sort():
    result_a, result_b = ⟦await⟧ asyncio.⟦gather⟧(fetch_task_a(), ⟦fetch_task_b()⟧)

    combined = result_a ⟦+⟧ result_b

    return ⟦sorted⟧(combined)


if __name__ == "__main__":
    print(asyncio.run(process_and_sort()))
`,
      `import asyncio


async def fetch_task_a():
    ⟦await asyncio.sleep(1.0)⟧
    ⟦return [42, 12, 88]⟧


async def fetch_task_b():
    ⟦await asyncio.sleep(1.5)⟧
    ⟦return [5, 67, 23]⟧


async def process_and_sort():
    ⟦result_a, result_b = await asyncio.gather(fetch_task_a(), fetch_task_b())⟧

    ⟦combined = result_a + result_b⟧

    ⟦return sorted(combined)⟧


if __name__ == "__main__":
    print(asyncio.run(process_and_sort()))
`,
      `import asyncio


async def fetch_task_a():
    # รอ 1.0 วินาที แล้วคืน [42, 12, 88]
    pass


async def fetch_task_b():
    # รอ 1.5 วินาที แล้วคืน [5, 67, 23]
    pass


async def process_and_sort():
    # 1) รัน fetch_task_a กับ fetch_task_b พร้อมกันด้วย gather
    # 2) รวมสอง list
    # 3) คืน list ที่เรียงน้อยไปมาก
    pass


if __name__ == "__main__":
    print(asyncio.run(process_and_sort()))
`,
      `# Q5: fetch_task_a(), fetch_task_b(), process_and_sort() — gather แล้วรวม+เรียงน้อยไปมาก
`,
    ],
  },

  // ───────────────────────────── Q6
  {
    id: "q6",
    num: 6,
    title: "PokéAPI",
    topic: "aiohttp · async with · parse JSON · gather",
    points: 20,
    brief: `
      <p>ดึงชื่อและประเภท (type) ของโปเกมอน 3 ตัวจาก PokéAPI พร้อมกันด้วย <code>aiohttp</code> + <code>asyncio.gather()</code></p>
      <ol>
        <li><code>async def fetch_pokemon(pokemon_name: str):</code>
          <ul>
            <li>GET <code>https://pokeapi.co/api/v2/pokemon/{pokemon_name}</code></li>
            <li>เอา Primary Type (ตัวแรกใน <code>types</code>)</li>
            <li>return <code>{"name": pokemon_name, "type": primary_type}</code></li>
          </ul>
        </li>
        <li><code>async def get_pokemons_info():</code> — gather <code>"ditto"</code>, <code>"pikachu"</code>, <code>"charizard"</code> แล้ว return list ตามลำดับ</li>
      </ol>
      <p class="note">ในเว็บนี้ <strong>จำลองอินเทอร์เน็ต</strong> ให้: ใช้ได้ทั้ง <code>aiohttp</code> และ <code>httpx</code> (AsyncClient) แต่ละคำขอหน่วง ~0.6–0.9 วิ</p>
      <details class="json-peek"><summary>โครง JSON ที่ได้กลับมา (ย่อ)</summary>
<pre>{
  "name": "charizard",
  "id": 6,
  "types": [
    {"slot": 1, "type": {"name": "fire",   "url": "..."}},
    {"slot": 2, "type": {"name": "flying", "url": "..."}}
  ],
  "weight": 905,
  ...
}</pre></details>`,
    output: `[{'name': 'ditto', 'type': 'normal'}, {'name': 'pikachu', 'type': 'electric'}, {'name': 'charizard', 'type': 'fire'}]`,
    rubric: [
      [5, "นิยามฟังก์ชันและโครงสร้าง async I/O ถูกต้อง"],
      [7, "ดึง API และ parse เอา primary type ได้ถูก"],
      [8, "ใช้ gather ดึง 3 ตัวพร้อมกันสำเร็จ"],
    ],
    hints: [
      "async with aiohttp.ClientSession() as session: แล้วซ้อน async with session.get(url) as response:",
      "response.json() เป็น coroutine ใน aiohttp → data = await response.json()",
      'types เป็น list: data["types"][0]["type"]["name"]',
    ],
    solution: `import asyncio
import aiohttp


async def fetch_pokemon(pokemon_name: str):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    primary_type = data["types"][0]["type"]["name"]

    return {"name": pokemon_name, "type": primary_type}


async def get_pokemons_info():
    results = await asyncio.gather(
        fetch_pokemon("ditto"),
        fetch_pokemon("pikachu"),
        fetch_pokemon("charizard"),
    )
    return results


if __name__ == "__main__":
    print(asyncio.run(get_pokemons_info()))
`,
    levels: [
      `import asyncio
import aiohttp


async def fetch_pokemon(pokemon_name: str):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"

    ⟦async⟧ with aiohttp.⟦ClientSession⟧() as session:
        async with session.⟦get⟧(url) as response:
            data = ⟦await⟧ response.⟦json⟧()

    primary_type = data["types"][⟦0⟧]["type"]["name"]

    return {"name": pokemon_name, "type": ⟦primary_type⟧}


async def get_pokemons_info():
    results = await asyncio.⟦gather⟧(
        fetch_pokemon("ditto"),
        fetch_pokemon("pikachu"),
        fetch_pokemon("charizard"),
    )
    return results


if __name__ == "__main__":
    print(asyncio.run(get_pokemons_info()))
`,
      `import asyncio
import aiohttp


async def fetch_pokemon(pokemon_name: str):
    ⟦url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"⟧

    ⟦async with aiohttp.ClientSession() as session:⟧
        ⟦async with session.get(url) as response:⟧
            ⟦data = await response.json()⟧

    ⟦primary_type = data["types"][0]["type"]["name"]⟧

    ⟦return {"name": pokemon_name, "type": primary_type}⟧


async def get_pokemons_info():
    ⟦results = await asyncio.gather(⟧
        fetch_pokemon("ditto"),
        fetch_pokemon("pikachu"),
        fetch_pokemon("charizard"),
    )
    return results


if __name__ == "__main__":
    print(asyncio.run(get_pokemons_info()))
`,
      `import asyncio
import aiohttp


async def fetch_pokemon(pokemon_name: str):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}"
    # 1) เปิด ClientSession แล้ว GET url
    # 2) แปลง response เป็น JSON
    # 3) เอา type แรกจาก data["types"]
    # 4) return {"name": ..., "type": ...}
    pass


async def get_pokemons_info():
    # gather: "ditto", "pikachu", "charizard" แล้ว return list
    pass


if __name__ == "__main__":
    print(asyncio.run(get_pokemons_info()))
`,
      `# Q6: fetch_pokemon(pokemon_name) ดึงจาก PokéAPI (aiohttp) + get_pokemons_info() ใช้ gather 3 ตัว
`,
    ],
  },
];
