#!/usr/bin/env python3
"""
refresh_nudger.py — rebuild the Deal Nudger queue in data/sales_data.json
from live HubSpot data.

Why this exists
---------------
The nudger array was hand-pasted into data/sales_data.json on 2026-07-23 and
has no way to self-correct. Deals qualified out since then still sit in the
queue wearing their old open-pipeline stage label, and newly created deals
never appear at all.

This script replaces ONLY the `nudger` key on each rep. Every other part of
sales_data.json (periods, charts, generated_at) is left byte-for-byte alone,
so it composes safely with generate_data.py rather than fighting it.

  IMPORTANT: generate_data.py does not write a `nudger` key. If you run
  generate_data.py, it will drop the array. Always run this script after it.

How stages are filtered
-----------------------
Two independent guards, deliberately belt-and-braces:

  1. The HubSpot search itself filters on `hs_is_closed = false`. In this
     portal that single condition already excludes Sales Qualified Out,
     Closed Lost, Churned and Paused across all three deal pipelines, and
     it keeps working when someone adds or renames a stage.

  2. Stage metadata is pulled live from /crm/v3/pipelines/deals and any
     stage flagged isClosed is dropped again locally. This catches the case
     where HubSpot's index lags behind a stage edit.

No stage IDs are hardcoded anywhere. That was the original bug: an
allow-list of IDs silently rots the moment ops edits a pipeline, and this
portal has three pipelines carrying near-duplicate stage sets.

Usage
-----
    export HUBSPOT_TOKEN=pat-eu1-xxxxxxxx
    python refresh_nudger.py

Requires a HubSpot private-app token with scope: crm.objects.deals.read
(and crm.schemas.deals.read for the pipeline metadata). Standard library
only — no pip install.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

# ── Config ────────────────────────────────────────────────────────────────────

PORTAL = "5606823"

# Reps to build a queue for, keyed by HubSpot owner ID.
# Add more entries here as the report grows beyond one rep.
REPS = {
    "91133237": "Dan Owens",
}

# Deals created within this many days are skipped, so a deal isn't nudged
# before anyone has had a chance to work it. Set to 0 to disable.
GRACE_DAYS = 7

# Optional: internal name of your DAU custom property. Leave as None if you
# don't have one — the `dau_tier1` field will simply be null, as it is today.
DAU_FIELD = os.environ.get("DAU_FIELD") or None

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "data", "sales_data.json")

API = "https://api.hubapi.com"
TOKEN = os.environ.get("HUBSPOT_TOKEN", "").strip()


# ── HTTP ──────────────────────────────────────────────────────────────────────

def api(path, method="GET", payload=None, _retries=4):
    """Call the HubSpot API. Retries on 429 and 5xx with linear backoff."""
    url = API + path
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Content-Type", "application/json")

    for attempt in range(_retries):
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:400]
            if e.code == 401:
                die("HubSpot rejected the token (401). Check HUBSPOT_TOKEN "
                    "and that the private app has crm.objects.deals.read.")
            if e.code == 403:
                die("HubSpot returned 403 — the token is valid but missing a "
                    "scope. Needs crm.objects.deals.read and "
                    "crm.schemas.deals.read.\n" + detail)
            if e.code == 429 or e.code >= 500:
                if attempt < _retries - 1:
                    wait = 2 * (attempt + 1)
                    log("  HubSpot %s, retrying in %ss" % (e.code, wait))
                    time.sleep(wait)
                    continue
            die("HubSpot %s on %s\n%s" % (e.code, path, detail))
        except urllib.error.URLError as e:
            if attempt < _retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            die("Could not reach HubSpot: %s" % e.reason)
    die("Gave up calling %s" % path)


def log(msg):
    print(msg, file=sys.stderr)


def die(msg):
    log("ERROR: " + msg)
    sys.exit(1)


# ── Stage metadata ────────────────────────────────────────────────────────────

def load_stages():
    """
    Build {stage_id: {"label": str, "closed": bool}} from live pipeline data.

    Nothing is hardcoded, so renamed or newly added stages are picked up on
    the next run with no code change.
    """
    stages = {}
    data = api("/crm/v3/pipelines/deals")
    for pipeline in data.get("results", []):
        for stage in pipeline.get("stages", []):
            meta = stage.get("metadata") or {}
            raw = meta.get("isClosed")
            closed = str(raw).lower() == "true"
            stages[stage["id"]] = {
                "label": (stage.get("label") or "").strip(),
                "closed": closed,
            }
    if not stages:
        die("No deal pipelines returned — cannot resolve stage labels.")
    log("Loaded %d stages across %d pipelines (%d flagged closed)."
        % (len(stages),
           len(data.get("results", [])),
           sum(1 for s in stages.values() if s["closed"])))
    return stages


# ── Deals ─────────────────────────────────────────────────────────────────────

def search_open_deals(owner_id):
    """
    Every open deal owned by owner_id.

    `hs_is_closed = false` is the whole filter. It is pipeline-agnostic and
    survives stage edits, which an explicit list of stage IDs does not.
    """
    props = [
        "dealname", "dealstage", "pipeline", "amount", "dealtype",
        "createdate", "hs_lastmodifieddate",
        "notes_last_contacted", "notes_last_updated",
        "hs_is_closed", "hs_is_closed_won",
    ]
    if DAU_FIELD:
        props.append(DAU_FIELD)

    payload = {
        "filterGroups": [{
            "filters": [
                {"propertyName": "hs_is_closed", "operator": "EQ",
                 "value": "false"},
                {"propertyName": "hubspot_owner_id", "operator": "EQ",
                 "value": str(owner_id)},
            ]
        }],
        "properties": props,
        "sorts": [{"propertyName": "hs_lastmodifieddate",
                   "direction": "ASCENDING"}],
        "limit": 100,
    }

    results, after, pages = [], None, 0
    while True:
        if after:
            payload["after"] = after
        page = api("/crm/v3/objects/deals/search", "POST", payload)
        results.extend(page.get("results", []))
        pages += 1
        after = (page.get("paging") or {}).get("next", {}).get("after")
        if not after:
            break
        if pages > 60:
            log("  Stopped paginating at 60 pages as a safety valve.")
            break
        time.sleep(0.12)  # stay well inside the search rate limit
    return results


# ── Shaping ───────────────────────────────────────────────────────────────────

def short_name(dealname):
    """'Indirect | Bumble' -> 'Bumble'. Matches the existing array's shape."""
    if not dealname:
        return "(unnamed deal)"
    if "|" in dealname:
        tail = dealname.split("|")[-1].strip()
        if tail:
            return tail
    return dealname.strip()


