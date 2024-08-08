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
            res = await con.fetchrow("SELECT * FROM vehicle_location WHERE vehicle_id=$1", vehicle_id)
        return {"longitude": res["longitude"], "latitude": res["latitude"]}
    
    
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
            routes_data = [
                            {"route_id": record[0], "file_name": record[1], "route_name": record[2], "description": record[3]}
                            for record in await con.fetch("SELECT id, file_name, name, description FROM route")
                          ]
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
            res = await con.fetch("""SELECT
                                     (vehicle.id, vehicle_location.longitude, vehicle_location.latitude, vehicle.status, vehicle.license_plate)
                                     FROM vehicle JOIN vehicle_location ON vehicle.id = vehicle_location.vehicle_id
                                     WHERE vehicle.route_id=$1""", route_id)
        if res is None: return None
        return [{"id": vehicle_info[0][0], "longitude": vehicle_info[0][1], 
                 "latitude": vehicle_info[0][2], "status": vehicle_info[0][3], "license_plate": vehicle_info[0][4]} for vehicle_info in res]

    @classmethod
    async def get_all_vehicles_info(cls):
        async with cls.db_pool.acquire() as con:
            res = await con.fetch("""SELECT (vehicle.id, vehicle_location.longitude, vehicle_location.latitude, vehicle.status)
                                  FROM vehicle JOIN vehicle_location ON vehicle.id = vehicle_location.vehicle_id""")
        if res is None: return None
        return [{"id": vehicle_info[0][0], "longitude": vehicle_info[0][1], 
                 "latitude": vehicle_info[0][2], "status": vehicle_info[0][3]} for vehicle_info in res]
    @classmethod
    async def get_vehicle_details(cls, vehicle_id):
        details = {"id": vehicle_id}
        async with cls.db_pool.acquire() as con:
            vehicle_info = await con.fetchrow("""SELECT
                                        (status, type, brand, model, license_plate, color, route_id)
                                        FROM vehicle WHERE id=$1""", vehicle_id)
            if vehicle_info is None: return None
            vehicle_info = vehicle_info[0]

            coords = await cls.get_vehicle_location(vehicle_id)
            feedback = await cls.get_vehicle_feedbacks(vehicle_id)

            details["status"] = vehicle_info[0]
            details["coordinates"] = [coords["longitude"], coords["latitude"]]
            details["vehicle"] = {
                "type" : vehicle_info[1],
                "brand" : vehicle_info[2],
                "model" : vehicle_info[3],
                "license_plate" : vehicle_info[4],
                "color" : vehicle_info[5]
            }
            details["feedback"] = feedback
            details["route_id"] = vehicle_info[6]
            
        return details
    @classmethod
    async def get_route_waypoints(cls, route_id):
        async with cls.db_pool.acquire() as con:
            result = await con.fetch("""SELECT (longitude, latitude, projection_index) FROM waypoint WHERE route_id = $1
                                     ORDER BY id""", route_id)
        result = [tuple(record[0]) for record in result]
        return result
    
    @classmethod
    async def get_vehicle_route_id(cls, vehicle_id):
        async with cls.db_pool.acquire() as con:
            res = await con.fetch("SELECT route_id from vehicle WHERE id = $1", vehicle_id)
        return res[0][0]

    @classmethod
    async def add_feedback(cls, passenger_id, vehicle_id, review):
        async with cls.db_pool.acquire() as con:
            return await con.execute("""INSERT INTO feedback (passenger_id, vehicle_id, reaction, complaint)
                                         VALUES ($1, $2, $3, $4)""", passenger_id, vehicle_id, review.reaction, review.complaint)


    @classmethod
    async def update_feedback(cls, passenger_id, vehicle_id, review):
        async with cls.db_pool.acquire() as con:
            return await con.execute("""UPDATE feedback SET reaction=$3, complaint=$4 
                                        WHERE passenger_id=$1 AND vehicle_id=$2""", passenger_id, vehicle_id, review.reaction, review.complaint)
        
    @classmethod
    async def remove_feedback(cls, passenger_id, vehicle_id):
        async with cls.db_pool.acquire() as con:
            return await con.execute("""DELETE FROM feedback WHERE passenger_id=$1 AND vehicle_id=$2""", passenger_id, vehicle_id)
        
    @classmethod
    async def remove_passenger_feedbacks(cls, passenger_id):
        async with cls.db_pool.acquire() as con:
            return await con.execute("""DELETE FROM feedback WHERE passenger_id=$1""", passenger_id)
        
    @classmethod
    async def remove_vehicle_feedbacks(cls,vehicle_id):
        async with cls.db_pool.acquire() as con:
            return await con.execute("""DELETE FROM feedback WHERE vehicle_id=$1""",vehicle_id)    
        
    @classmethod
    async def get_all_feedbacks(cls):
        async with cls.db_pool.acquire() as con:
            res = await con.fetch("SELECT (passenger_id, vehicle_id, reaction, complaint) FROM feedback")
            if res is None: return None
            return [{"passenger_id": feedback_info[0][0], "vehicle_id": feedback_info[0][1],
                     "reaction": feedback_info[0][2], "complaint": feedback_info[0][3]} for feedback_info in res]
            
        
    @classmethod
    async def get_vehicle_feedbacks(cls, vehicle_id):
        async with cls.db_pool.acquire() as con:
            res = await con.fetch("SELECT (passenger_id, reaction, complaint) FROM feedback WHERE vehicle_id=$1", vehicle_id)
            if res is None: return None
            return [{"passenger_id": feedback_info[0][0],
                     "reaction": feedback_info[0][1], "complaint": feedback_info[0][2]} for feedback_info in res]
        
    @classmethod
    async def get_passenger_feedbacks(cls, passenger_id):
        async with cls.db_pool.acquire() as con:
            res = await con.fetch("SELECT (vehicle_id, reaction, complaint) FROM feedback WHERE passenger_id=$1", passenger_id)
            if res is None: return None
            return [{"vehicle_id": feedback_info[0][0],
                     "reaction": feedback_info[0][1], "complaint": feedback_info[0][2]} for feedback_info in res]
        
    @classmethod
    async def get_feedback(cls, passenger_id, vehicle_id):
        async with cls.db_pool.acquire() as con:
            res = await con.fetch("SELECT (reaction, complaint) FROM feedback WHERE passenger_id=$1 AND vehicle_id=$2", passenger_id, vehicle_id)
            if res is None: return None
            return [{"reaction": feedback_info[0][0], "complaint": feedback_info[0][1]} for feedback_info in res]
        