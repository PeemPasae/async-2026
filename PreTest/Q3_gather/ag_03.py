import asyncio

async def fetch_db_record(table_name: str, latency: float):
    """
    Coroutine ดึงข้อมูลจากฐานข้อมูลสมมติ:
    1. await asyncio.sleep(latency)
    2. return f"RowData_{table_name}"
    """

    await asyncio.sleep(latency)
    return f"RowData_{table_name}"
	
async def main_fetch():
	
	result = await asyncio.gather(
		
		fetch_db_record("users", 1.0),
		fetch_db_record("orders", 1.5),
		fetch_db_record("products", 0.5)
	)
	
	return result
	
if __name__=="__main__":
	
	print(asyncio.run(main_fetch()))