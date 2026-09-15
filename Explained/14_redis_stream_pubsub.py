"""
14 · Redis (redis.asyncio): GET/SET · Stream + Consumer Group · Pub/Sub
อ้างอิงงานในคลาส: Week9/student1–5, teacher_race_control.py, Week10/server.py, bot.py

ต้องมี:  pip install redis   และ Redis server ที่ localhost:6379
         (docker run --name redis-f1 -p 6379:6379 redis:alpine)
ถ้าไม่มี server ไฟล์จะแจ้งแล้วจบ — อ่านโค้ดกับคอมเมนต์แทนได้

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    decode_responses=True → ได้ str แทน bytes (ไม่ใส่จะได้ b'GREEN')

KEY–VALUE (สัญญาณปล่อยตัว f1:race:status)
    await r.set(key, value)   ·   await r.get(key) → str หรือ None

STREAM = log ต่อท้ายเรื่อย ๆ เก็บข้อมูลไว้ อ่านย้อนหลังได้
    await r.xadd(stream, {field: value}, maxlen=1000, approximate=True) → message id "1712345678901-0"
        maxlen: เก็บแค่ประมาณ 1000 ข้อความล่าสุด
    await r.xgroup_create(stream, group, id="$", mkstream=True)
        id="$" : กลุ่มเริ่มอ่านเฉพาะข้อความที่เข้ามา "หลังจากนี้"   id="0" : อ่านตั้งแต่ข้อความแรก
        mkstream=True : ถ้ายังไม่มี stream ให้สร้าง
        ถ้ามีกลุ่มอยู่แล้ว → ResponseError "BUSYGROUP" (จับแล้วข้ามได้)
    await r.xreadgroup(group, consumer, {stream: ">"}, count=1, block=1000)
        ">"      : ขอข้อความที่ยังไม่เคยส่งให้ใครในกลุ่มนี้
        count    : ขอกี่ข้อความ   block : ไม่มีข้อความ รอได้กี่ ms (ไม่มี = คืน [])
        คืนรูปแบบ [[stream, [(msg_id, {field: value}), ...]]]
        ★ ในกลุ่มเดียวกัน 1 ข้อความไปหา consumer "คนเดียว" (แบ่งงานกัน)
    await r.xack(stream, group, msg_id)   ยืนยันว่าประมวลผลเสร็จ

PUB/SUB = กระจายข่าวสด ไม่เก็บ ใครไม่ได้ฟังตอนนั้นก็พลาด
    await r.publish(channel, message)                → จำนวนผู้ฟังที่ได้รับ
    pubsub = r.pubsub(); await pubsub.subscribe(channel)
    async for msg in pubsub.listen():
        if msg["type"] == "message": msg["data"]     ← ข้าม type "subscribe" ที่มาเป็นอันแรก
    ★ ทุก subscriber ได้ทุกข้อความ

รัน:  python 14_redis_stream_pubsub.py
"""
import asyncio
import json
import sys

try:
    import redis.asyncio as redis
    from redis.exceptions import ResponseError
except ImportError:
    sys.exit("ไฟล์นี้ต้องติดตั้งก่อน:  pip install redis")

STREAM = "explain:telemetry"
GROUP = "pitwall"
CHANNEL = "explain:dashboard"


async def close(conn):
    closer = getattr(conn, "aclose", None) or conn.close     # redis 5+ ใช้ aclose
    await closer()


async def demo_key_value(r):
    print("=== 1) SET / GET ===")
    await r.set("explain:race:status", "RED")
    print("   status =", await r.get("explain:race:status"))
    await r.set("explain:race:status", "GREEN")
    print("   status =", await r.get("explain:race:status"))
    print("   key ที่ไม่มี =", await r.get("explain:nothing"))    # None


