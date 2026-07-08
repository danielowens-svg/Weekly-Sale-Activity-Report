import json, os, re
from datetime import datetime, timezone, timedelta

PORTAL = "5606823"
STAGE_LABELS = {"1278450782":"Lead","1343040315":"Lead with Peer SDK","1157536":"MQL","1855526":"Sales Prospecting","1574904":"Sales Qualified Lead","961283":"Sales Proposal","1295831362":"Internal Review","961284":"MSA Shared","961285":"Signed","1298527140":"Waiting Integration","1213494111":"Integrating","1213494112":"Live & Testing","1213493907":"Fully Scaled","1217350681":"Paused","1217350682":"Churned","34415407":"Sales Qualified Out","961286":"Closed Lost"}
STAGE_RANK = {"1278450782":1,"1343040315":2,"1157536":3,"1855526":4,"1574904":5,"961283":6,"1295831362":7,"961284":8,"961285":9,"1298527140":10,"1213494111":11,"1213494112":12,"1213493907":13}
CLOSED = {"34415407","961286"}
PEER_SDK = "1343040315"
LINKEDIN_KW = ["linkedin","li message","linked in","messaged on li","li outreach"]
OOO_LOG = {"91133237":[{"date":"2026-06-17","note":"OOO"},{"date":"2026-06-18","note":"OOO"},{"date":"2026-06-19","note":"OOO"},{"date":"2026-06-20","note":"OOO"},{"date":"2026-06-23","note":"OOO"},{"date":"2026-06-24","note":"OOO"}]}

EMAIL_DEAL_MAP = {
    "what3words":"Indirect | What3words","viber":"Indirect | Viber",
    "muzz":"Indirect | Muzz LTD","minute media":"Indirect | Minute Media",
    "peaksel":"Indirect | Peaksel","tech tree":"Tech Tree",
    "ziff davis":"Indirect | Ziff Davis","tunein":"Indirect TuneIn",
    "gameberry":"Indirect | Gameberry Labs","influent media":"Indirect Influent Media",
    "indrive":"Indirect | InDrive (SUOL)","aniview":"Aniview & BidMachine",
    "sliide":"Mia from Sliide","by glass labs":"Indirect | byglasslabs.io",
    "nordcurrent":"Indirect | Nordcurrent","hero fighting":"Indirect | Hero Fighting Games",
    "likee":"Indirect | Likee","orange one":"Indirect | Pleasure City",
    "gravity":"Indirect | Gravity Ltd","dijital elma":"Zubeyda / DIJITAL ELMA",
    "luma ai":"Indirect | Luma AI","mage games":"Indirect | Mage Games",
    "lootcopter":"Indirect | Lootcopter","cyanads":"Indirect | CyanAds",
    "ey parthenon":"Indirect | Parthenon EY","bbc":"Indirect | BBC",
    "sky":"Indirect | Sky","bumble":"Indirect | Bumble",
    "badoo":"Indirect | Badoo Software","vinted":"Indirect | Vinted",
    "kleinanzeigen":"Indirect | Kleinanzeigen","rakuten":"Indirect | Rakuten",
    "soundcloud":"Indirect | SoundCloud","trade house":"Indirect | Trade House Media",
    "match media":"Indirect | Match Media Group","bereal":"Indirect | BeReal",
    "investing.com":"Indirect | Investing.com","warner bros":"Indirect | Warner Bros",
    "iscool":"Indirect | IsCool Entertainment","pleasure city":"Indirect | Pleasure City",
    "pluto":"Indirect | Pluto Inc","fandom":"Indirect | Fandom",
    "npr":"Indirect | NPR","dailymail":"Indirect | DailyMail",
    "telegraph":"Indirect | Telegraph","channel 4":"Indirect | Channel 4",
    "nbcuniversal":"Indirect | NBCUniversal","adevinta":"Indirect | Adevinta",
    "disney":"Indirect | Disney",
}

