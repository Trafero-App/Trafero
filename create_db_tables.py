import psycopg2
import os 
from dotenv import load_dotenv, find_dotenv

def recreate_tables():
    load_dotenv(find_dotenv())

    conn = psycopg2.connect(database=os.getenv("db_name"),
                            user=os.getenv("db_user"),
                            host= os.getenv("db_host"),
                            password = os.getenv("db_password"),
                            port = int(os.getenv("db_port"))
                            )

    cur = conn.cursor()

    cur.execute(open("sql/schema.sql").read())

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    recreate_tables()