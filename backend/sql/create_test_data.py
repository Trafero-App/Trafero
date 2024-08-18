import asyncpg
import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from create_db_tables import recreate_tables
from time import sleep
async def main():
    print("Recreating db tables...")
    await recreate_tables()
    print("Done")
    sleep(0.5)
    
    load_dotenv(find_dotenv())
    db = await asyncpg.connect(os.getenv("db_url"))

    print("Entering test data...")
    
    await db.execute(open("backend/sql/test_data.sql").read())    
    
    print("Done")

    await db.close()



if __name__ == "__main__":
    asyncio.run(main())