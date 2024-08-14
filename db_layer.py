import asyncpg
import geojson
from validation import Account_DB_Entry, Review_DB_Entry
from typing import Literal

class db:
    @classmethod
    async def connect(cls, DB_URL):
        cls.db_pool = await asyncpg.create_pool(DB_URL)
        await cls.store_all_routes_data()
        
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
            old_location = await con.fetchrow("SELECT (longitude, latitude) FROM vehicle_location WHERE vehicle_id=$1", vehicle_id)
            if old_location is None: return False
            old_long, old_lat = old_location[0]
            await con.execute("INSERT INTO vehicle_location_history (vehicle_id, old_long, old_lat, new_long, new_lat) VALUES ($1, $2, $3, $4, $5)",
                              vehicle_id, old_long, old_lat, longitude, latitude)
            res =  await con.execute("""UPDATE vehicle_location SET longitude=$1, 
                                                latitude=$2 WHERE vehicle_id=$3""", longitude, latitude, vehicle_id)
            return res != "UPDATE 0"


    @classmethod
    async def store_all_routes_data(cls):
        routes = {}
        routes_search_data = []
        routes_data = await db.get_all_routes_data()
        for route_data in routes_data:        
            route_data = {"details": route_data}
            route_geojson = await db.get_route_geojson(route_data["details"]["file_name"])
            del route_data["details"]["file_name"]
            route_data["line"] = route_geojson
            routes[route_data["details"]["route_id"]] = route_data

            routes_search_data.append(((route_data["details"]["route_id"],) + tuple(route_data["details"]["description"].split(' - '))))
        cls.routes = routes
        cls.routes_search_data = routes_search_data


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
            feedback = await cls.get_vehicle_feedback(vehicle_id)

            details["status"] = vehicle_info[0]
            details["coordinates"] = [coords["longitude"], coords["latitude"]]
            details["vehicle"] = {
                "type" : vehicle_info[1],
                "brand" : vehicle_info[2],
                "model" : vehicle_info[3],
                "license_plate" : vehicle_info[4],
                "color" : vehicle_info[5]
            }
            details["route_id"] = vehicle_info[6]
            for key, value in feedback.items():
                details[key] = value
            
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
    async def get_account_info_by_email(cls, identifier, account_type: Literal["passenger", "vehicle"]):
        async with cls.db_pool.acquire() as con:
            if account_type == "passenger":
                res = await con.fetchrow("SELECT * FROM passenger WHERE email=$1", identifier)
                if res is None: return None
                res = dict(res)
                res["account_type"] = "passenger"
            else:
                res = await con.fetchrow("SELECT * FROM vehicle WHERE email=$1", identifier)
                if res is None: return None
                res = dict(res)
                route_list = await con.fetch("SELECT route_id FROM vehicle_routes WHERE vehicle_id=$1", res["id"])
                route_list = [record[0] for record in route_list]
                res["route_list"] = route_list
                res["account_type"] = "vehicle"
        return res
             
    
    @classmethod
    async def get_account_info_by_phone_number(cls, identifier, account_type: Literal["passenger", "vehicle"]):
        async with cls.db_pool.acquire() as con:
            if account_type == "passenger":
                res = await con.fetchrow("SELECT * FROM passenger WHERE phone_number=$1", identifier)
                if res is None: return None
                res = dict(res)
                res["account_type"] = "passenger"
            else:
                res = await con.fetchrow("SELECT * FROM vehicle WHERE phone_number=$1", identifier)
                if res is None: return None
                res = dict(res)
                route_list = await con.fetch("SELECT route_id FROM vehicle_routes WHERE vehicle_id=$1", res["id"])
                route_list = [record[0] for record in route_list]
                res["route_list"] = route_list
                res["account_type"] = "vehicle"
        return res
    
    @classmethod
    async def get_account_info_by_id(cls, user_id, account_type: Literal["passenger", "vehicle"]):
        async with cls.db_pool.acquire() as con:
            if account_type == "passenger":
                res = await con.fetchrow("SELECT * FROM passenger WHERE id=$1", user_id)
                if res is None: return None
                res = dict(res)
                res["account_type"] = "passenger"
            else:
                res = await con.fetchrow("SELECT * FROM vehicle WHERE id=$1", user_id)
                if res is None: return None
                res = dict(res)
                route_list = await con.fetch("SELECT route_id FROM vehicle_routes WHERE vehicle_id=$1", user_id)
                route_list = [record[0] for record in route_list]
                res["route_list"] = route_list
                res["account_type"] = "vehicle"

        return res
    
    @classmethod
    async def get_vehicle_route_id(cls, vehicle_id):
        async with cls.db_pool.acquire() as con:
            res = await con.fetch("SELECT cur_route_id from vehicle WHERE id = $1", vehicle_id)
        return res[0][0]

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
                await (con.execute("""INSERT INTO passenger (password_hash, first_name,
                            last_name, date_of_birth, phone_number, email)
                            VALUES ($1, $2, $3, $4, $5, $6) RETURNING id""", account_info.password_hash,
                            account_info.first_name, account_info.last_name, account_info.date_of_birth,
                            account_info.phone_number, account_info.email))[0][0]
            else:
                account_id = (await con.fetch("""INSERT INTO vehicle (password_hash, first_name,
                            last_name, date_of_birth, phone_number, email, cur_route_id, "status",
                            "type", brand, model, license_plate, color)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) RETURNING id""", account_info.password_hash,
                            account_info.first_name, account_info.last_name, account_info.date_of_birth, account_info.phone_number,
                            account_info.email, account_info.cur_route_id, account_info.status, account_info.vehicle_type,
                            account_info.brand, account_info.model, account_info.license_plate, account_info.vehicle_color))[0][0]
                for route_id in account_info.routes:
                    await con.execute("""INSERT INTO vehicle_routes (vehicle_id, route_id) VALUES ($1, $2)""", account_id, route_id)
            return account_id
    @classmethod
    async def get_fixed_complaints_list(cls):
        async with cls.db_pool.acquire() as con:
            res = await con.fetch("""SELECT * FROM fixed_complaint""")
        return [tuple(record) for record in res]

    @classmethod
    async def add_complaints(cls, review_data, feedback_id):
        async with cls.db_pool.acquire() as con:
            fixed_complaints_list = await cls.get_fixed_complaints_list()
            complaint_to_id = {record[1]: record[0] for record in fixed_complaints_list}
            for complaint in review_data.complaints:
                complaint_id = complaint_to_id.get(complaint, -1)
                if complaint_id != -1:
                    await con.execute("""INSERT INTO feedback_fixed_complaint (feedback_id, fixed_complaint_id) VALUES ($1, $2)""", feedback_id, complaint_id)
                    
                else:
                    await con.execute("INSERT INTO other_complaint (feedback_id, complaint_details) VALUES ($1, $2)", feedback_id, complaint)


    @classmethod
    async def add_feedback(cls, review_data: Review_DB_Entry):
        async with cls.db_pool.acquire() as con:
            print(review_data)
            feedback_id = await con.fetch("""INSERT INTO feedback (passenger_id, vehicle_id, reaction) VALUES ($1, $2, $3) RETURNING id""",
                                    review_data.passenger_id, review_data.vehicle_id, review_data.reaction)
            print("y")
            feedback_id = feedback_id[0][0]
            if review_data.reaction == "thumbs_down":
                await cls.add_complaints(review_data, feedback_id)

    @classmethod
    async def update_feedback(cls, review_data: Review_DB_Entry):
        async with cls.db_pool.acquire() as con:
            success = await cls.delete_feedback(review_data.passenger_id, review_data.vehicle_id)

            if not success:
                return False
            await cls.add_feedback(review_data)
            return True
        
    @classmethod
    async def delete_feedback(cls, passenger_id, vehicle_id):
        async with cls.db_pool.acquire() as con:
            res = await con.execute("DELETE FROM feedback WHERE passenger_id=$1 AND vehicle_id=$2", 
                        passenger_id, vehicle_id)
            if res == "DELETE 0": return False
            else: return True

    @classmethod
    async def get_passenger_reaction(cls, passenger_id, vehicle_id):
        async with cls.db_pool.acquire() as con:
            feedback = await con.fetchrow("""SELECT id, reaction FROM feedback WHERE passenger_id=$1 AND vehicle_id=$2""", passenger_id, vehicle_id)
            if feedback is None: return {"reaction": None}
            return {"reaction": feedback[1]}
    
    @classmethod
    async def get_vehicle_feedback(cls, vehicle_id):
        async with cls.db_pool.acquire() as con: 
            thumbs_up_count = (await con.fetchrow("SELECT COUNT(*) FROM feedback WHERE vehicle_id=$1 AND reaction='thumbs_up'", vehicle_id))[0]
            thumbs_down_count = (await con.fetchrow("SELECT COUNT(*) FROM feedback WHERE vehicle_id=$1 AND reaction='thumbs_down'", vehicle_id))[0]
            fixed_complaints = await con.fetch("""SELECT fixed_complaint.complaint_details, COUNT(*) FROM feedback JOIN feedback_fixed_complaint
                                                  ON feedback.id = feedback_fixed_complaint.feedback_id JOIN fixed_complaint
                                                 ON feedback_fixed_complaint.fixed_complaint_id = fixed_complaint.id
                                                 WHERE feedback.vehicle_id=$1 GROUP BY fixed_complaint.complaint_details ORDER BY COUNT(*) DESC""", vehicle_id)
            
            complaints = []
            for complaint, count in fixed_complaints:
                complaints.append({"complaint": complaint, "count": count})
            return {"thumbs_up": thumbs_up_count, "thumbs_down": thumbs_down_count,
                    "complaints": complaints }
            

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
            res = await con.execute("UPDATE vehicle SET cur_route_id=$1 WHERE id=$2", new_active_route, vehicle_id)
        return res != "UPDATE 0"

    @classmethod
    async def set_route(cls, vehicle_id, new_routes):
        async with cls.db_pool.acquire() as con:
            await con.execute("DELETE FROM vehicle_routes WHERE vehicle_id=$1", vehicle_id)
            for new_route_id in new_routes:
                await con.execute("INSERT INTO vehicle_routes (vehicle_id, route_id) VALUES ($1, $2)", vehicle_id, new_route_id)

    @classmethod
    async def delete_vehicle_route(cls, vehicle_id, route_id):
        async with cls.db_pool.acquire() as con:
            res = await con.execute("DELETE FROM vehicle_routes WHERE vehicle_id=$1 AND route_id=$2", vehicle_id, route_id)
        return res != "DELETE 0"
        


    @classmethod
    async def update_status(cls, vehicle_id, new_status):
        async with cls.db_pool.acquire() as con:
            # To keep track of status history
            old_status_res = (await con.fetchrow("SELECT status FROM vehicle WHERE id=$1", vehicle_id))
            if old_status_res == None: return False
            old_status = old_status_res[0]
            await con.execute("INSERT INTO vehicle_status_history (vehicle_id, old_status, new_status) VALUES ($1, $2, $3)",
                            vehicle_id, old_status, new_status)

            res = await con.execute("UPDATE vehicle SET status=$1 WHERE id=$2", new_status, vehicle_id)

            return res != "UPDATE 0"
            
            


    @classmethod 
    async def get_intersections(cls):
        async with cls.db_pool.acquire() as con:
            res = await con.fetch("SELECT (route_id, local_index, auxiliary_route, auxiliary_index) FROM intersection")
            return [(intersection_info[0][0], intersection_info[0][1], 
                     intersection_info[0][2], intersection_info[0][3]) for intersection_info in res]
        
