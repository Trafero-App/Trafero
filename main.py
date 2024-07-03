from fastapi import FastAPI
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


@app.get("/vehicle_location/{vehicle_id}")
async def get_vehicle_location(vehicle_id: int):
    entry = await app.state.db.fetchrow("SELECT * FROM vehicle_location WHERE vehicle_id=$1", vehicle_id)
    if entry is None:
        return {"found" : False, "longitude": None, "latitude" : None}
    return {"found" : True, "longitude": entry["longitude"], "latitude" : entry["latitude"]}

@app.post("/vehicle_location")
async def post_vehicle_location(vehicle_location_data: vehicle_location):
    vehicle_id, latitude, longitude = vehicle_location_data.id, vehicle_location_data.latitude, vehicle_location_data.longitude
    try:
        await app.state.db.execute("""INSERT INTO vehicle_location 
                               (vehicle_id, latitude, longitude) VALUES ($1, $2, $3)""", vehicle_id, latitude, longitude)
        return {"added" : True}
    except asyncpg.exceptions.UniqueViolationError:
        return {"added" : False, "error":"UniqueViolationError"}
    except asyncpg.exceptions.ForeignKeyViolationError:
        return {"added" : False, "error":"ForeignKeyViolationError"}


@app.put("/vehicle_location")
async def post_vehicle_location(vehicle_location_data: vehicle_location):
    vehicle_id, latitude, longitude = vehicle_location_data.id, vehicle_location_data.latitude, vehicle_location_data.longitude
    result = await app.state.db.execute("""UPDATE vehicle_location SET longitude=$1, 
                                        latitude=$2 WHERE vehicle_id=$3""", longitude, latitude, vehicle_id)
    # False signifies that you tried to update the location of a vehicle whose location isn't in the db yet
    if result == "UPDATE 0":
        return {"updated" : False}
    else:
        return {"updated" : True}
