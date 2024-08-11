import asyncpg
import geojson
from validation_classes import Account_DB_Entry
from typing import Literal

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
        if res is None: return None
        return {"longitude": res["longitude"], "latitude": res["latitude"]}
    
    
    @classmethod
    async def add_vehicle_location(cls, vehicle_id, latitude, longitude):
        async with cls.db_pool.acquire() as con: 
            return await con.execute("""INSERT INTO vehicle_location 
                                (vehicle_id, latitude, longitude) VALUES ($1, $2, $3)""", vehicle_id, latitude, longitude)
        
    @classmethod
    async def update_vehicle_location(cls, vehicle_id, latitude, longitude):
        async with cls.db_pool.acquire() as con:
            res =  await con.execute("""UPDATE vehicle_location SET longitude=$1, 
                                                latitude=$2 WHERE vehicle_id=$3""", longitude, latitude, vehicle_id)
            return res != "UPDATE 0"

    @classmethod
    async def get_route_file_name(cls, route_id):
        async with cls.db_pool.acquire() as con:
            return await con.fetchrow("SELECT file_name FROM route WHERE id=$1", route_id)["file_name"]

    @classmethod
    async def get_all_routes_data(cls):
        async with cls.db_pool.acquire() as con:
            routes_data = [
                            {"route_id": record[0], "file_name": record[1], "route_name": record[2],
                             "description": record[3], "working_hours": record[4], "active_days": record[5],
                             "company_name": record[6], "expected_price":record[7], "phone_number":record[8],"distance":record[9],"estimated_travel_time":record[10], 
                             "route_type": record[11]}
                            for record in await con.fetch("""SELECT id, file_name, route_name, description,
                                                          working_hours, active_days, company_name, expected_price,
                                                          company_phone_number, distance, estimated_travel_time, route_type FROM route""")
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
                                     WHERE vehicle.cur_route_id=$1""", route_id)
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
                                        (status, type, brand, model, license_plate, color, cur_route_id)
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
    async def get_vehicles_search_info(cls):
        async with cls.db_pool.acquire() as con:
            result = await con.fetch("""SELECT (id, license_plate, status) FROM vehicle""")
        return [tuple(record[0]) for record in result]
    
    @classmethod
    async def get_route_waypoints(cls, route_id):
        async with cls.db_pool.acquire() as con:
            result = await con.fetch("""SELECT (longitude, latitude, projection_index) FROM waypoint WHERE route_id = $1
                                     ORDER BY id""", route_id)
        result = [tuple(record[0]) for record in result]
        return result
    
    @classmethod
    async def get_account_info(cls, username, account_type: Literal["passenger", "vehicle"]):
        async with cls.db_pool.acquire() as con:
            if account_type == "passenger":
                res = await con.fetchrow("SELECT * FROM passenger WHERE username=$1", username)
            else:
                res = await con.fetchrow("SELECT * FROM vehicle WHERE username=$1", username)
        if res is None: return None
        return {"id": res["id"], "username": res["username"], "password_hash": res["password_hash"], "first_name": res["first_name"],
                "last_name": res["last_name"], "phone_number": res["phone_number"], "type": account_type}
            
    @classmethod
    async def get_vehicle_route_id(cls, vehicle_id):
        async with cls.db_pool.acquire() as con:
            res = await con.fetch("SELECT cur_route_id from vehicle WHERE id = $1", vehicle_id)
        return res[0][0]

    @classmethod
    async def add_feedback(cls, passenger_id, vehicle_id, review):
        async with cls.db_pool.acquire() as con:
            return await con.execute("""INSERT INTO feedback (passenger_id, vehicle_id, reaction, complaint)
                                         VALUES ($1, $2, $3, $4)""", passenger_id, vehicle_id, review.reaction, review.complaint)


    @classmethod
    async def get_account_password_hash(cls, username, account_type: Literal["passenger", "vehicle"]):
        async with cls.db_pool.acquire() as con:
            res = await con.fetchrow("SELECT password_hash FROM account WHERE username=$1 AND account_type=$2", username, account_type)
        if res is None: return None
        return {"password_hash": res[0]}
    
    @classmethod 
    async def check_phone_number_available(cls, phone_number, account_type: Literal["passenger", "vehicle"]):
        async with cls.db_pool.acquire() as con:
            if account_type == "passenger":
                res = await con.fetchrow("SELECT * FROM passenger WHERE phone_number=$1", phone_number)
            else:
                res = await con.fetchrow("SELECT * FROM vehicle WHERE phone_number=$1", phone_number)
        if res is None: return True
        else: return False
    
    @classmethod 
    async def check_username_available(cls, username, account_type: Literal["passenger", "vehicle"]):
        async with cls.db_pool.acquire() as con:
            if account_type == "passenger":
                res = await con.fetchrow("SELECT * FROM passenger WHERE username=$1", username)
            else:
                res = await con.fetchrow("SELECT * FROM vehicle WHERE username=$1", username)
        if res is None: return True
        else: return False
    
    @classmethod 
    async def check_email_available(cls, email, account_type: Literal["passenger", "vehicle"]):
        async with cls.db_pool.acquire() as con:
            if account_type == "passenger":
                res = await con.fetchrow("SELECT * FROM passenger WHERE email=$1", email)
            else:
                res = await con.fetchrow("SELECT * FROM vehicle WHERE email=$1", email)
        if res is None: return True
        else: return False
    
    @classmethod
    async def add_account(cls, account_info: Account_DB_Entry):
        async with cls.db_pool.acquire() as con:
            if account_info.account_type == "passenger":
                account_id = await con.fetch("""INSERT INTO passenger (username, password_hash, first_name,
                            last_name, phone_number, email)
                            VALUES ($1, $2, $3, $4, $5, $6) RETURNING id""", account_info.username, account_info.password_hash,
                            account_info.first_name, account_info.last_name, account_info.phone_number, account_info.email)
            else:
                account_id = (await con.fetch("""INSERT INTO vehicle (username, password_hash, first_name,
                            last_name, phone_number, email, cur_route_id, status, license_plate)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) RETURNING id""", account_info.username,
                            account_info.password_hash, account_info.first_name, account_info.last_name, account_info.phone_number,
                            account_info.email, account_info.cur_route_id, account_info.status, account_info.license_plate))[0][0]
                for route_id in account_info.routes:
                    await con.execute("""INSERT INTO vehicle_routes (vehicle_id, route_id) VALUES ($1, $2)""", account_id, route_id)

            
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
        
    @classmethod
    async def get_stations(cls):
        async with cls.db_pool.acquire() as con:
            res = await con.fetch("SELECT (route_id, station_name, longitude, latitude) FROM station")
            return [{"route_id": station_info[0][0], "station_name": station_info[0][1], 
                     "longitude": station_info[0][2], "latitude": station_info[0][3]} for station_info in res]
        
    @classmethod
    async def get_vehicle_routes(cls, vehicle_id):
        async with cls.db_pool.acquire() as con:
            res = await con.fetch("SELECT route_id FROM vehicle_routes WHERE vehicle_id=$1", vehicle_id)
        return [record[0] for record in res]
    
    @classmethod
    async def change_active_route(cls, vehicle_id, new_active_route):
        async with cls.db_pool.acquire() as con:
            await con.execute("UPDATE vehicle SET cur_route_id=$1 WHERE id=$2", new_active_route, vehicle_id)

    @classmethod
    async def add_route(cls, vehicle_id, new_route_id):
        async with cls.db_pool.acquire() as con:
            await con.execute("INSERT INTO vehicle_routes (vehicle_id, route_id) VALUES ($1, $2)", vehicle_id, new_route_id)

    @classmethod
    async def delete_vehicle_route(cls, vehicle_id, route_id):
        async with cls.db_pool.acquire() as con:
            res = await con.execute("DELETE FROM vehicle_routes WHERE vehicle_id=$1 AND route_id=$2", vehicle_id, route_id)
        return res != "DELETE 0"
        


    @classmethod
    async def update_status(cls, vehicle_id, new_status):
        async with cls.db_pool.acquire() as con:
            res = await con.execute("UPDATE vehicle SET status=$1 WHERE id=$2", new_status, vehicle_id)
        if res == "UPDATE 0": return False
        else: return True


    @classmethod 
    async def get_intersections(cls):
        async with cls.db_pool.acquire() as con:
            res = await con.fetch("SELECT (route_id, local_index, auxiliary_route, auxiliary_index) FROM intersection")
            return [(intersection_info[0][0], intersection_info[0][1], 
                     intersection_info[0][2], intersection_info[0][3]) for intersection_info in res]
        