ALL_EMAILS = [
    {"subject":"RE: Bidmachine Offering - EY Parthenon","date":"2026-07-04"},
    {"subject":"Monetization Partnership - Bidmachine | Orange One Limited","date":"2026-07-03"},
    {"subject":"Monetisation partnership - Bidmachine | InDrive","date":"2026-07-03"},
    {"subject":"Re: Monetisation partnership Bidmachine | Viber","date":"2026-07-03"},
    {"subject":"Re: Bidmachine / what3words","date":"2026-07-03"},
    {"subject":"Re: Bidmachine | Minute Media as a demand partner","date":"2026-07-02"},
    {"subject":"Re: Bidmachine MSA","date":"2026-07-02"},
    {"subject":"Monetisation partnership Bidmachine | Viber","date":"2026-07-01"},
    {"subject":"Re: Bidmachine | Minute Media as a demand partner","date":"2026-07-01"},
    {"subject":"Monetisation partnership - Bidmachine / Muzz","date":"2026-07-01"},
    {"subject":"Re: App monetistion partnership - Bidmachine","date":"2026-07-01"},
    {"subject":"Monetisation partnership - Certified MAX bidder","date":"2026-07-01"},
    {"subject":"Re: Bidmachine MSA","date":"2026-06-30"},
    {"subject":"Re: App Monetisation Partnership","date":"2026-06-30"},
    {"subject":"Re: Bidmachine / Influent Media next steps","date":"2026-06-30"},
    {"subject":"Re: Bidmachine / what3words","date":"2026-06-30"},
    {"subject":"Re: Bidmachine MSA","date":"2026-06-29"},
    {"subject":"Bidmachine | Minute Media as a demand partner","date":"2026-06-29"},
    {"subject":"App monetistion partnership - Bidmachine","date":"2026-06-29"},
    {"subject":"Monetisation Partnership","date":"2026-06-29"},
    {"subject":"Monetisation partnership - Bidmachine / Muzz","date":"2026-07-07"},
    {"subject":"In-app monetisation - Bidmachine | Global","date":"2026-07-07"},
    {"subject":"Re: Bidmachine & Peaksel","date":"2026-07-07"},
    {"subject":"RE: Bidmachine Offering - EY Parthenon","date":"2026-07-07"},
    {"subject":"Bidmachine | Gameberry Labs","date":"2026-07-07"},
    {"subject":"Re: BidMachine & Aniview - Partnership","date":"2026-07-07"},
    {"subject":"Monetization Partnership - Bidmachine | TuneIn","date":"2026-07-07"},
    {"subject":"Monetisation Partnership - Bidmachine | Scoopz/Luma AI","date":"2026-07-07"},
    {"subject":"Bidmachine | Nordcurrent next steps","date":"2026-07-07"},
    {"subject":"Monetisation partnership - Bidmachine | Sliide","date":"2026-07-06"},
    {"subject":"Demand intro - By Glass Labs | Bidmachine","date":"2026-07-06"},
    {"subject":"BidMachine & Aniview - Partnership","date":"2026-07-06"},
    {"subject":"Re: Bidmachine / what3words","date":"2026-07-06"},
    {"subject":"Bidmachine & Peaksel","date":"2026-07-06"},
    {"subject":"Bidmachine | Minute Media","date":"2026-07-08"},
    {"subject":"Monetisation partnership - Bidmachine | Gravity","date":"2026-07-08"},
    {"subject":"RE: Bidmachine Offering - EY Parthenon","date":"2026-07-08"},
    {"subject":"Monetisation partnership - Hero Fighting Games / Bidmachine","date":"2026-06-25"},
    {"subject":"Monetization partnership - Likee / Bidmachine","date":"2026-06-26"},
    {"subject":"Bidmachine MSA","date":"2026-06-16"},
    {"subject":"Re: Bidmachine / what3words","date":"2026-06-25"},
    {"subject":"Re: Bidmachine / Influent Media next steps","date":"2026-06-16"},
    {"subject":"Re: Monetization - Bidmachine / Tech Tree Games","date":"2026-06-12"},
    {"subject":"Re: Bidmachine / Dijital Elma","date":"2026-06-10"},
    {"subject":"Monetization - Bidmachine / Tech Tree Games","date":"2026-06-09"},
    {"subject":"Re: Mage Games X Bidmachine Support","date":"2026-06-09"},
    {"subject":"Re: Intro (app demand)","date":"2026-06-08"},
    {"subject":"Re: Bidmachine / Minute Media","date":"2026-06-01"},
    {"subject":"Bidmachine-CyanAds Demand discussion","date":"2026-06-01"},
    {"subject":"Bidmachine / Dijital Elma","date":"2026-06-02"},
    {"subject":"Re: Partner Inquiry: Ad Monetization Integration Lootcopter x Bidmachine","date":"2026-06-18"},
    {"subject":"Monetarisierungspartnerschaft - Bidmachine","date":"2026-06-26"},
]

def emails_to_deal_touches(emails, start, end):
    deal_touches = {}
    for e in emails:
        d = e["date"]
        if not (start <= d <= end):
            continue
        subj = (e.get("subject") or "").lower()
        for kw, deal_name in EMAIL_DEAL_MAP.items():
            if kw in subj:
                if deal_name not in deal_touches or d > deal_touches[deal_name]:
                    deal_touches[deal_name] = d
    return deal_touches

