# BidMachine Supply Sales Dashboard

GitHub Pages dashboard showing HubSpot sales activity by rep.
Updated weekly via a Python fetch script.

---

## Quick setup

### 1. Install dependencies

```bash
pip install requests python-dateutil
```

### 2. Get a HubSpot Private App token

1. Go to HubSpot → Settings → Integrations → Private Apps
2. Create a new private app with these scopes:
   - `crm.objects.deals.read`
   - `crm.objects.contacts.read`
   - `crm.objects.companies.read`
   - `crm.objects.notes.read`
   - `crm.objects.meetings.read`
3. Copy the token

### 3. Add your token to fetch_data.py

Open `fetch_data.py` and replace:
```python
HS_TOKEN = "YOUR_HUBSPOT_PRIVATE_APP_TOKEN_HERE"
```

> ⚠️ Never commit your token to GitHub. Add `fetch_data.py` to `.gitignore`
> and store the token in an environment variable for production use.

### 4. Enable GitHub Pages

In your repo: Settings → Pages → Source → Deploy from branch → `main` → `/ (root)`

### 5. Run the first fetch

```bash
python fetch_data.py
git add data/sales_data.json
git commit -m "data: initial fetch"
git push
```

Your dashboard will be live at: `https://YOUR_USERNAME.github.io/YOUR_REPO/`

---

## Weekly workflow (every Friday lunchtime)

```bash
python fetch_data.py
git add data/sales_data.json
git commit -m "data: weekly refresh $(date +%Y-%m-%d)"
git push
```

That's it. GitHub Pages serves the updated data automatically within ~1 minute.

---

## Adding another sales rep

Open `fetch_data.py` and find the `REPS` list. Uncomment or add:

```python
REPS = [
    {"id": "91133237", "name": "Dan Owens"},
    {"id": "42306400", "name": "Joel Chang"},      # uncomment to add
    {"id": "64757937", "name": "Randy Barenscott"}, # uncomment to add
    # Add more here — owner IDs from HubSpot
]
```

To find a rep's owner ID: search for them in HubSpot → the URL contains their owner ID,
or ask Claude "what is [name]'s HubSpot owner ID".

---

## Confirming the DAU field name

The DAU field (`DAU_FIELD` in `fetch_data.py`) defaults to `estimated_revenue_us_per_month`.
To confirm the correct field name:

1. Open any deal in HubSpot that has DAU entered
2. Check the URL, then ask Claude: "what is the HubSpot internal property name for the DAU field on deals?"
3. Update `DAU_FIELD` in `fetch_data.py`

---

## LinkedIn message detection

LinkedIn messages are detected from HubSpot notes containing any of these keywords
(case-insensitive):

```
linkedin, li message, linked in, messaged on li, li outreach
```

To add more keywords, edit the `LINKEDIN_KEYWORDS` list in `fetch_data.py`.

---

## File structure

```
sales-dashboard/
├── index.html          # Dashboard UI (GitHub Pages entry point)
├── fetch_data.py       # Weekly data fetch script (do not commit token)
├── data/
│   └── sales_data.json # Generated data file (commit this each week)
└── README.md
```

---

## Security note

`fetch_data.py` contains your HubSpot token. For a more secure setup:

```bash
export HUBSPOT_TOKEN="pat-xxx"
```

Then in `fetch_data.py`:
```python
HS_TOKEN = os.environ.get("HUBSPOT_TOKEN", "")
```

The `data/sales_data.json` file contains no credentials — it's safe to commit and serve publicly.
