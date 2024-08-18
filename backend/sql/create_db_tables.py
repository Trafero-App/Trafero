import asyncio
import asyncpg
import os 
from dotenv import load_dotenv, find_dotenv

async def recreate_tables():
    load_dotenv(find_dotenv())

    db = await asyncpg.connect(os.getenv("db_url"))

    await db.execute(open("backend/sql/schema.sql").read())    
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(recreate_tables())