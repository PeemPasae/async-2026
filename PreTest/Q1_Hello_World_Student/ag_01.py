import asyncio

async def say_hello():
	print(f'Hello')
	await asyncio.sleep(1.5)
	print(f'World')

asyncio.run(say_hello())