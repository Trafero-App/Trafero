from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager
import asyncpg
import os
from dotenv import load_dotenv, find_dotenv

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

# Automatically redirect requests for "/" to react
app.mount("/", StaticFiles(directory="my-app/build", html=True), name="React-Project")

