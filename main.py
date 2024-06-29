from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

# Automatically redirect requests for "/" to react
app.mount("/", StaticFiles(directory="my-app/build", html=True), name="React-Project")

