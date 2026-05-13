import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response

load_dotenv()

import models
from database import engine
from routes.places import router as places_router
from services.google_places import API_KEY, PLACES_BASE

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="What to Eat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(places_router)


@app.get("/api/photos")
async def proxy_photo(ref: str = Query(...)):
    """Proxy Google Places photo so the API key stays server-side."""
    if not API_KEY:
        return Response(status_code=404)
    url = f"{PLACES_BASE}/{ref}/media?key={API_KEY}&maxHeightPx=400"
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            r = await client.get(url)
        return Response(
            content=r.content,
            media_type=r.headers.get("content-type", "image/jpeg"),
        )
    except Exception:
        return Response(status_code=502)


# Serve frontend index.html at root (local dev)
_frontend = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.isdir(_frontend):

    @app.get("/")
    def index():
        return FileResponse(os.path.join(_frontend, "index.html"))
