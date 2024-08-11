import asyncpg
import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from create_db_tables import recreate_tables
async def main():
    recreate_tables()

    load_dotenv(find_dotenv())
    db = await asyncpg.connect(os.getenv("db_url"))

    await db.execute(open("sql/test_data.sql").read())    
    
    await db.close()



if __name__ == "__main__":
    asyncio.run(main())