async def demo_stream(r):
    print("\n=== 2) Stream + Consumer Group ===")
    await r.delete(STREAM)                                      # เริ่มใหม่ทุกครั้งที่รันตัวอย่าง

    try:
        await r.xgroup_create(STREAM, GROUP, id="$", mkstream=True)
        print(f"   สร้างกลุ่ม '{GROUP}'")
    except ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise
    try:                                                        # สร้างซ้ำ → BUSYGROUP
        await r.xgroup_create(STREAM, GROUP, id="$", mkstream=True)
    except ResponseError as e:
        print(f"   สร้างซ้ำได้ error: {e}  ← จับแล้วข้ามได้")

    for i in range(1, 5):
        msg_id = await r.xadd(STREAM, {"speed": 200 + i * 10, "tire_wear": 20 * i}, maxlen=1000)
        print(f"   xadd → {msg_id}")

    # consumer 2 คนในกลุ่มเดียวกัน ผลัดกันอ่าน → ข้อความถูกแบ่ง ไม่ซ้ำกัน
    for consumer in ["engineer_A", "engineer_B", "engineer_A", "engineer_B"]:
        entries = await r.xreadgroup(GROUP, consumer, {STREAM: ">"}, count=1, block=500)
        for _stream, messages in entries:
            for msg_id, data in messages:
                tire = float(data["tire_wear"])                 # ค่าใน stream เป็น str เสมอ ต้องแปลง
                print(f"   {consumer} ได้ {msg_id} tire_wear={tire}")
                await r.xack(STREAM, GROUP, msg_id)

    entries = await r.xreadgroup(GROUP, "engineer_A", {STREAM: ">"}, count=1, block=300)
    print(f"   อ่านอีกครั้งตอนไม่มีข้อความใหม่ → {entries} (รอ block 300 ms แล้วคืนว่าง)")


async def demo_pubsub(r):
    print("\n=== 3) Pub/Sub ===")
    received = []

    async def listener(name):
        pubsub = r.pubsub()
        await pubsub.subscribe(CHANNEL)
        try:
            async for msg in pubsub.listen():
                if msg["type"] == "message":                  # ข้ามข้อความยืนยัน subscribe
                    packet = json.loads(msg["data"])
                    received.append((name, packet["speed"]))
        finally:
            await pubsub.unsubscribe(CHANNEL)
            await close(pubsub)

    count = await r.publish(CHANNEL, json.dumps({"speed": 999}))
    print(f"   publish ก่อนมีคนฟัง → ถึงผู้ฟัง {count} คน (ข้อความนี้หายไปเลย)")

    listeners = [asyncio.create_task(listener(n)) for n in ("dashboard", "teacher")]
    await asyncio.sleep(0.2)                                   # ให้ subscribe เสร็จก่อน

    for speed in (250, 260):
        count = await r.publish(CHANNEL, json.dumps({"speed": speed}))
        print(f"   publish speed={speed} → ถึงผู้ฟัง {count} คน")
    await asyncio.sleep(0.2)

    for t in listeners:
        t.cancel()
    await asyncio.gather(*listeners, return_exceptions=True)
    print(f"   ผู้ฟังได้รับ: {sorted(received)}  ← ทุกคนได้ทุกข้อความ")


async def main():
    r = redis.Redis(host="localhost", port=6379, decode_responses=True, socket_connect_timeout=1)
    try:
        await r.ping()
    except (OSError, redis.ConnectionError, redis.TimeoutError):
        print("ต่อ Redis ที่ localhost:6379 ไม่ได้ — เปิด Redis server ก่อน หรืออ่านโค้ดกับคอมเมนต์ในไฟล์นี้แทน")
        await close(r)
        return
    try:
        await demo_key_value(r)
        await demo_stream(r)
        await demo_pubsub(r)
    finally:
        await r.delete(STREAM, "explain:race:status")
        await close(r)


if __name__ == "__main__":
    asyncio.run(main())

# ─── สรุป ───────────────────────────────────────────────────────────────────
# • decode_responses=True ไม่งั้นได้ bytes · ค่าจาก stream เป็น str ต้อง float()/int()
# • Stream: xadd → xgroup_create(id="$", mkstream=True) → xreadgroup(">") → xack
# • consumer ชื่อต่างกันในกลุ่มเดียวกัน = แบ่งข้อความกัน (ไม่ใช่ทุกคนได้ครบ)
# • Pub/Sub: publish ↔ subscribe + listen · ทุกคนได้ครบ แต่ไม่เก็บย้อนหลัง
