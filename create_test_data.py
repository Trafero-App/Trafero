import asyncpg
import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from create_db_tables import recreate_tables
async def main():
    recreate_tables()

    load_dotenv(find_dotenv())
    db = await asyncpg.connect(os.getenv("db_url"))

    """
    passenger:
    =====================================================================
    | id | user_name | password  | first_name | last_name | phone_number|
    =====================================================================
    | 1  | User1     | User1pass | User1first | User1last | 11111111    |
    ---------------------------------------------------------------------
    | 2  | User2     | User2pass | User2first | User2last | 22222222    |
    ---------------------------------------------------------------------
    | 4  | User4     | User4pass | User4first | User4last | 44444444    |
    ---------------------------------------------------------------------
    | 5  | User5     | User5pass | User5first | User5last | 55555555    |
    =====================================================================

    route:
    =========================
    | id | file_name        |
    =========================
    | 1  | bus_15_1.geojson |
    -------------------------
    | 2  | bus_15_2.geojson |
    -------------------------
    | 3  | van_sea_road.geojson |
    =========================


    vehicle:
    ================================
    | id | route_id | phone_number |
    ================================ 
    | 1  | 2        | 11111112     |
    -------------------------------- 
    | 2  | 2        | 11111113     |
    -------------------------------- 
    | 3  | 2        | 11111114     |
    -------------------------------- 
    | 4  | 1        | 11111115     |
    ================================
    vehicle_location: 
    ==========================================
    | id | longitude | latitude | vehicle_id |
    ==========================================
    | 1  | 35.5149   | 33.8966  | 1          |
    ------------------------------------------
    | 2  | 35.5119   | 33.8979  | 3          |
    ------------------------------------------
    | 3  | 35.5295   | 33.8987  | 2          |
    ------------------------------------------
    | 4  | 35.5276   | 33.8990  | 4          |
    ==========================================

    """
    await db.execute("""INSERT INTO passenger 
                     (user_name, password, first_name, last_name, phone_number) VALUES
                     ('User1', 'User1pass', 'User1first', 'User1last', '11111111'),
                     ('User2', 'User2pass', 'User2first', 'User2last', '22222222'),
                     ('UserDUD', 'X', 'X', 'X', '90'),
                     ('User4', 'User4pass', 'User4first', 'User4last', '44444444'),
                     ('User5', 'User5pass', 'User5first', 'User5last', '55555555');


                     DELETE FROM passenger WHERE id=3;

                    INSERT INTO route (file_name) VALUES 
                     ('bus_15_1.geojson'), ('bus_15_2.geojson'), ('van_sea_road.geojson');

                    INSERT INTO vehicle (route_id, phone_number) VALUES 
                     (2, '11111112'), (2, '11111113'), (2, '11111114'), (1, '11111115');
                     INSERT INTO vehicle_location (longitude, latitude, vehicle_id) VALUES
                    (35.5149, 33.8966, 1),
                    (35.5119, 33.8979, 3),
                    (35.5295, 33.8987, 2),
                    (35.5276, 33.8990, 4);
                     """)
    
    
    await db.close()



if __name__ == "__main__":
    asyncio.run(main())