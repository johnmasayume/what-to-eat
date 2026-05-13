# what-to-eat

A lunch place picker for the team — crowdsourced restaurant entries with daily recommendations.

## What it does

- Team members add restaurant/place info (name, Maps link, parking, days closed, budget, EPP)
- Home page shows today's random recommendation + all places open today
- All Places page lets you browse, filter, edit, and delete entries
- Duplicate detection via Google Maps URL (exact match)
- Place name and address auto-filled from Maps URL (no API key needed)

## Tech Stack

- **Frontend**: Vue 3 via CDN, single `index.html`, hosted on GitHub Pages
- **Backend**: FastAPI + SQLite, hosted on home server behind Caddy (HTTPS + DDNS)
- **Place lookup**: URL parsing + Nominatim (OpenStreetMap) reverse geocoding — no API key, no cost

## Local Dev

```bash
cd backend
uvicorn main:app --reload
# visit http://localhost:8000
```

Frontend is served by FastAPI at `/` during local dev. In production, GitHub Pages serves the same `index.html`.

The `API_BASE` in `index.html` auto-switches between `localhost` and the production DDNS domain.
Before deploying to GitHub Pages, replace `YOUR_DDNS_DOMAIN_HERE` in `frontend/index.html`.

## Project Structure

```
what-to-eat/
├── backend/
│   ├── main.py              # FastAPI app + static file serving
│   ├── models.py            # SQLite Place model
│   ├── database.py          # SQLAlchemy + SQLite setup
│   ├── schemas.py           # Pydantic request/response models
│   ├── routes/
│   │   └── places.py        # Place CRUD + today filter + recommend
│   └── services/
│       └── place_lookup.py  # URL parsing + Nominatim reverse geocode
├── frontend/
│   └── index.html           # Vue 3 CDN single-page app
└── CLAUDE.md
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/places/` | All places |
| GET | `/api/places/today` | Places open today (filtered by day of week) |
| GET | `/api/places/recommend` | Random place open today |
| GET | `/api/places/lookup?maps_url=` | Auto-fill name/address, check duplicate |
| POST | `/api/places/` | Create a place (409 if duplicate Maps URL) |
| PUT | `/api/places/{id}` | Update a place |
| DELETE | `/api/places/{id}` | Delete a place |

## Key Decisions

- No login — user enters their name on submission only
- Duplicate detection by Google Maps URL (exact match at lookup + save time)
- Budget stored as RM min/max integers (Malaysian Ringgit)
- EPP = simple boolean flag (company discount exists at this place)
- Days closed stored as comma-separated day names e.g. `"Saturday,Sunday"`
- No photos — emoji placeholder used instead (avoids Google Places API credit card requirement)
- Place lookup: follow URL redirects → extract name from path → Nominatim for address
- Frontend `days_closed` is a string in DB but a `string[]` in Vue form state (joined on save)