def deal_row(d, df="hs_lastmodifieddate"):
    t1 = d.get("dau_tier_1"); ps = d.get("prev_stage")
    return {"id":d["id"],"name":d["dealname"],"amount":d.get("amount"),
            "stage":STAGE_LABELS.get(d["dealstage"],d["dealstage"]),"stage_id":d["dealstage"],
            "date":d.get(df,d.get("hs_lastmodifieddate",""))[:10],
            "url":f"https://app.hubspot.com/contacts/{PORTAL}/record/0-3/{d['id']}",
            "dau_tier1":int(t1) if t1 and str(t1) not in("0","") else None,"dau_us":None,
            "prev_stage":STAGE_LABELS.get(ps,None) if ps else None,"prev_stage_id":ps}

def email_deal_row(deal_name, date):
    return {"id":f"email_{deal_name}","name":deal_name,"amount":None,
            "stage":"Email activity","date":date,
            "url":f"https://app.hubspot.com/contacts/{PORTAL}/objects/0-3/",
            "dau_tier1":None,"dau_us":None,"prev_stage":None,"prev_stage_id":None}

def get_progressed(deals):
    out = []
    for d in deals:
        ps = d.get("prev_stage"); cs = d["dealstage"]
        if not ps or cs in CLOSED: continue
        if STAGE_RANK.get(cs,0) > STAGE_RANK.get(ps,0):
            r = deal_row(d); r["progression"] = f"{STAGE_LABELS.get(ps,ps)} → {STAGE_LABELS.get(cs,cs)}"; out.append(r)
    return out

def get_ooo(owner, s, e):
    return [o for o in OOO_LOG.get(owner,[]) if s <= o["date"] <= e]

def build(deals, meetings, notes, companies, owner, ps, pe):
    closed  = [d for d in deals if d["dealstage"] in CLOSED]
    new_d   = [d for d in deals if ps <= d["createdate"] <= pe]
    peer    = [d for d in deals if d["dealstage"] == PEER_SDK and ps <= d["createdate"] <= pe]
    dau_t1  = [d for d in deals if d.get("dau_tier_1") and str(d["dau_tier_1"]) not in ("0","")]
    li      = [n for n in notes if any(kw in n["text"].lower() for kw in LINKEDIN_KW)]
    prog    = get_progressed(deals)
    ooo     = get_ooo(owner, ps, pe)
    email_touches = emails_to_deal_touches(ALL_EMAILS, ps, pe)
    extra_email_deals = {name: date for name, date in email_touches.items()
                         if not any(name.lower() in d["dealname"].lower() or
                                    d["dealname"].lower() in name.lower() for d in deals)}
    total_touched = len(deals) + len(extra_email_deals)
    touched_detail = [deal_row(d) for d in deals]
    for name, date in extra_email_deals.items():
        touched_detail.append(email_deal_row(name, date))
    ss = {}
    for d in deals:
        lbl = STAGE_LABELS.get(d["dealstage"], d["dealstage"])
        if lbl not in ss: ss[lbl] = []
        ss[lbl].append(deal_row(d))
    return {
        "stats": {"deals_touched":total_touched,"new_deals":len(new_d),"qualified_out":len(closed),
                  "meetings":len(meetings),"linkedin":len(li),"new_companies":len(companies),
                  "dau_us_added":0,"dau_tier1_added":len(dau_t1),"peer_sdk":len(peer),
                  "stage_progressed":len(prog),"ooo_days":len(ooo),
                  "emails":len([e for e in ALL_EMAILS if ps <= e["date"] <= pe])},
        "detail": {"deals_touched":touched_detail,"new_deals":[deal_row(d,"createdate") for d in new_d],
                   "qualified_out":[deal_row(d,"closedate") for d in closed],"stage_summary":ss,
                   "meetings":meetings,"linkedin":li,
                   "new_companies":[{"id":c["id"],"name":c["name"],"domain":c.get("domain",""),
                                     "date":c["date"],"url":f"https://app.hubspot.com/contacts/{PORTAL}/record/0-2/{c['id']}"}
                                    for c in companies],
                   "dau_us_added":[],"dau_tier1_added":[deal_row(d) for d in dau_t1],
                   "peer_sdk":[deal_row(d,"createdate") for d in peer],
                   "stage_progressed":prog,"ooo":ooo}}

