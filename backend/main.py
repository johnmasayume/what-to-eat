import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import models
from database import engine
from routes.places import router as places_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="What to Eat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(places_router)

# Serve frontend index.html at root (local dev)
_frontend = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(_frontend):

    @app.get("/")
    def index():
        return FileResponse(os.path.join(_frontend, "index.html"))
