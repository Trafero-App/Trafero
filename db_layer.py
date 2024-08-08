import asyncpg
import geojson
from validation_classes import Account_DB_Entry
# load_dotenv(find_dotenv())
# DB_URL = os.getenv("db_url")

class db:
    @classmethod
    async def connect(cls, DB_URL):
        cls.db_pool = await asyncpg.create_pool(DB_URL)
        
    @classmethod
    async def disconnect(cls):
        await cls.db_pool.close()

    @classmethod
    async def get_vehicle_location(cls, vehicle_id):
        async with cls.db_pool.acquire() as con:
            return await con.fetchrow("SELECT * FROM vehicle_location WHERE vehicle_id=$1", vehicle_id)
    
    @classmethod
    async def add_vehicle_location(cls, vehicle_id, latitude, longitude):
        async with cls.db_pool.acquire() as con: 
            return await con.execute("""INSERT INTO vehicle_location 
                                (vehicle_id, latitude, longitude) VALUES ($1, $2, $3)""", vehicle_id, latitude, longitude)
        
    @classmethod
    async def update_vehicle_location(cls, vehicle_id, latitude, longitude):
        async with cls.db_pool.acquire() as con:
            return await con.execute("""UPDATE vehicle_location SET longitude=$1, 
                                                latitude=$2 WHERE vehicle_id=$3""", longitude, latitude, vehicle_id)

    @classmethod
    async def get_route_file_name(cls, route_id):
        async with cls.db_pool.acquire() as con:
            return await con.fetchrow("SELECT file_name FROM route WHERE id=$1", route_id)["file_name"]

    @classmethod
    async def get_all_routes_data(cls):
        async with cls.db_pool.acquire() as con:
            routes_data = [(record[0], record[1]) for record in (await con.fetch("SELECT id, file_name FROM route"))]
            return routes_data

    @classmethod
    async def get_route_geojson(cls, file_name):
        route_file = open("routes/" + file_name)
        geojson_route_data = dict(geojson.load(route_file))
        route_file.close()
        return geojson_route_data
    
    @classmethod
    async def get_route_vehicles(cls, route_id):
        
        async with cls.db_pool.acquire() as con: 
            res = await con.fetch("""SELECT (vehicle.id, vehicle_location.longitude, vehicle_location.latitude, vehicle.status)
                                     FROM vehicle JOIN vehicle_location ON vehicle.id = vehicle_location.vehicle_id
                                     WHERE vehicle.id=$1""", route_id)
        if res is None: return None
        return [{"vehicle_id": vehicle_info[0][0], "longitude": vehicle_info[0][1], 
                 "latitude": vehicle_info[0][2], "status": vehicle_info[0][1]} for vehicle_info in res]
        
    @classmethod
    async def get_route_waypoints(cls, route_id):
        async with cls.db_pool.acquire() as con:
            result = await con.fetch("""SELECT (longitude, latitude, projection_index) FROM waypoint WHERE route_id = $1
                                     ORDER BY id""", route_id)
        result = [tuple(record[0]) for record in result]
        print(result)
        return result
    
    @classmethod
    async def get_account_info(cls, username):
        async with cls.db_pool.acquire() as con:
            res = await con.fetchrow("SELECT * FROM account WHERE username=$1", username)
        if res is None: return None
        return {"username": res["username"], "password_hash": res["password_hash"], "first_name": res["first_name"],
                "last_name": res["last_name"], "phone_number": res["phone_number"]}
            

    @classmethod
    async def get_account_password_hash(cls, username, account_type):
        async with cls.db_pool.acquire() as con:
            res = await con.fetchrow("SELECT password_hash FROM account WHERE username=$1 AND account_type=$2", username, account_type)
        if res is None: return None
        return {"password_hash": res[0]}
    
    @classmethod 
    async def check_phone_number_available(cls, phone_number):
        async with cls.db_pool.acquire() as con:
            res = await con.fetchrow("SELECT * FROM account WHERE phone_number=$1", phone_number)
        if res is None: return True
        else: return False
    
    @classmethod 
    async def check_username_available(cls, username):
        print()
        print()
        print()
        print()
        print("KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK")
        async with cls.db_pool.acquire() as con:
            res = await con.fetchrow("SELECT * FROM account WHERE username=$1", username)
        print(res)
        print()
        print()
        print()
        if res is None: return True
        else: return False
    
    @classmethod
    async def add_account(cls, account_info: Account_DB_Entry):
        async with cls.db_pool.acquire() as con:
            account_id = await con.fetch("""INSERT INTO account (account_type, username, password_hash, first_name,
                          last_name, phone_number)
                          VALUES ($1, $2, $3, $4, $5, $6) RETURNING id""", account_info.account_type, account_info.username,
                          account_info.password_hash, account_info.first_name, account_info.last_name, account_info.phone_number)
            if type == "passenger":
                await con.execute("""INSERT INTO passenger (id) VALUES ($1)""", account_id)
            
        