now = datetime.now(timezone.utc)
today = now.strftime("%Y-%m-%d")
last_monday = now - timedelta(days=now.weekday() + 7)
last_sunday = last_monday + timedelta(days=6)
WEEK_START = last_monday.strftime("%Y-%m-%d")
WEEK_END = last_sunday.strftime("%Y-%m-%d")
first_this_month = now.replace(day=1)
last_month_end = first_this_month - timedelta(days=1)
last_month_start = last_month_end.replace(day=1)
MONTH_START = last_month_start.strftime("%Y-%m-%d")
MONTH_END = last_month_end.strftime("%Y-%m-%d")
QUARTER_START = "2026-07-01"
QUARTER_END = today
LAST_QUARTER_START = "2026-04-01"
LAST_QUARTER_END = "2026-06-30"
YEAR_START = "2026-01-01"

print(f"Last week:     {WEEK_START} to {WEEK_END}")
print(f"Last month:    {MONTH_START} to {MONTH_END}")
print(f"This quarter:  {QUARTER_START} to {QUARTER_END}")
print(f"Last quarter:  {LAST_QUARTER_START} to {LAST_QUARTER_END}")

CQ_DEALS=[{"id":"59724975001","dealname":"Indirect | Minute Media","dealstage":"1343040315","amount":None,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-07-08","closedate":"2026-12-31","dau_tier_1":"0","prev_stage":None},{"id":"45994176365","dealname":"Indirect TuneIn","dealstage":"1855526","amount":146298,"createdate":"2025-10-15","hs_lastmodifieddate":"2026-07-08","closedate":"2026-12-31","dau_tier_1":"65767","prev_stage":"1343040315"},{"id":"59693639305","dealname":"Indirect | Telegraph","dealstage":"1855526","amount":62910,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-07-08","closedate":"2026-12-31","dau_tier_1":"202008","prev_stage":None},{"id":"62115238406","dealname":"Indirect | DN Capital","dealstage":"34415407","amount":None,"createdate":"2026-07-03","hs_lastmodifieddate":"2026-07-08","closedate":"2026-07-31","dau_tier_1":None,"prev_stage":None},{"id":"58135605117","dealname":"Indirect Teslatech","dealstage":"34415407","amount":740,"createdate":"2026-03-18","hs_lastmodifieddate":"2026-07-08","closedate":"2026-07-08","dau_tier_1":"1658","prev_stage":None},{"id":"46008372826","dealname":"Indirect | SoundCloud","dealstage":"1343040315","amount":1021031,"createdate":"2025-10-15","hs_lastmodifieddate":"2026-07-08","closedate":"2026-12-31","dau_tier_1":"1500302","prev_stage":None},{"id":"57393985163","dealname":"Indirect | NPR","dealstage":"1343040315","amount":46336,"createdate":"2026-03-02","hs_lastmodifieddate":"2026-07-08","closedate":"2026-12-31","dau_tier_1":"1879","prev_stage":None},{"id":"58591201183","dealname":"Indirect | DailyMail","dealstage":"1855526","amount":9796,"createdate":"2026-03-31","hs_lastmodifieddate":"2026-07-08","closedate":"2026-09-30","dau_tier_1":"112000","prev_stage":None},{"id":"57401048456","dealname":"Indirect | Pluto Inc","dealstage":"34415407","amount":559721,"createdate":"2026-03-02","hs_lastmodifieddate":"2026-07-08","closedate":"2026-07-08","dau_tier_1":"18097","prev_stage":"1343040315"},{"id":"59724909111","dealname":"Indirect | Ziff Davis","dealstage":"1855526","amount":1868903,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-07-08","closedate":"2026-12-31","dau_tier_1":"308913","prev_stage":None},{"id":"59697119280","dealname":"Indirect | Investing.com","dealstage":"1855526","amount":214653,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-07-08","closedate":"2026-12-31","dau_tier_1":"507942","prev_stage":None},{"id":"3851796237","dealname":"Indirect | Vinted","dealstage":"1343040315","amount":2552016,"createdate":"2020-12-29","hs_lastmodifieddate":"2026-07-08","closedate":"2026-12-31","dau_tier_1":"14331684","prev_stage":None},{"id":"61764854383","dealname":"Indirect | IsCool Entertainment","dealstage":"1343040315","amount":None,"createdate":"2026-06-30","hs_lastmodifieddate":"2026-07-08","closedate":"2026-09-30","dau_tier_1":None,"prev_stage":None},{"id":"62045501561","dealname":"Indirect | Pleasure City","dealstage":"1343040315","amount":None,"createdate":"2026-07-02","hs_lastmodifieddate":"2026-07-08","closedate":"2026-10-31","dau_tier_1":None,"prev_stage":None},{"id":"62045627294","dealname":"Indirect | Gravity Ltd","dealstage":"1343040315","amount":None,"createdate":"2026-07-02","hs_lastmodifieddate":"2026-07-08","closedate":"2026-09-30","dau_tier_1":None,"prev_stage":None},{"id":"29202384969","dealname":"Indirect | Gameberry Labs","dealstage":"1343040315","amount":198168,"createdate":"2024-11-18","hs_lastmodifieddate":"2026-07-08","closedate":"2026-09-30","dau_tier_1":"305242","prev_stage":None},{"id":"61935672396","dealname":"Indirect | Muzz LTD","dealstage":"1343040315","amount":34430,"createdate":"2026-06-30","hs_lastmodifieddate":"2026-07-08","closedate":"2026-08-31","dau_tier_1":"95842","prev_stage":None},{"id":"60068956505","dealname":"Indirect | Peaksel","dealstage":"1855526","amount":72007,"createdate":"2026-05-07","hs_lastmodifieddate":"2026-07-08","closedate":"2026-09-30","dau_tier_1":"106000","prev_stage":"1343040315"},{"id":"60075512157","dealname":"Indirect | Trade House Media","dealstage":"961283","amount":154442,"createdate":"2026-05-07","hs_lastmodifieddate":"2026-07-08","closedate":"2026-09-30","dau_tier_1":None,"prev_stage":"1855526"},{"id":"4999713719","dealname":"Indirect | Viber","dealstage":"1574904","amount":561736,"createdate":"2021-04-14","hs_lastmodifieddate":"2026-07-08","closedate":"2026-12-31","dau_tier_1":"3500000","prev_stage":None},{"id":"60019213915","dealname":"Indirect | Match Media Group","dealstage":"1574904","amount":2930730,"createdate":"2026-05-05","hs_lastmodifieddate":"2026-07-07","closedate":"2026-12-31","dau_tier_1":"4400000","prev_stage":"1855526"},{"id":"59724942006","dealname":"Indirect | BBC","dealstage":"1855526","amount":814229,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-07-07","closedate":"2026-12-31","dau_tier_1":"4044590","prev_stage":"1343040315"},{"id":"59725784139","dealname":"Indirect | Fandom","dealstage":"34415407","amount":None,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-07-06","closedate":"2026-07-06","dau_tier_1":"0","prev_stage":None},{"id":"59724831156","dealname":"Indirect | Kleinanzeigen","dealstage":"1343040315","amount":2608372,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-07-06","closedate":"2026-12-31","dau_tier_1":"9074628","prev_stage":None},{"id":"59724743968","dealname":"Indirect | Warner Bros","dealstage":"1855526","amount":574936,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-07-06","closedate":"2026-12-31","dau_tier_1":"93822","prev_stage":None},{"id":"59725741170","dealname":"Indirect | Rakuten","dealstage":"1343040315","amount":4330629,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-07-05","closedate":"2026-12-31","dau_tier_1":"8919418","prev_stage":None},{"id":"57392746260","dealname":"Indirect | BeReal","dealstage":"34415407","amount":4742616,"createdate":"2026-03-02","hs_lastmodifieddate":"2026-07-05","closedate":"2026-05-27","dau_tier_1":"5674120","prev_stage":None},{"id":"45982477850","dealname":"Indirect | Badoo Software","dealstage":"1343040315","amount":2510680,"createdate":"2025-10-15","hs_lastmodifieddate":"2026-07-05","closedate":"2026-12-31","dau_tier_1":"1494519","prev_stage":None},{"id":"57389803862","dealname":"Indirect | Bumble","dealstage":"1343040315","amount":152442,"createdate":"2026-03-02","hs_lastmodifieddate":"2026-07-05","closedate":"2026-12-31","dau_tier_1":"732","prev_stage":None},{"id":"59725714776","dealname":"Indirect | Sky","dealstage":"1343040315","amount":8455152,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-07-05","closedate":"2026-12-31","dau_tier_1":"15000000","prev_stage":None},{"id":"34811011880","dealname":"Tech Tree","dealstage":"961283","amount":42444,"createdate":"2025-03-19","hs_lastmodifieddate":"2026-07-05","closedate":"2026-09-30","dau_tier_1":"40247","prev_stage":"1855526"},{"id":"60786218535","dealname":"Indirect | What3words","dealstage":"961283","amount":34227,"createdate":"2026-06-01","hs_lastmodifieddate":"2026-07-07","closedate":"2026-08-31","dau_tier_1":"182000","prev_stage":"1855526"}]
LQ_DEALS=[{"id":"61750324636","dealname":"Indirect | Yango Ads","dealstage":"34415407","amount":None,"createdate":"2026-06-29","hs_lastmodifieddate":"2026-06-29","closedate":"2026-06-30","dau_tier_1":None,"prev_stage":None},{"id":"59724784280","dealname":"Indirect | Channel 4","dealstage":"1343040315","amount":45311,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-06-26","closedate":"2026-12-31","dau_tier_1":"159357","prev_stage":None},{"id":"45974947895","dealname":"Indirect | Disney","dealstage":"1343040315","amount":5689980,"createdate":"2025-10-15","hs_lastmodifieddate":"2026-06-25","closedate":"2026-12-31","dau_tier_1":"1159159","prev_stage":None},{"id":"59725747570","dealname":"Indirect | NBCUniversal","dealstage":"1343040315","amount":783335,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-06-25","closedate":"2026-12-31","dau_tier_1":"1620946","prev_stage":None},{"id":"60135565222","dealname":"hubx","dealstage":"34415407","amount":27763,"createdate":"2026-05-09","hs_lastmodifieddate":"2026-06-25","closedate":"2026-06-25","dau_tier_1":"100000","prev_stage":None},{"id":"60650544716","dealname":"Indirect | OLX Group","dealstage":"34415407","amount":None,"createdate":"2026-05-26","hs_lastmodifieddate":"2026-06-25","closedate":"2026-06-25","dau_tier_1":None,"prev_stage":None},{"id":"59724816683","dealname":"Indirect | Gram Games","dealstage":"34415407","amount":227303,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-06-17","closedate":"2026-05-13","dau_tier_1":"171560","prev_stage":None},{"id":"61024719419","dealname":"Indirect | Fever Labs","dealstage":"34415407","amount":None,"createdate":"2026-06-10","hs_lastmodifieddate":"2026-06-16","closedate":"2026-06-30","dau_tier_1":None,"prev_stage":None},{"id":"59725772813","dealname":"Indirect | Uber","dealstage":"34415407","amount":None,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-06-12","closedate":"2026-09-30","dau_tier_1":"0","prev_stage":None},{"id":"59724769541","dealname":"Indirect | Overwolf","dealstage":"34415407","amount":7798,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-06-11","closedate":"2026-06-11","dau_tier_1":"6138","prev_stage":None},{"id":"45978573572","dealname":"Indirect | CNN Interactive","dealstage":"34415407","amount":228523,"createdate":"2025-10-15","hs_lastmodifieddate":"2026-06-10","closedate":"2026-06-10","dau_tier_1":"0","prev_stage":None},{"id":"45994331692","dealname":"Indirect | Tinder","dealstage":"34415407","amount":9498847,"createdate":"2025-10-15","hs_lastmodifieddate":"2026-05-28","closedate":"2026-05-07","dau_tier_1":"4624462","prev_stage":None},{"id":"59725714728","dealname":"Indirect | Deliveroo","dealstage":"34415407","amount":None,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-05-28","closedate":"2026-09-30","dau_tier_1":"1559181","prev_stage":None},{"id":"59697270836","dealname":"Indirect | Crunchyroll","dealstage":"34415407","amount":2290065,"createdate":"2026-04-27","hs_lastmodifieddate":"2026-05-28","closedate":"2026-05-28","dau_tier_1":"1298589","prev_stage":None},{"id":"45987590230","dealname":"Indirect Affinity Apps","dealstage":"34415407","amount":8336166,"createdate":"2025-10-15","hs_lastmodifieddate":"2026-05-28","closedate":"2026-05-28","dau_tier_1":"4624462","prev_stage":None},{"id":"57401357356","dealname":"Indirect | Hinge Inc","dealstage":"34415407","amount":5834329,"createdate":"2026-03-02","hs_lastmodifieddate":"2026-05-18","closedate":"2026-06-30","dau_tier_1":"3000000","prev_stage":None},{"id":"60075512157_lq","dealname":"Indirect | Trade House Media","dealstage":"1855526","amount":154442,"createdate":"2026-05-07","hs_lastmodifieddate":"2026-06-15","closedate":"2026-09-30","dau_tier_1":None,"prev_stage":"1343040315"},{"id":"60019213915_lq","dealname":"Indirect | Match Media Group","dealstage":"1855526","amount":2930730,"createdate":"2026-05-05","hs_lastmodifieddate":"2026-06-20","closedate":"2026-12-31","dau_tier_1":"4400000","prev_stage":"1574904"}]
CQ_MEETINGS=[{"id":"m1","title":"BidMachine | Muzz intro","date":"2026-07-10","outcome":"","notes":""},{"id":"m2","title":"Dan / Nikola BidMachine | Peaksel","date":"2026-07-10","outcome":"","notes":""},{"id":"m3","title":"BidMachine / Viber","date":"2026-07-09","outcome":"","notes":""},{"id":"m4","title":"Minute Media / Elsa","date":"2026-07-08","outcome":"","notes":"Elsa said Axel Springer purchase has slowed commercial conversations."},{"id":"m5","title":"SoundCloud / Ben","date":"2026-07-08","outcome":"","notes":"Ben offered intro to head of monetisation. Very audio heavy vs display/video."},{"id":"m6","title":"Introduction BidMachine / Parthenon EY","date":"2026-07-07","outcome":"","notes":""},{"id":"m7","title":"BidMachine | Minute Media","date":"2026-07-07","outcome":"","notes":""},{"id":"m8","title":"Aniview & BidMachine","date":"2026-07-06","outcome":"","notes":""},{"id":"m9","title":"Paramount","date":"2026-07-02","outcome":"COMPLETED","notes":"CTV focus, Freewheel + Springserve stack. Next: ops/tech call."},{"id":"m10","title":"Dan / Zach / Alex lunch","date":"2026-07-01","outcome":"","notes":""}]
LQ_MEETINGS=[{"id":"lq1","title":"Trade House Media / Post Industria","date":"2026-06-04","outcome":"COMPLETED","notes":"They use Post Industria (Pubmatic SDK). Need ~$25K dev work."},{"id":"lq2","title":"News Corp / Tim","date":"2026-06-02","outcome":"COMPLETED","notes":"Tim promoted to Head of Ops. Run in-house mediation GAM+TAM+Ozone."},{"id":"lq3","title":"What3words product lead","date":"2026-06-01","outcome":"COMPLETED","notes":"Starting ad monetisation. Open to Q3 launch."},{"id":"lq4","title":"Venatus (Sam)","date":"2026-05-19","outcome":"COMPLETED","notes":"No direct app inventory. Two channels: Google MCN and Index Exchange."},{"id":"lq5","title":"NewsUK / Guillaume","date":"2026-05-19","outcome":"COMPLETED","notes":"Partners need direct placement on ads.txt."},{"id":"lq6","title":"Match Media Group / Gregg","date":"2026-05-13","outcome":"COMPLETED","notes":"Match acquired Sniffy's. Introducing Dan to Greg Murphy."},{"id":"lq7","title":"Beeler Tech","date":"2026-06-10","outcome":"COMPLETED","notes":"9 contacts. Sim (Warner Bros) and Noeleen (Fandom) strongest leads."},{"id":"lq8","title":"Fandom / Noeleen Boyle","date":"2026-06-11","outcome":"COMPLETED","notes":"Intro via Beeler. Will connect to internal monetisation owner."}]
CQ_NOTES=[{"id":"n1","date":"2026-07-06","text":"In the process of purchasing Telegraph — will likely need to contract with new owner but TBC"},{"id":"n2","date":"2026-07-06","text":"According to ST - YOC is mediation used"},{"id":"n3","date":"2026-07-03","text":"Exchange operational requests: Mediation: google GAM. Networks: AdMob, InMobi, Moloco."},{"id":"n4","date":"2026-07-03","text":"LinkedIn reply from InDrive: Thanks for reaching out Dan — could you email details about adding BidMachine demand?"}]
CQ_COMPANIES=[{"id":"c1","name":"digitalyg.com","domain":"digitalyg.com","date":"2026-07-08"},{"id":"c2","name":"byglasslabs.io","domain":"byglasslabs.io","date":"2026-07-06"},{"id":"c3","name":"Axel Springer SE","domain":"axelspringer.com","date":"2026-07-06"},{"id":"c4","name":"DN Capital","domain":"dncapital.com","date":"2026-07-03"},{"id":"c5","name":"Suol Innovations (InDrive)","domain":"indriver.com","date":"2026-07-03"}]
LQ_COMPANIES=[{"id":"lc1","name":"What3words","domain":"what3words.com","date":"2026-06-01"},{"id":"lc2","name":"Rail Delivery Group","domain":"raildeliverygroup.com","date":"2026-06-10"},{"id":"lc3","name":"Bloomberg LP","domain":"bloomberg.com","date":"2026-06-10"},{"id":"lc4","name":"Fever Labs","domain":"feverup.com","date":"2026-06-10"},{"id":"lc5","name":"OLX Group","domain":"olxgroup.com","date":"2026-05-26"},{"id":"lc6","name":"MAG Interactive","domain":"maginteractive.com","date":"2026-05-26"},{"id":"lc7","name":"CoinMarketCap","domain":"coinmarketcap.com","date":"2026-05-28"}]

