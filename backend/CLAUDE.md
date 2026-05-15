# Backend

FastAPI + SQLAlchemy + SQLite. Runs on a home server exposed via Tailscale Funnel (HTTPS).

## Run locally

```bash
cd backend
uvicorn main:app --reload --port 9912
# API at http://localhost:9912
# Also serves frontend/index.html at GET /
```

## Production hosting

Tailscale Funnel proxies port 9912 to a public HTTPS URL:

```bash
tailscale funnel 9912
```

No Caddy, no port-forward, no router config needed.

## File map

```
backend/
├── main.py              # App entry point — wires router, CORS, static file serving, runs migrations
├── database.py          # Engine, SessionLocal, Base, run_migrations()
├── models.py            # SQLAlchemy Place model
├── schemas.py           # Pydantic schemas: PlaceCreate, PlaceOut, PlaceUpdate, LookupOut
├── routes/
│   └── places.py        # All CRUD + /today + /recommend + /lookup
└── services/
    └── place_lookup.py  # Resolves Maps URL → name + address via URL parsing + Nominatim
```

## Database

SQLite file: `backend/what_to_eat.db`

`models.Base.metadata.create_all()` runs on startup (creates table if not exists). New columns are added via `run_migrations()` in `database.py`, which wraps each `ALTER TABLE ADD COLUMN` in a try/except — SQLite raises an error if the column already exists, which is silently swallowed.

### Place schema

| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| name | String | Required |
| maps_url | String UNIQUE | Duplicate key — exact match |
| address | String nullable | From Nominatim reverse geocode |
| parking_difficulty | String | `"easy"` or `"hard"` |
| days_closed | String | Comma-separated day names e.g. `"Saturday,Sunday"`. Empty string = open daily. |
| budget_min | Integer | RM |
| budget_max | Integer | RM |
| has_epp | Boolean | Company discount available |
| submitted_by | String | Free-text name, no auth |
| created_at | DateTime | UTC |
| notes | String nullable | Free-text notes about the place |
| shop_images | JSON (TEXT) | List of image URLs `["url1", "url2"]`. SQLAlchemy JSON type auto-serialises. |
| menu_images | JSON (TEXT) | Same as shop_images |

### Days closed logic

`today_name()` uses `Asia/Kuala_Lumpur` timezone explicitly (via `zoneinfo`). The server might run UTC — using server-local time would give wrong results between midnight and 8am MYT.

## API endpoints

| Method | Path | Notes |
|--------|------|-------|
| GET | `/api/places/` | All places, newest first |
| GET | `/api/places/today` | Filtered by `is_open()` — today not in days_closed |
| GET | `/api/places/recommend?country=` | Random place open today, filtered by country if provided. Falls back to all if no match. |
| GET | `/api/places/lookup?maps_url=` | Returns `{name, address, canonical_url, is_duplicate}`. Used before add form shows. |
| POST | `/api/places/` | 409 if maps_url already exists |
| PUT | `/api/places/{id}` | Partial update via `exclude_unset=True`. 409 on maps_url conflict. |
| DELETE | `/api/places/{id}` | 204 no content |

Route order matters in FastAPI: `/today`, `/recommend`, `/lookup` are registered before `/{place_id}` so they are never swallowed by the path parameter route.

## Place lookup flow

`GET /api/places/lookup?maps_url=<url>`

1. Follow redirects on the URL (handles `goo.gl/maps/` short links) → canonical URL
2. Extract place name from `/maps/place/<name>/` path segment
3. Extract `@lat,lon` from URL with regex
4. Call Nominatim reverse geocode to get human-readable address
5. Return `{name, address, canonical_url, is_duplicate: false}` (or `{is_duplicate: true}` if maps_url already in DB)

`canonical_url` is the resolved URL with place name + place ID — frontend stores this instead of the raw input so Maps links open the full place card with images.

Nominatim requires a `User-Agent` header — set to `what-to-eat-app/1.0 (internal lunch picker)`.

## Schemas

- `days_closed` is a plain `str` in all schemas (the frontend joins/splits it)
- `shop_images` / `menu_images` are `list[str]` in schemas. `PlaceOut` has a `field_validator` that converts `None` → `[]` for rows that predate these columns.
- `PlaceUpdate` uses all-Optional fields; the route applies only fields present via `exclude_unset=True`.

## Dependencies

```
fastapi
uvicorn
sqlalchemy
pydantic
httpx
tzdata
```

`tzdata` required on Windows — `zoneinfo` has no bundled timezone data there. Install: `pip install tzdata`.

No external API keys. No paid services.
