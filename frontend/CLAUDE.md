# Frontend

Vue 3 via CDN + Tailwind via CDN. Single file: `frontend/index.html`. No build step, no npm.

## Hosting

- **Local dev**: served by FastAPI at `GET /` (backend reads `../frontend/index.html`)
- **Production**: hosted on GitHub Pages — push `frontend/index.html` to the `gh-pages` branch (or configure Pages to serve from `/frontend`)

Before deploying to GitHub Pages, replace `YOUR_DDNS_DOMAIN_HERE` in `index.html` with the actual DDNS domain.

## API base URL

```javascript
const API_BASE = (hostname === 'localhost' || hostname === '127.0.0.1')
  ? `http://${window.location.host}`   // local dev → same host as uvicorn
  : 'https://YOUR_DDNS_DOMAIN_HERE';   // production → home server
```

## Views

Three tabs, single-page, no router:

| Tab | `currentView` | What it shows |
|-----|--------------|---------------|
| Today's Picks | `today` | Recommendation card + "All Open Today" list |
| All Places | `all` | Filterable grid of every place |
| + Add | `add` | Add place form (lookup-gated) |

## State

All state is Vue 3 `ref` / `computed`. Nothing persisted client-side beyond the current session.

Key refs:
- `allPlaces` — full list from `GET /api/places/`
- `todayPlaces` — list from `GET /api/places/today`
- `recommended` — single place from `GET /api/places/recommend`, or `null`
- `filters` — `{ search, eppOnly, parking, budgetMax }` for the All Places view
- `form` — add-place form state (see `makeForm()`)
- `editTarget` / `editForm` — controls the edit modal

## Add place form flow

1. User pastes a Google Maps URL and clicks **Lookup**
2. `GET /api/places/lookup?maps_url=...` — returns `{name, address, is_duplicate}`
3. If duplicate → show error, block form
4. If success → `form.looked_up = true`, rest of form reveals
5. User fills in the remaining fields and submits
6. On success → redirect to All Places tab

`makeForm()` is the single source of truth for blank form state. Both reset and initial state use it.

## Image arrays (shop_images / menu_images)

These are `ref`-reactive arrays of URL strings. Dynamic rows work via Vue 3's Proxy reactivity:
- `form.shop_images.push('')` — adds a row
- `form.shop_images.splice(i, 1)` — removes row at index i
- `v-model="form.shop_images[i]"` — two-way bind to each input

Empty strings are filtered out before submitting: `.filter(u => u.trim())`.

## Map thumbnails

Map tiles come from `https://tile.openstreetmap.org/{z}/{x}/{y}.png` — OSM CDN, no API key.

Tile coordinates are computed from the `@lat,lon` found in the stored Google Maps URL:

```javascript
function mapImageUrl(mapsUrl) {
  const m = mapsUrl.match(/@(-?\d+\.\d+),(-?\d+\.\d+)/);
  // standard Web Mercator tile math at zoom 17
  ...
  return `https://tile.openstreetmap.org/17/${x}/${y}.png`;
}
```

Works for full Google Maps URLs (which embed `@lat,lon`). Falls back to emoji `🍴` if no coords found or image fails to load (`@error` handler sets `display:none`).

## Filters (All Places)

`filteredPlaces` computed applies these in order:
1. EPP only — `p.has_epp`
2. Parking — `p.parking_difficulty === filters.parking`
3. Budget — `p.budget_min <= filters.budgetMax` (empty = no filter)
4. Search — name or address contains query (case-insensitive)

## Edit modal

`openEdit(place)` copies place data into `editForm` (deep copy for arrays). `closeEdit()` sets both `editTarget` and `editForm` to null. The modal is rendered with `v-if="editTarget"`.

`saveEdit()` guards against the form being cleared mid-flight (async race) by checking `if (editForm.value)` before accessing it in catch/finally.

## Data type notes

- `days_closed` — string in DB and API (`"Saturday,Sunday"`). Form state uses `string[]`, joined to string on submit.
- `shop_images` / `menu_images` — `string[]` in API response (backend normalises null → `[]`). Passed as arrays in POST/PUT body.
- `budget_min` / `budget_max` — integers (RM). Use `v-model.number` on inputs.
- `has_epp` — boolean checkbox.

## Key dependencies (CDN)

```html
<script src="https://cdn.tailwindcss.com"></script>
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
```

No build tools, no package.json.
