from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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


@app.get("/vehicle_location/{vehicle_id}")
async def get_vehicle_location(vehicle_id: int):
    entry = await app.state.db.fetchrow("""SELECT * FROM vehicle_location WHERE vehicle_id=$1
                         """, vehicle_id)
    
    return {'longitude': entry["longitude"], "latitude" : entry["latitude"]}

@app.post("/vehicle_location")
async def post_vehicle_location(vehicle_location_data: vehicle_location):
    vehicle_id, latitude, longitude = vehicle_location_data.id, vehicle_location_data.latitude, vehicle_location_data.longitude
    await app.state.db.execute("""INSERT INTO vehicle_location 
                               (vehicle_id, latitude, longitude) VALUES ($1, $2, $3)""", vehicle_id, latitude, longitude)


@app.put("/vehicle_location")
async def post_vehicle_location(vehicle_location_data: vehicle_location):
    vehicle_id, latitude, longitude = vehicle_location_data.id, vehicle_location_data.latitude, vehicle_location_data.longitude
    await app.state.db.execute("UPDATE vehicle_location SET longitude=$1, latitude=$2 WHERE vehicle_id=$3", longitude, latitude, vehicle_id)
    

# Automatically redirect requests for "/" to react
app.mount("/", StaticFiles(directory="my-app/build", html=True), name="React-Project")