cq    = build([d for d in CQ_DEALS if QUARTER_START<=d["hs_lastmodifieddate"]<=QUARTER_END],[m for m in CQ_MEETINGS if QUARTER_START<=m["date"]<=QUARTER_END],[n for n in CQ_NOTES if QUARTER_START<=n["date"]<=QUARTER_END],[c for c in CQ_COMPANIES if QUARTER_START<=c["date"]<=QUARTER_END],"91133237",QUARTER_START,QUARTER_END)
lq    = build([d for d in LQ_DEALS if LAST_QUARTER_START<=d["hs_lastmodifieddate"]<=LAST_QUARTER_END],[m for m in LQ_MEETINGS if LAST_QUARTER_START<=m["date"]<=LAST_QUARTER_END],[],[c for c in LQ_COMPANIES if LAST_QUARTER_START<=c["date"]<=LAST_QUARTER_END],"91133237",LAST_QUARTER_START,LAST_QUARTER_END)
month = build([d for d in LQ_DEALS+CQ_DEALS if MONTH_START<=d["hs_lastmodifieddate"]<=MONTH_END],[m for m in LQ_MEETINGS+CQ_MEETINGS if MONTH_START<=m["date"]<=MONTH_END],[n for n in CQ_NOTES if MONTH_START<=n["date"]<=MONTH_END],[c for c in LQ_COMPANIES+CQ_COMPANIES if MONTH_START<=c["date"]<=MONTH_END],"91133237",MONTH_START,MONTH_END)
week  = build([d for d in LQ_DEALS+CQ_DEALS if WEEK_START<=d["hs_lastmodifieddate"]<=WEEK_END],[m for m in LQ_MEETINGS+CQ_MEETINGS if WEEK_START<=m["date"]<=WEEK_END],[n for n in CQ_NOTES if WEEK_START<=n["date"]<=WEEK_END],[c for c in LQ_COMPANIES+CQ_COMPANIES if WEEK_START<=c["date"]<=WEEK_END],"91133237",WEEK_START,WEEK_END)
year  = build(CQ_DEALS+LQ_DEALS,CQ_MEETINGS+LQ_MEETINGS,CQ_NOTES,CQ_COMPANIES+LQ_COMPANIES,"91133237",YEAR_START,today)

