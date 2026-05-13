import os
from typing import Optional
from urllib.parse import unquote, urlparse

import httpx

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
PLACES_BASE = "https://places.googleapis.com/v1"


async def resolve_url(url: str) -> str:
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            r = await client.head(url)
            return str(r.url)
    except Exception:
        return url


def extract_name_from_url(url: str) -> Optional[str]:
    path = urlparse(url).path
    if "/maps/place/" in path:
        segment = path.split("/maps/place/")[1].split("/")[0]
        name = unquote(segment).replace("+", " ").strip()
        return name or None
    return None


async def lookup_place(maps_url: str) -> dict:
    if not API_KEY:
        return {"name": None, "address": None, "photo_reference": None}

    canonical = await resolve_url(maps_url)
    name_hint = extract_name_from_url(canonical)
    if not name_hint:
        return {"name": None, "address": None, "photo_reference": None}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"{PLACES_BASE}/places:searchText",
                headers={
                    "X-Goog-Api-Key": API_KEY,
                    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.photos",
                },
                json={"textQuery": f"{name_hint} Malaysia"},
            )
        data = r.json()
    except Exception:
        return {"name": name_hint, "address": None, "photo_reference": None}

    places = data.get("places", [])
    if not places:
        return {"name": name_hint, "address": None, "photo_reference": None}

    place = places[0]
    name = place.get("displayName", {}).get("text") or name_hint
    address = place.get("formattedAddress")
    photos = place.get("photos", [])
    photo_reference = photos[0].get("name") if photos else None

    return {"name": name, "address": address, "photo_reference": photo_reference}
