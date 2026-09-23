import asyncio

async def print_message(message, delay):
	
	await asyncio.sleep(delay)
	print(message)
	
async def main_tack():

	task1 = await asyncio.create_task(print_message("A", 1.0))
	task2 = await asyncio.create_task(print_message("B", 2.0))
	
	
if __name__=="__main__":
	
    asyncio.run(main_tack())