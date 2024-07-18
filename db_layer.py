import asyncpg
import geojson
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
            return await con.fetchrow("SELECT file_name FROM route WHERE id=$1", route_id)
        
    @classmethod
    async def get_route_geojson(cls, file_name):
        route_file = open("routes/" + file_name)
        geojson_route_data = dict(geojson.load(route_file))
        route_file.close()
        return geojson_route_data




    