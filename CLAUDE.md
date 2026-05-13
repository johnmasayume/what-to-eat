# what-to-eat

A lunch place picker for the team — crowdsourced restaurant entries with daily recommendations.

## What it does

- Team members add restaurant/place info (name, Maps link, parking, days closed, budget, EPP)
- Home page shows today's random recommendation + all places open today
- All places page lets you browse and filter the full list
- Duplicate detection via Google Maps URL

## Tech Stack

- **Frontend**: Vue 3 via CDN, single `index.html`, hosted on GitHub Pages
- **Backend**: FastAPI + SQLite, hosted on home server behind Caddy (HTTPS + DDNS)
- **Google Places API**: Called server-side to auto-fill name, address, photo from Maps URL

## Local Dev

```bash
cd backend
uvicorn main:app --reload
# visit http://localhost:8000
```

Frontend is served by FastAPI at `/` during local dev. In production, GitHub Pages serves the same `index.html`.

## Project Structure

```
what-to-eat/
├── backend/
│   ├── main.py          # FastAPI app + static file serving
│   ├── models.py        # SQLite models (SQLAlchemy)
│   ├── database.py      # DB setup
│   ├── routes/
│   │   └── places.py    # Place CRUD + recommend endpoint
│   ├── services/
│   │   └── google_places.py  # Google Places API integration
│   └── .env.example     # GOOGLE_PLACES_API_KEY
├── frontend/
│   └── index.html       # Vue 3 CDN single-page app
└── CLAUDE.md
```

## Key Decisions

- No login — user enters their name on submission only
- Duplicate detection by Google Maps URL (exact match)
- Budget in RM (Malaysian Ringgit), stored as min/max integers
- EPP = simple boolean flag (company discount exists at this place)
- Days closed stored as comma-separated day names (e.g. "Saturday,Sunday")
- Currency: RM (Malaysian Ringgit)
- Language: English UI