out = {"generated_at":datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),"generated_date":datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC"),"reps":[{"rep":{"id":"91133237","name":"Dan Owens"},"periods":{"week":week,"month":month,"quarter":cq,"last_quarter":lq,"year":year},"charts":{"month":{"labels":["w/c 8 Jun","w/c 15 Jun","w/c 22 Jun","w/c 29 Jun","w/c 6 Jul"],"deals":[52,38,0,55,65],"new_deals":[3,2,0,8,8],"meetings":[11,4,0,7,10]},"quarter":{"labels":["Apr 2026","May 2026","Jun 2026","Jul 2026"],"deals":[0,28,88,65],"new_deals":[0,12,18,8],"meetings":[0,8,22,10]},"year":{"labels":["Q1 2026","Q2 2026","Q3 2026"],"deals":[0,len(LQ_DEALS),len(CQ_DEALS)],"new_deals":[0,30,8],"meetings":[0,len(LQ_MEETINGS),len(CQ_MEETINGS)]},"quarter_vs_last":{"labels":["Deals","New deals","Qual. out","Meetings","LinkedIn","New cos","Tier 1 DAU","Peer SDK","Progressed"],"current":[cq["stats"]["deals_touched"],cq["stats"]["new_deals"],cq["stats"]["qualified_out"],cq["stats"]["meetings"],cq["stats"]["linkedin"],cq["stats"]["new_companies"],cq["stats"]["dau_tier1_added"],cq["stats"]["peer_sdk"],cq["stats"]["stage_progressed"]],"previous":[lq["stats"]["deals_touched"],lq["stats"]["new_deals"],lq["stats"]["qualified_out"],lq["stats"]["meetings"],lq["stats"]["linkedin"],lq["stats"]["new_companies"],lq["stats"]["dau_tier1_added"],lq["stats"]["peer_sdk"],lq["stats"]["stage_progressed"]]}}}]}

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"data","sales_data.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path,"w") as f: json.dump(out,f,indent=2)
for p in ["week","month","quarter","last_quarter"]:
    s = out["reps"][0]["periods"][p]["stats"]
    print(f"{p}: deals_touched={s['deals_touched']}, new={s['new_deals']}, progressed={s['stage_progressed']}, ooo={s['ooo_days']}")
print(f"\nWritten to {out_path}")
