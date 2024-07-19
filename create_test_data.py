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
    -------------------------------- 
    | 5  | 1        | 11111116     |
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
    waypoint:
    ==========================================
    | id | longitude | latitude | route_id   |
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
                     (2, '11111112'), (2, '11111113'), (2, '11111114'), (1, '11111115'), (1, '11111116');
                     INSERT INTO vehicle_location (longitude, latitude, vehicle_id) VALUES
                    (35.5149, 33.8966, 1),
                    (35.5119, 33.8979, 3),
                    (35.5295, 33.8987, 2),
                    (35.5276, 33.8990, 4);
                     
                     INSERT INTO waypoint (longitude, latitude, route_id) VALUES 
                    (35.549770,33.893568, 1), (35.550345,33.893612, 1), (35.550257,33.893953, 1), (35.527903,33.899252, 1),
                    (35.512803,33.897313, 1), (35.501058,33.902061, 1), (35.494315,33.902217, 1),
                    (35.488325,33.901411, 1), (35.470759,33.899928, 1), (35.474010,33.886733, 1), (35.483601,33.882138, 1),
                    (35.495867,33.879112, 1), (35.506941,33.878175, 1), (35.512301,33.878567, 1), (35.522318,33.879707, 1),
                    (35.528226,33.882107, 1), (35.529695,33.883657, 1), (35.529864,33.881180, 1), (35.535424,33.878790, 1),
                    (35.537514,33.878331, 1), (35.542767,33.878814, 1), (35.540308,33.880782, 1), (35.540037,33.879629, 1);
                     """)
    
    
    await db.close()



if __name__ == "__main__":
    asyncio.run(main())