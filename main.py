from fastapi import FastAPI, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
import asyncpg
import os
from dotenv import load_dotenv, find_dotenv

from pydantic import BaseModel


# For data validation
class vehicle_location(BaseModel):
    id: int
    latitude: float
    longitude: float


# Get access credentials to database
load_dotenv(find_dotenv())
DB_URL = os.getenv("db_url")

# Open connection to database when app starts up
# and close the connection when the app shuts down
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = await asyncpg.connect(DB_URL)
    yield
    await app.state.db.close()


app = FastAPI(lifespan=lifespan)

# Allow only specific origins to make requests
origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # allow requests from the specified origins
    allow_credentials=True, # allow credentials to be sent (e.g cookies)
    allow_methods=["*"], # allow POST, GET, PUT ... `*` is "all"
    allow_headers=["*"]

)


@app.get("/vehicle_location/{vehicle_id}", status_code=status.HTTP_200_OK)
async def get_vehicle_location(vehicle_id: int, response: Response):
    entry = await app.state.db.fetchrow("SELECT * FROM vehicle_location WHERE vehicle_id=$1", vehicle_id)
    if entry is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"Message" : "Error: Vehicle location is not available."}
    
    
    return {"longitude": entry["longitude"], "latitude" : entry["latitude"], "Message": "All Good 👍"}

@app.post("/vehicle_location", status_code=status.HTTP_200_OK)
async def post_vehicle_location(vehicle_location_data: vehicle_location, response: Response):
    vehicle_id, latitude, longitude = vehicle_location_data.id, vehicle_location_data.latitude, vehicle_location_data.longitude
    try:
        await app.state.db.execute("""INSERT INTO vehicle_location 
                               (vehicle_id, latitude, longitude) VALUES ($1, $2, $3)""", vehicle_id, latitude, longitude)
        return {"Message": "All Good 👍"}
    except asyncpg.exceptions.UniqueViolationError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
                "Message":
                """Error: You have attempted to add the location of a vehicle who's location has already been added. Maybe you meant to send a PUT request?"""
                }
    except asyncpg.exceptions.ForeignKeyViolationError:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Message": "Error: You have attempted to add the location of a vehicle that doesn't exist."}


@app.put("/vehicle_location", status_code=status.HTTP_200_OK)
async def post_vehicle_location(vehicle_location_data: vehicle_location, response: Response):
    vehicle_id, latitude, longitude = vehicle_location_data.id, vehicle_location_data.latitude, vehicle_location_data.longitude
    result = await app.state.db.execute("""UPDATE vehicle_location SET longitude=$1, 
                                        latitude=$2 WHERE vehicle_id=$3""", longitude, latitude, vehicle_id)
    # False signifies that you tried to update the location of a vehicle whose location isn't in the db yet
    if result == "UPDATE 0":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"Message" : """Error: You have attempted to update the location of a vehicle who's location hasn't been added.
                            Maybe you mean to send a POST request?"""}
    else:
        return {"Message": "All Good 👍"}