def last_activity(props):
    """
    Best available 'last touched' date, as YYYY-MM-DD.

    Prefers real engagement (notes_last_contacted) over record edits, so the
    'days since last activity' figure on the card means something.
    """
    for key in ("notes_last_contacted", "notes_last_updated",
                "hs_lastmodifieddate", "createdate"):
        val = props.get(key)
        if val:
            return str(val)[:10]
    return None


def to_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def build_queue(owner_id, stages):
    deals = search_open_deals(owner_id)
    log("  %d open deals returned by HubSpot." % len(deals))

    cutoff = None
    if GRACE_DAYS > 0:
        cutoff = (datetime.now(timezone.utc)
                  - timedelta(days=GRACE_DAYS)).strftime("%Y-%m-%d")

    queue = []
    skipped_closed = skipped_new = skipped_nodate = 0

    for deal in deals:
        props = deal.get("properties") or {}
        stage_id = props.get("dealstage")
        stage = stages.get(stage_id)

        # Guard 2: drop anything the pipeline metadata says is closed, even
        # if the search index hasn't caught up yet.
        if stage and stage["closed"]:
            skipped_closed += 1
            continue

        date = last_activity(props)
        if not date:
            skipped_nodate += 1
            continue

        created = str(props.get("createdate") or "")[:10]
        if cutoff and created and created > cutoff:
            skipped_new += 1
            continue

        queue.append({
            "id": deal["id"],
            "name": short_name(props.get("dealname")),
            "full_name": (props.get("dealname") or "").strip() or None,
            "stage": stage["label"] if stage else (stage_id or "Unknown"),
            "amount": to_float(props.get("amount")),
            "date": date,
            "url": "https://app.hubspot.com/contacts/%s/record/0-3/%s"
                   % (PORTAL, deal["id"]),
            "dau_tier1": to_float(props.get(DAU_FIELD)) if DAU_FIELD else None,
        })

    # Stalest first — same ordering the deleted client-side filter used.
    queue.sort(key=lambda d: d["date"])

    log("  Kept %d. Skipped: %d closed-by-metadata, %d inside %d-day grace, "
        "%d with no usable date."
        % (len(queue), skipped_closed, skipped_new, GRACE_DAYS,
           skipped_nodate))
    return queue


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not TOKEN:
        die("HUBSPOT_TOKEN is not set.\n"
            "  export HUBSPOT_TOKEN=pat-eu1-xxxxxxxx")

    if not os.path.exists(DATA_PATH):
        die("Cannot find %s — run this from the repo root." % DATA_PATH)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    reps = data.get("reps")
    if not reps:
        die("sales_data.json has no `reps` array — nothing to attach to.")

    stages = load_stages()
    total = 0
    matched = 0

    for rep_entry in reps:
        rep_id = str(((rep_entry.get("rep") or {}).get("id") or "")).strip()
        rep_name = (rep_entry.get("rep") or {}).get("name") or rep_id

        if rep_id not in REPS:
            log("Skipping %s (%s) — not in the REPS map." % (rep_name, rep_id))
            continue

        matched += 1
        log("Rebuilding nudger for %s (%s)..." % (rep_name, rep_id))
        queue = build_queue(rep_id, stages)
        rep_entry["nudger"] = queue
        total += len(queue)

    if not matched:
        die("None of the reps in sales_data.json matched the REPS map. "
            "Check the owner IDs at the top of this script.")

    data["nudger_generated_at"] = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    log("Done. %d deals across %d rep(s) written to %s"
        % (total, matched, DATA_PATH))


if __name__ == "__main__":
    main()
