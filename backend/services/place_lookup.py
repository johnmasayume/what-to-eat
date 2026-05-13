import re
from typing import Optional
from urllib.parse import unquote, urlparse

import httpx

_HEADERS = {"User-Agent": "what-to-eat-app/1.0 (internal lunch picker)"}
_NOMINATIM = "https://nominatim.openstreetmap.org/reverse"


async def _resolve_url(url: str) -> str:
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10) as client:
            r = await client.get(url, headers=_HEADERS)
            return str(r.url)
    except Exception:
        return url


def _extract_name(url: str) -> Optional[str]:
    path = urlparse(url).path
    if "/maps/place/" in path:
        segment = path.split("/maps/place/")[1].split("/")[0]
        name = unquote(segment).replace("+", " ").strip()
        return name or None
    return None


def _extract_coords(url: str) -> Optional[tuple[float, float]]:
    m = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    return (float(m.group(1)), float(m.group(2))) if m else None


async def _reverse_geocode(lat: float, lng: float) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                _NOMINATIM,
                params={"lat": lat, "lon": lng, "format": "json"},
                headers=_HEADERS,
            )
        return r.json().get("display_name")
    except Exception:
        return None


async def lookup_place(maps_url: str) -> dict:
    canonical = await _resolve_url(maps_url)
    name = _extract_name(canonical)

    address = None
    coords = _extract_coords(canonical)
    if coords:
        address = await _reverse_geocode(*coords)

    return {"name": name, "address": address}
